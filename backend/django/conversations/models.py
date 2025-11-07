from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """
    대화(세션) 모델
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="사용자"
    )
    
    character = models.ForeignKey(
        "characters.Character",
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name="캐릭터"
    )
    
    classroom = models.ForeignKey(
        "organizations.Classroom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="conversations",
        verbose_name="학급"
    )
    
    title = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="대화 제목"
    )
    
    subject = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="대화 주제",
        help_text="대화의 주제나 목적"
    )
    
    policy_snapshot_ref = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="정책 스냅샷",
        help_text="대화 생성 시점의 School Mode 정책"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="활성 여부"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="수정일시"
    )
    
    class Meta:
        db_table = "conversations"
        verbose_name = "대화"
        verbose_name_plural = "대화"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["classroom", "created_at"]),
            models.Index(fields=["character", "created_at"]),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.character.name} ({self.created_at})"


class Message(models.Model):
    """
    메시지 모델
    """
    ROLE_CHOICES = [
        ("user", "사용자"),
        ("assistant", "어시스턴트"),
        ("system", "시스템"),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="대화"
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        verbose_name="역할"
    )
    
    content = models.TextField(
        verbose_name="메시지 내용"
    )
    
    # 토큰 사용량 추적
    token_usage = models.IntegerField(
        default=0,
        verbose_name="토큰 사용량"
    )
    
    # 안전성 및 필터링 정보
    safety_status = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="안전 상태",
        help_text="safe, flagged, blocked 등"
    )
    
    filtered = models.BooleanField(
        default=False,
        verbose_name="필터링 여부"
    )
    
    filter_reason = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="필터링 사유"
    )
    
    # AI 모델 정보
    model_version = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="모델 버전",
        help_text="사용된 AI 모델 버전 (예: gpt-4, gpt-3.5-turbo)"
    )
    
    prompt_hash = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="프롬프트 해시",
        help_text="프롬프트 무결성 검증용"
    )
    
    # 인용 및 출처
    citations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="인용/출처",
        help_text="응답에 사용된 참고 자료"
    )
    
    # 오류 및 재시도
    error_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="오류 코드"
    )
    
    retry_count = models.IntegerField(
        default=0,
        verbose_name="재시도 횟수"
    )
    
    # 메타데이터
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="메타데이터"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    class Meta:
        db_table = "messages"
        verbose_name = "메시지"
        verbose_name_plural = "메시지"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"]),
            models.Index(fields=["role", "created_at"]),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class ConversationReport(models.Model):
    """
    대화 리포트 모델
    - 요약, 퀴즈 등 자동 생성
    """
    conversation = models.OneToOneField(
        Conversation,
        on_delete=models.CASCADE,
        related_name="report",
        verbose_name="대화"
    )
    
    summary = models.TextField(
        blank=True,
        null=True,
        verbose_name="요약"
    )
    
    quiz_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="퀴즈 데이터"
    )
    
    pdf_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="PDF URL"
    )
    
    generated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="생성일시"
    )
    
    class Meta:
        db_table = "conversation_reports"
        verbose_name = "대화 리포트"
        verbose_name_plural = "대화 리포트"
    
    def __str__(self):
        return f"Report for {self.conversation}"
