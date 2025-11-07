from django.contrib import admin
from django.utils.html import format_html
from .models import Conversation, Message, ConversationReport


class MessageInline(admin.TabularInline):
    """대화 안에서 메시지 인라인 표시"""
    model = Message
    extra = 0
    fields = ["role", "content_preview", "token_usage", "safety_status", "created_at"]
    readonly_fields = ["content_preview", "token_usage", "safety_status", "created_at"]
    can_delete = False

    def content_preview(self, obj):
        """메시지 내용 미리보기 (50자)"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = "내용 미리보기"


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """대화 관리 페이지"""
    
    list_display = [
        "id",
        "user",
        "character_link",
        "title_preview",
        "message_count",
        "is_active",
        "created_at",
        "updated_at",
    ]
    
    list_filter = [
        "is_active",
        "created_at",
        "updated_at",
        "character",
    ]
    
    search_fields = [
        "user__username",
        "character__name",
        "title",
        "subject",
    ]
    
    readonly_fields = [
        "user",
        "character",
        "created_at",
        "updated_at",
        "message_count",
    ]
    
    inlines = [MessageInline]
    
    fieldsets = (
        ("기본 정보", {
            "fields": ("user", "character", "classroom", "title", "subject")
        }),
        ("상태", {
            "fields": ("is_active", "message_count")
        }),
        ("정책", {
            "fields": ("policy_snapshot_ref",),
            "classes": ("collapse",),
        }),
        ("메타데이터", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    def character_link(self, obj):
        """캐릭터 링크"""
        return format_html(
            '<a href="/admin/characters/character/{}/change/">{}</a>',
            obj.character.id,
            obj.character.name
        )
    
    character_link.short_description = "캐릭터"
    
    def title_preview(self, obj):
        """제목 미리보기"""
        if obj.title:
            return obj.title[:30] + "..." if len(obj.title) > 30 else obj.title
        return "(제목 없음)"
    
    title_preview.short_description = "대화 제목"
    
    def message_count(self, obj):
        """메시지 개수"""
        count = obj.messages.count()
        return format_html(
            '<span style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 3px;">{} 개</span>',
            count
        )
    
    message_count.short_description = "메시지 수"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """메시지 관리 페이지"""
    
    list_display = [
        "id",
        "conversation_link",
        "role_badge",
        "content_preview",
        "token_usage",
        "safety_badge",
        "created_at",
    ]
    
    list_filter = [
        "role",
        "safety_status",
        "filtered",
        "created_at",
    ]
    
    search_fields = [
        "conversation__user__username",
        "conversation__character__name",
        "content",
    ]
    
    readonly_fields = [
        "conversation",
        "role",
        "content",
        "token_usage",
        "safety_status",
        "filtered",
        "filter_reason",
        "model_version",
        "prompt_hash",
        "citations",
        "error_code",
        "retry_count",
        "metadata",
        "created_at",
    ]
    
    fieldsets = (
        ("기본 정보", {
            "fields": ("conversation", "role", "content")
        }),
        ("토큰 사용", {
            "fields": ("token_usage", "model_version")
        }),
        ("안전 검사", {
            "fields": ("safety_status", "filtered", "filter_reason"),
        }),
        ("메타데이터", {
            "fields": ("citations", "prompt_hash", "metadata"),
            "classes": ("collapse",),
        }),
        ("오류 정보", {
            "fields": ("error_code", "retry_count"),
            "classes": ("collapse",),
        }),
        ("생성일시", {
            "fields": ("created_at",),
        }),
    )
    
    def conversation_link(self, obj):
        """대화 링크"""
        return format_html(
            '<a href="/admin/conversations/conversation/{}/change/">대화 #{}</a>',
            obj.conversation.id,
            obj.conversation.id
        )
    
    conversation_link.short_description = "대화"
    
    def role_badge(self, obj):
        """역할 배지"""
        colors = {
            "user": "#28a745",
            "assistant": "#007bff",
            "system": "#6c757d",
        }
        color = colors.get(obj.role, "#999999")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_role_display()
        )
    
    role_badge.short_description = "역할"
    
    def content_preview(self, obj):
        """내용 미리보기"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    
    content_preview.short_description = "내용"
    
    def safety_badge(self, obj):
        """안전 상태 배지"""
        if obj.filtered:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 10px; border-radius: 3px;">차단됨</span>'
            )
        elif obj.safety_status == "safe":
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 10px; border-radius: 3px;">안전</span>'
            )
        return format_html(
            '<span style="background-color: #ffc107; color: black; padding: 3px 10px; border-radius: 3px;">{}</span>',
            obj.safety_status or "미검사"
        )
    
    safety_badge.short_description = "안전 상태"


@admin.register(ConversationReport)
class ConversationReportAdmin(admin.ModelAdmin):
    """대화 리포트 관리 페이지"""
    
    list_display = [
        "id",
        "conversation_link",
        "has_summary",
        "has_quiz",
        "has_pdf",
        "generated_at",
    ]
    
    list_filter = [
        "generated_at",
    ]
    
    search_fields = [
        "conversation__user__username",
        "conversation__character__name",
        "summary",
    ]
    
    readonly_fields = [
        "conversation",
        "generated_at",
    ]
    
    fieldsets = (
        ("기본 정보", {
            "fields": ("conversation",)
        }),
        ("요약", {
            "fields": ("summary",)
        }),
        ("퀴즈", {
            "fields": ("quiz_data",),
            "classes": ("collapse",),
        }),
        ("PDF", {
            "fields": ("pdf_url",)
        }),
        ("생성일시", {
            "fields": ("generated_at",)
        }),
    )
    
    def conversation_link(self, obj):
        """대화 링크"""
        return format_html(
            '<a href="/admin/conversations/conversation/{}/change/">대화 #{}</a>',
            obj.conversation.id,
            obj.conversation.id
        )
    
    conversation_link.short_description = "대화"
    
    def has_summary(self, obj):
        """요약 존재 여부"""
        return "✅" if obj.summary else "❌"
    
    has_summary.short_description = "요약"
    
    def has_quiz(self, obj):
        """퀴즈 존재 여부"""
        return "✅" if obj.quiz_data else "❌"
    
    has_quiz.short_description = "퀴즈"
    
    def has_pdf(self, obj):
        """PDF 존재 여부"""
        return "✅" if obj.pdf_url else "❌"
    
    has_pdf.short_description = "PDF"
