from django.contrib import admin
from django.utils.html import format_html
from .models import MediaAsset, GenerationJob


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    """저장된 이미지 파일 관리"""
    
    list_display = [
        "id",
        "file_name_preview",
        "asset_type_badge",
        "user",
        "file_size_display",
        "dimensions_display",
        "is_public",
        "created_at",
    ]
    
    list_filter = [
        "asset_type",
        "is_public",
        "created_at",
    ]
    
    search_fields = [
        "file_name",
        "user__username",
        "storage_path",
    ]
    
    readonly_fields = [
        "user",
        "storage_path",
        "sha256",
        "scanned_at",
        "created_at",
        "preview_image",
    ]
    
    fieldsets = (
        ("기본 정보", {
            "fields": ("user", "organization", "file_name", "storage_path", "asset_type")
        }),
        ("이미지 정보", {
            "fields": ("mime_type", "file_size", "width", "height")
        }),
        ("AI 생성 정보", {
            "fields": ("generation_prompt",),
            "description": "AI로 생성된 이미지인 경우 사용된 프롬프트",
            "classes": ("collapse",),
        }),
        ("미리보기", {
            "fields": ("preview_image",),
        }),
        ("보안", {
            "fields": ("sha256", "scanned_at", "is_public"),
            "classes": ("collapse",),
        }),
        ("메타데이터", {
            "fields": ("metadata", "created_at"),
            "classes": ("collapse",),
        }),
    )
    
    def file_name_preview(self, obj):
        """파일명 미리보기"""
        max_length = 30
        if len(obj.file_name) > max_length:
            return obj.file_name[:max_length] + "..."
        return obj.file_name
    
    file_name_preview.short_description = "파일명"
    
    def asset_type_badge(self, obj):
        """이미지 유형 배지"""
        colors = {
            "generated": "#007bff",  # AI 생성
            "uploaded": "#28a745",   # 사용자 업로드
            "avatar": "#6c757d",     # 프로필/아바타
        }
        color = colors.get(obj.asset_type, "#999999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_asset_type_display()
        )
    
    asset_type_badge.short_description = "파일 유형"
    
    def file_size_display(self, obj):
        """파일 크기 표시 (KB/MB)"""
        size = obj.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"
    
    file_size_display.short_description = "파일 크기"
    
    def dimensions_display(self, obj):
        """이미지 해상도 표시"""
        if obj.width and obj.height:
            return f"{obj.width} × {obj.height} px"
        return "-"
    
    dimensions_display.short_description = "해상도"
    
    def preview_image(self, obj):
        """이미지 미리보기"""
        # Supabase Storage URL로 미리보기 (실제로는 서명 URL 필요)
        return format_html(
            '<img src="{}" style="max-width: 400px; max-height: 300px; border: 1px solid #ddd; border-radius: 4px; padding: 5px;" />',
            obj.storage_path  # 실제로는 서명 URL로 변경 필요
        )
    
    preview_image.short_description = "미리보기"


