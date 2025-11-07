from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django_filters import rest_framework as filters
from django.utils import timezone
from django.db import models

from .models import Character
from .serializers import (
    CharacterListSerializer,
    CharacterDetailSerializer,
    CharacterCreateUpdateSerializer,
    CharacterApprovalSerializer,
    CharacterPromptPreviewSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """캐릭터 소유자 또는 관리자만 수정/삭제 가능"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.role == "admin"


class IsAdmin(permissions.BasePermission):
    """관리자 전용"""

    def has_permission(self, request, view):
        return request.user.role == "admin"


class CharacterFilter(filters.FilterSet):
    """캐릭터 필터링"""

    subject = filters.CharFilter(field_name="subject")
    visibility = filters.CharFilter(field_name="visibility")
    status = filters.CharFilter(field_name="status")
    category = filters.CharFilter(field_name="category")
    owner = filters.CharFilter(field_name="owner__username")

    class Meta:
        model = Character
        fields = ["subject", "visibility", "status", "category", "owner"]


class CharacterViewSet(viewsets.ModelViewSet):
    """
    캐릭터 CRUD API
    - 조회: 모든 인증된 사용자 가능 (공개/승인된 캐릭터)
    - 생성: 관리자/교사/학생 (상태: draft)
    - 수정: 소유자 또는 관리자
    - 삭제: 소유자 또는 관리자
    - 승인/반려: 관리자만
    """

    queryset = Character.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CharacterFilter

    def get_permissions(self):
        """액션별 권한 설정"""
        if self.action in ['list', 'retrieve', 'public_characters']:
            # 목록 조회, 상세 조회, 공개 캐릭터는 인증 없이 가능
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action == "list":
            return CharacterListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return CharacterCreateUpdateSerializer
        elif self.action in ["approve", "reject"]:
            return CharacterApprovalSerializer
        elif self.action == "preview_prompt":
            return CharacterPromptPreviewSerializer
        return CharacterDetailSerializer

    def get_queryset(self):
        """사용자 역할에 따른 쿼리셋 필터링"""
        user = self.request.user
        qs = Character.objects.all()

        if self.action == "list":
            # 인증되지 않은 사용자: 공개된 승인 캐릭터만
            if not user.is_authenticated:
                qs = qs.filter(visibility="public", status="approved")
            # 일반 사용자: 공개 캐릭터 또는 자신의 캐릭터
            elif user.role != "admin":
                qs = qs.filter(
                    models.Q(visibility="public", status="approved")
                    | models.Q(owner=user)
                )
            # 관리자: 모든 캐릭터
            return qs.order_by("-created_at")

        return qs

    def create(self, request, *args, **kwargs):
        """캐릭터 생성 (요청 데이터 로깅 추가)"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[Character Create Request] User: {request.user}")
        logger.info(f"[Character Create Request] Data keys: {list(request.data.keys())}")
        logger.info(f"[Character Create Request] avatar_url: {request.data.get('avatar_url')} (type: {type(request.data.get('avatar_url'))})")
        
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """캐릭터 생성 시 소유자 자동 설정"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[Character Create] User: {self.request.user}")
        logger.info(f"[Character Create] Validated Data: {serializer.validated_data}")
        
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        """캐릭터 삭제 권한 확인"""
        if instance.owner != self.request.user and self.request.user.role != "admin":
            raise PermissionDenied("이 캐릭터를 삭제할 권한이 없습니다.")
        instance.delete()

    @action(detail=False, methods=["get"])
    def my_characters(self, request):
        """현재 사용자의 모든 캐릭터 조회"""
        characters = Character.objects.filter(owner=request.user).order_by("-created_at")
        serializer = CharacterListSerializer(characters, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        """캐릭터 승인 (관리자만)"""
        character = self.get_object()
        if character.status != "pending":
            return Response(
                {"error": "대기 중인 캐릭터만 승인할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        character.status = "approved"
        character.approved_by = request.user
        character.approved_at = timezone.now()
        character.save()

        serializer = self.get_serializer(character)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        """캐릭터 반려 (관리자만)"""
        character = self.get_object()
        if character.status != "pending":
            return Response(
                {"error": "대기 중인 캐릭터만 반려할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CharacterApprovalSerializer(
            character, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def preview_prompt(self, request):
        """프롬프트 미리보기 (자동 생성)"""
        serializer = CharacterPromptPreviewSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["get"])
    def prompt(self, request, pk=None):
        """최종 시스템 프롬프트 조회"""
        character = self.get_object()
        return Response({
            "id": character.id,
            "name": character.name,
            "system_prompt": character.system_prompt,
            "example_conversations": character.example_conversations,
        })

    @action(detail=True, methods=["post"])
    def submit_for_approval(self, request, pk=None):
        """임시저장 상태의 캐릭터를 승인대기로 변경"""
        character = self.get_object()

        # 소유자 확인
        if character.owner != request.user and request.user.role != "admin":
            raise PermissionDenied("이 캐릭터를 제출할 권한이 없습니다.")

        # 현재 상태 확인
        if character.status != "draft":
            return Response(
                {"error": f"임시저장 상태의 캐릭터만 제출할 수 있습니다. (현재: {character.status})"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        character.status = "pending"
        character.save()

        serializer = CharacterDetailSerializer(character)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def increment_usage(self, request, pk=None):
        """캐릭터 사용 횟수 증가 (대화 시작 시 호출)"""
        character = self.get_object()
        character.usage_count += 1
        character.save()

        return Response(
            {"message": "사용 횟수가 증가했습니다.", "usage_count": character.usage_count}
        )

    @action(detail=False, methods=["get"])
    def pending_approvals(self, request):
        """승인 대기 중인 캐릭터 조회 (관리자만)"""
        if request.user.role != "admin":
            raise PermissionDenied("관리자만 조회할 수 있습니다.")

        pending_characters = Character.objects.filter(status="pending")
        serializer = CharacterListSerializer(pending_characters, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def public_characters(self, request):
        """공개 승인 캐릭터 조회 (온보딩/선택 화면용) - 누구나 접근 가능"""
        public_characters = Character.objects.filter(
            visibility="public", status="approved"
        ).order_by("-usage_count", "-created_at")

        # 과목별로 그룹핑
        characters_by_subject = {}
        for char in public_characters:
            subject = char.get_subject_display()
            if subject not in characters_by_subject:
                characters_by_subject[subject] = []
            characters_by_subject[subject].append(CharacterListSerializer(char).data)

        return Response(characters_by_subject)
