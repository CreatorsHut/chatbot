from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    커스텀 유저 모델
    - 역할: admin(관리자), teacher(교사), student(학생)
    """
    ROLE_CHOICES = [
        ("admin", "관리자"),
        ("teacher", "교사"),
        ("student", "학생"),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="student",
        verbose_name="역할"
    )
    
    # 추가 필드
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="전화번호"
    )
    
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="소속 조직"
    )
    
    credit = models.IntegerField(
        default=0,
        verbose_name="크레딧"
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
        db_table = "users"
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
