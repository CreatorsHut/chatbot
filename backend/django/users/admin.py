from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """사용자 관리자"""

    # 리스트 표시할 필드
    list_display = ['email', 'username', 'first_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name']
    ordering = ['-created_at']

    # 사이트 제목
    site_header = '캐릭터챗 관리'
    site_title = '캐릭터챗'
    index_title = '관리자 페이지'

    # 기본 필드 세트
    fieldsets = (
        ('기본 정보', {'fields': ('email', 'username', 'first_name', 'password')}),
        ('권한', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('추가 정보', {'fields': ('phone', 'organization', 'credit')}),
        ('중요 날짜', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    # 새 사용자 추가 시 필드 세트
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'password1', 'password2', 'role'),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