@admin.register(GenerationJob)
class GenerationJobAdmin(admin.ModelAdmin):
    """생성 작업 기록 관리"""

    list_display = [
        "id",
        "job_type_badge",
        "status",
        "user_with_count",
        "this_attempt_display",
        "duration_display",
        "created_at_display",
    ]

    list_filter = [
        "job_type",
        "status",
        "created_at",
    ]

    search_fields = [
        "user__username",
        "celery_task_id",
    ]

    # 상태 변경 가능하도록 수정
    readonly_fields = [
        "user",
        "celery_task_id",
        "created_at",
        "duration_display",
    ]

    # 리스트 페이지에서 상태 직접 편집 가능
    list_editable = [
        "status",
    ]

    # 상태 변경 액션 추가
    actions = [
        "mark_as_processing",
        "mark_as_completed",
        "mark_as_failed",
        "retry_failed",
    ]
    
    fieldsets = (
        ("📋 기본 정보", {
            "fields": ("user", "job_type", "status", "celery_task_id")
        }),
        ("📝 요청 내용", {
            "fields": ("input_data",),
            "description": "사용자가 요청한 이미지 생성 정보 (프롬프트, 크기, 품질 등)"
        }),
        ("✅ 생성 결과", {
            "fields": ("result_data", "result_media"),
            "description": "생성된 이미지 URL 및 개선된 프롬프트"
        }),
        ("⚠️ 오류 및 재시도", {
            "fields": ("error_message", "attempts"),
            "classes": ("collapse",),
            "description": "실패 시 오류 메시지 및 재시도 횟수"
        }),
        ("⏱️ 작업 시간", {
            "fields": ("created_at", "started_at", "completed_at", "duration_display"),
            "description": "작업 생성부터 완료까지의 타임라인",
            "classes": ("wide",),
        }),
    )
    
    def job_type_badge(self, obj):
        """작업 유형 배지"""
        colors = {
            "image": "#007bff",      # 이미지 생성
            "variation": "#6c757d",  # 이미지 변형
        }
        color = colors.get(obj.job_type, "#999999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_job_type_display()
        )
    
    job_type_badge.short_description = "작업 종류"
    
    def status_badge(self, obj):
        """상태 배지"""
        colors = {
            "pending": "#ffc107",
            "processing": "#007bff",
            "completed": "#28a745",
            "failed": "#dc3545",
        }
        color = colors.get(obj.status, "#999999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )
    
    status_badge.short_description = "상태"
    
    def user_with_count(self, obj):
        """사용자 정보와 총 생성 횟수"""
        # 해당 사용자의 총 이미지 생성 횟수 계산
        total_count = GenerationJob.objects.filter(
            user=obj.user,
            job_type="image"
        ).count()
        
        # 완료된 작업 수
        completed_count = GenerationJob.objects.filter(
            user=obj.user,
            job_type="image",
            status="completed"
        ).count()
        
        return format_html(
            '{}<br><span style="color: #6c757d; font-size: 11px;">총 {}회 요청 / {}회 성공</span>',
            obj.user,
            total_count,
            completed_count
        )
    
    user_with_count.short_description = "요청 사용자"
    
    def this_attempt_display(self, obj):
        """이 작업의 재시도 횟수"""
        if obj.attempts > 3:
            color = "#dc3545"  # 빨강
        elif obj.attempts > 1:
            color = "#ffc107"  # 노랑
        else:
            color = "#28a745"  # 초록
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} 회</span>',
            color,
            obj.attempts
        )
    
    this_attempt_display.short_description = "재시도"
    
    def duration_display(self, obj):
        """작업 소요 시간"""
        if obj.started_at and obj.completed_at:
            duration = (obj.completed_at - obj.started_at).total_seconds()
            if duration < 1:
                return f"{duration * 1000:.0f}ms"
            elif duration < 60:
                return f"{duration:.1f}초"
            else:
                minutes = int(duration / 60)
                seconds = duration % 60
                return f"{minutes}분 {seconds:.0f}초"
        elif obj.started_at and obj.status == "processing":
            # 진행 중인 작업의 경과 시간
            from django.utils import timezone
            duration = (timezone.now() - obj.started_at).total_seconds()
            duration_str = f"{duration:.1f}초 (진행중)"
            return format_html(
                '<span style="color: #007bff;">{}</span>',
                duration_str
            )
        return "-"

    duration_display.short_description = "소요 시간"
    
    def created_at_display(self, obj):
        """생성일시 표시"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        # 한국 시간으로 변환
        local_time = timezone.localtime(obj.created_at)
        time_diff = timesince(obj.created_at)
        
        return format_html(
            '<span title="{}">{} 전</span>',
            local_time.strftime("%Y-%m-%d %H:%M:%S"),
            time_diff.split(',')[0]  # 첫 번째 단위만 표시
        )
    
    created_at_display.short_description = "생성일시"

    # ========== 상태 변경 액션 ==========

    def mark_as_processing(self, request, queryset):
        """선택된 작업을 '처리중'으로 변경"""
        from django.utils import timezone

        updated_count = 0
        for job in queryset:
            if job.status in ["pending", "failed"]:  # pending 또는 failed 상태만 변경 가능
                job.status = "processing"
                if not job.started_at:
                    job.started_at = timezone.now()
                job.save()
                updated_count += 1

        self.message_user(
            request,
            f"{updated_count}개 작업을 '처리중'으로 변경했습니다.",
            level="success"
        )

    mark_as_processing.short_description = "✅ 처리중으로 변경"

    def mark_as_completed(self, request, queryset):
        """선택된 작업을 '완료'로 변경"""
        from django.utils import timezone

        updated_count = 0
        for job in queryset:
            if job.status != "completed":
                job.status = "completed"
                if not job.started_at:
                    job.started_at = timezone.now()
                if not job.completed_at:
                    job.completed_at = timezone.now()
                job.save()
                updated_count += 1

        self.message_user(
            request,
            f"{updated_count}개 작업을 '완료'로 변경했습니다.",
            level="success"
        )

    mark_as_completed.short_description = "✅ 완료로 변경"

    def mark_as_failed(self, request, queryset):
        """선택된 작업을 '실패'로 변경"""
        from django.utils import timezone

        updated_count = 0
        for job in queryset:
            if job.status != "failed":
                job.status = "failed"
                if not job.started_at:
                    job.started_at = timezone.now()
                if not job.completed_at:
                    job.completed_at = timezone.now()
                job.save()
                updated_count += 1

        self.message_user(
            request,
            f"{updated_count}개 작업을 '실패'로 변경했습니다.",
            level="warning"
        )

    mark_as_failed.short_description = "❌ 실패로 변경"

    def retry_failed(self, request, queryset):
        """실패한 작업을 '대기중'으로 되돌려 재시도 가능하게"""
        updated_count = 0
        for job in queryset:
            if job.status == "failed":
                job.status = "pending"
                job.attempts += 1
                job.error_message = ""  # 기존 오류 메시지 제거
                job.started_at = None
                job.completed_at = None
                job.save()
                updated_count += 1

        self.message_user(
            request,
            f"{updated_count}개 작업을 재시도를 위해 '대기중'으로 변경했습니다.",
            level="info"
        )

    retry_failed.short_description = "🔄 재시도 (대기중으로 변경)"
