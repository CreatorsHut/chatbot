from django.db import models
from django.conf import settings


class Organization(models.Model):
    """
    조직/학교 모델
    """
    TYPE_CHOICES = [
        ("school", "학교"),
        ("academy", "학원"),
        ("company", "기업"),
        ("other", "기타"),
    ]
    
    name = models.CharField(
        max_length=200,
        verbose_name="조직명"
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="school",
        verbose_name="조직 유형"
    )
    
    region = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="지역"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="설명"
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
        db_table = "organizations"
        verbose_name = "조직"
        verbose_name_plural = "조직"
        indexes = [
            models.Index(fields=["type", "region"]),
        ]
    
    def __str__(self):
        return self.name


class Classroom(models.Model):
    """
    학급/반 모델
    """
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="classrooms",
        verbose_name="소속 조직"
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name="반 이름"
    )
    
    grade = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="학년"
    )
    
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_classrooms",
        verbose_name="담당 교사"
    )
    
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_classrooms",
        blank=True,
        verbose_name="학생들"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="설명"
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
        db_table = "classrooms"
        verbose_name = "학급"
        verbose_name_plural = "학급"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "is_active"]),
            models.Index(fields=["teacher", "is_active"]),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.name}"
