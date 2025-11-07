from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone

from .models import Conversation, Message, ConversationReport
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    ConversationReportSerializer,
)


class IsOwnerOrAdmin(permissions.BasePermission):
    """대화 소유자 또는 관리자만 접근 가능"""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # 조회는 소유자 또는 관리자/교사
            return obj.user == request.user or request.user.role in ["admin", "teacher"]
        # 수정/삭제는 소유자만
        return obj.user == request.user


class ConversationViewSet(viewsets.ModelViewSet):
    """
    대화 CRUD API
    - 조회: 본인 대화만 조회
    - 생성: 인증된 사용자 누구나
    - 수정/삭제: 본인 대화만
    """
    
    queryset = Conversation.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action == "list":
            return ConversationListSerializer
        elif self.action == "create":
            return ConversationCreateSerializer
        return ConversationDetailSerializer
    
    def get_queryset(self):
        """사용자 역할에 따른 필터링"""
        user = self.request.user
        
        if user.role == "admin":
            # 관리자는 모든 대화 조회 가능
            return Conversation.objects.all().order_by("-updated_at")
        elif user.role == "teacher":
            # 교사는 자신의 학급 대화 조회 가능
            return Conversation.objects.filter(
                Q(user=user) | Q(classroom__teacher=user)
            ).order_by("-updated_at")
        else:
            # 학생은 본인 대화만
            return Conversation.objects.filter(user=user).order_by("-updated_at")
    
    def perform_create(self, serializer):
        """대화 생성 시 사용자 자동 설정"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["get"])
    def my_conversations(self, request):
        """현재 사용자의 모든 대화 조회"""
        conversations = Conversation.objects.filter(
            user=request.user
        ).order_by("-updated_at")
        serializer = ConversationListSerializer(conversations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        """특정 대화의 메시지 목록 조회"""
        conversation = self.get_object()
        messages = conversation.messages.all().order_by("created_at")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None):
        """대화에 메시지 추가"""
        conversation = self.get_object()
        
        # 권한 확인
        if conversation.user != request.user:
            raise PermissionDenied("이 대화에 메시지를 추가할 권한이 없습니다.")
        
        serializer = MessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(conversation=conversation)
            
            # 대화 updated_at 갱신
            conversation.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        """대화 활성화/비활성화 토글"""
        conversation = self.get_object()
        conversation.is_active = not conversation.is_active
        conversation.save()
        
        return Response({
            "message": "대화 상태가 변경되었습니다.",
            "is_active": conversation.is_active
        })
    
    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        """대화 리포트 조회"""
        conversation = self.get_object()
        
        try:
            report = conversation.report
            serializer = ConversationReportSerializer(report)
            return Response(serializer.data)
        except ConversationReport.DoesNotExist:
            return Response(
                {"detail": "리포트가 아직 생성되지 않았습니다."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=["post"])
    def generate_report(self, request, pk=None):
        """대화 리포트 생성 요청"""
        conversation = self.get_object()
        
        # 이미 리포트가 있는지 확인
        if hasattr(conversation, "report"):
            return Response(
                {"detail": "리포트가 이미 존재합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Celery 작업으로 리포트 생성
        # 현재는 간단하게 생성
        report = ConversationReport.objects.create(
            conversation=conversation,
            summary="리포트 생성 중...",
        )
        
        serializer = ConversationReportSerializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    메시지 조회 API (읽기 전용)
    - 메시지는 대화를 통해서만 생성됨
    """
    
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """사용자 역할에 따른 필터링"""
        user = self.request.user
        
        if user.role == "admin":
            return Message.objects.all().order_by("-created_at")
        elif user.role == "teacher":
            return Message.objects.filter(
                Q(conversation__user=user) | Q(conversation__classroom__teacher=user)
            ).order_by("-created_at")
        else:
            return Message.objects.filter(
                conversation__user=user
            ).order_by("-created_at")
