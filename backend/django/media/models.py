from django.db import models
from django.conf import settings


class MediaAsset(models.Model):
    """
    이미지 자산 모델
    - AI 생성 이미지 및 업로드 이미지 관리
    - Supabase Storage에 저장된 이미지 정보
    """
    TYPE_CHOICES = [
        ("generated", "AI 생성"),
        ("uploaded", "사용자 업로드"),
        ("avatar", "프로필/아바타"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="media_assets",
        verbose_name="업로드 사용자"
    )
    
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="media_assets",
        null=True,
        blank=True,
        verbose_name="소속 조직"
    )
    
    storage_path = models.CharField(
        max_length=500,
        unique=True,
        verbose_name="저장 경로"
    )
    
    file_name = models.CharField(
        max_length=255,
        verbose_name="파일명"
    )
    
    mime_type = models.CharField(
        max_length=100,
        verbose_name="MIME 타입"
    )
    
    file_size = models.BigIntegerField(
        verbose_name="파일 크기 (bytes)"
    )
    
    asset_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="uploaded",
        verbose_name="이미지 유형"
    )
    
    # 이미지 메타데이터
    width = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="가로 크기 (px)"
    )
    
    height = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="세로 크기 (px)"
    )
    
    # AI 생성 정보 (generated 타입인 경우)
    generation_prompt = models.TextField(
        blank=True,
        null=True,
        verbose_name="생성 프롬프트",
        help_text="AI 이미지 생성에 사용된 프롬프트"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="추가 메타데이터"
    )
    
    # 보안 및 무결성
    sha256 = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="SHA256 해시",
        help_text="파일 무결성 검증용"
    )
    
    scanned_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="바이러스 스캔 일시"
    )
    
    # 접근 제어
    is_public = models.BooleanField(
        default=False,
        verbose_name="공개 여부"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    class Meta:
        db_table = "media_assets"
        verbose_name = "저장된 이미지 파일"
        verbose_name_plural = "저장된 이미지 파일"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.file_name} ({self.user.username})"


class GenerationJob(models.Model):
    """
    AI 이미지 생성 작업 모델
    - DALL-E 이미지 생성 작업 추적
    """
    STATUS_CHOICES = [
        ("pending", "대기중"),
        ("processing", "처리중"),
        ("completed", "완료"),
        ("failed", "실패"),
    ]
    
    TYPE_CHOICES = [
        ("image", "이미지 생성"),
        ("variation", "이미지 변형"),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="generation_jobs",
        verbose_name="요청 사용자"
    )
    
    job_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name="작업 유형"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="상태"
    )
    
    # 작업 입력
    input_data = models.JSONField(
        default=dict,
        verbose_name="입력 데이터"
    )
    
    # 작업 결과
    result_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="결과 데이터"
    )
    
    result_media = models.ForeignKey(
        MediaAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generation_jobs",
        verbose_name="결과 미디어"
    )
    
    # 오류 정보
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="오류 메시지"
    )
    
    # Celery 작업 ID
    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Celery Task ID"
    )
    
    # 재시도 정보
    attempts = models.IntegerField(
        default=0,
        verbose_name="재시도 횟수",
        help_text="이 작업의 재시도 횟수 (실패 후 재시도한 경우)"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="시작일시"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="완료일시"
    )

    class Meta:
        db_table = "generation_jobs"
        verbose_name = "생성 작업 기록"
        verbose_name_plural = "생성 작업 기록"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_job_type_display()} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        """상태 변경 시 자동으로 started_at, completed_at 업데이트"""
        from django.utils import timezone

        # 상태가 processing으로 변경될 때 started_at 자동 설정
        if self.status == "processing" and not self.started_at:
            self.started_at = timezone.now()

        # 상태가 completed/failed로 변경될 때 completed_at 자동 설정
        if self.status in ["completed", "failed"] and not self.completed_at:
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)
