from django.contrib import admin
from django.utils.html import format_html
from .models import Character


class CharacterAdmin(admin.ModelAdmin):
    """캐릭터 관리 페이지"""

    # 목록 표시
    list_display = [
        "name",
        "owner",
        "category_display",
        "subject_display",
        "status_badge",
        "visibility",
        "usage_count",
        "created_at",
    ]

    list_filter = [
        "status",
        "visibility",
        "category",
        "subject",
        "created_at",
        "owner__role",
    ]

    search_fields = ["name", "owner__username", "short_description"]

    ordering = ["-created_at"]

    # 상세 페이지 필드 그룹화
    fieldsets = (
        ("기본 정보", {
            "fields": ("name", "short_description", "category", "subject", "owner", "organization")
        }),
        ("🎨 성격 설정", {
            "fields": ("personality_traits", "greeting_message"),
            "classes": ("collapse",),
        }),
        ("📖 배경 및 세계관", {
            "fields": ("background_story", "world_setting", "teaching_style"),
            "classes": ("collapse",),
        }),
        ("💬 대화 예시", {
            "fields": ("example_conversations",),
            "description": "캐릭터 말투를 학습할 수 있는 예시 대화 (JSON 형식)",
            "classes": ("collapse",),
        }),
        ("🎭 연출 스타일", {
            "fields": ("narration_style", "narration_template"),
            "classes": ("collapse",),
        }),
        ("🤖 AI 프롬프트", {
            "fields": ("system_prompt",),
            "description": "AI 모델에 전달될 최종 프롬프트",
        }),
        ("⚙️ 제어 설정", {
            "fields": ("creativity", "context_length", "moderation_level"),
            "classes": ("collapse",),
        }),
        ("이미지 및 메타데이터", {
            "fields": ("avatar_url", "version", "tags"),
            "classes": ("collapse",),
        }),
        ("상태 관리", {
            "fields": ("status", "visibility", "approved_by", "approved_at", "rejection_reason"),
        }),
    )

    readonly_fields = [
        "owner",
        "status",
        "approved_by",
        "approved_at",
        "usage_count",
        "created_at",
        "updated_at",
    ]

    def status_badge(self, obj):
        """상태 배지 표시"""
        status_colors = {
            "draft": "#FFA500",
            "pending": "#1E90FF",
            "approved": "#228B22",
            "rejected": "#DC143C",
        }
        color = status_colors.get(obj.status, "#999999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "상태"

    def category_display(self, obj):
        """카테고리 표시"""
        return obj.get_category_display()

    category_display.short_description = "카테고리"

    def subject_display(self, obj):
        """과목 표시"""
        return obj.get_subject_display()

    subject_display.short_description = "과목"

    def save_model(self, request, obj, form, change):
        """저장 시 owner 설정, 상태 자동 변경, 프롬프트 자동 생성"""
        # 새 캐릭터 생성 시 owner를 현재 로그인한 사용자로 설정
        if not change:  # 새로 생성하는 경우
            obj.owner = request.user
        
        # 공개 범위가 '공개'로 설정되면 상태를 '승인됨'으로 자동 변경
        if obj.visibility == 'public' and obj.status == 'draft':
            obj.status = 'approved'
        
        # 시스템 프롬프트가 비어있거나, 다른 필드만 수정된 경우 자동 생성
        if not obj.system_prompt or (form.changed_data and "system_prompt" not in form.changed_data):
            obj.system_prompt = obj.build_system_prompt()
        
        super().save_model(request, obj, form, change)


admin.site.register(Character, CharacterAdmin)
