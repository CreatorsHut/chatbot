from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from .models import MediaAsset, GenerationJob


class MediaAssetSerializer(serializers.ModelSerializer):
    """미디어 자산 Serializer"""
    user_name = serializers.CharField(source="user.username", read_only=True)
    
    class Meta:
        model = MediaAsset
        fields = [
            "id",
            "user",
            "user_name",
            "organization",
            "storage_path",
            "file_name",
            "mime_type",
            "file_size",
            "asset_type",
            "width",
            "height",
            "duration",
            "metadata",
            "sha256",
            "is_public",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "storage_path",
            "sha256",
            "created_at",
        ]


class GenerationJobSerializer(serializers.ModelSerializer):
    """생성 작업 Serializer"""
    user_name = serializers.CharField(source="user.username", read_only=True)
    job_type_display = serializers.CharField(source="get_job_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    
    class Meta:
        model = GenerationJob
        fields = [
            "id",
            "user",
            "user_name",
            "job_type",
            "job_type_display",
            "status",
            "status_display",
            "input_data",
            "result_data",
            "result_media",
            "error_message",
            "celery_task_id",
            "attempts",
            "created_at",
            "started_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


class GenerationJobCreateSerializer(serializers.ModelSerializer):
    """생성 작업 생성용 Serializer"""

    class Meta:
        model = GenerationJob
        fields = [
            "id",
            "job_type",
            "input_data",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
        ]


class MediaAssetViewSet(viewsets.ModelViewSet):
    """미디어 자산 API"""
    
    queryset = MediaAsset.objects.all()
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """사용자 역할에 따른 필터링"""
        user = self.request.user
        
        if user.role == "admin":
            return MediaAsset.objects.all().order_by("-created_at")
        elif user.role == "teacher":
            return MediaAsset.objects.filter(
                Q(user=user) | Q(organization=user.organization)
            ).order_by("-created_at")
        else:
            return MediaAsset.objects.filter(user=user).order_by("-created_at")
    
    def perform_create(self, serializer):
        """미디어 생성 시 사용자 자동 설정"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=["get"])
    def my_media(self, request):
        """현재 사용자의 미디어 조회"""
        media = MediaAsset.objects.filter(user=request.user).order_by("-created_at")
        serializer = self.get_serializer(media, many=True)
        return Response(serializer.data)


class GenerationJobViewSet(viewsets.ModelViewSet):
    """생성 작업 API"""
    
    queryset = GenerationJob.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """액션별 Serializer 선택"""
        if self.action == "create":
            return GenerationJobCreateSerializer
        return GenerationJobSerializer
    
    def get_queryset(self):
        """사용자 역할에 따른 필터링"""
        user = self.request.user
        
        if user.role == "admin":
            return GenerationJob.objects.all().order_by("-created_at")
        else:
            return GenerationJob.objects.filter(user=user).order_by("-created_at")
    
    def perform_create(self, serializer):
        """작업 생성 시 사용자 자동 설정"""
        job = serializer.save(
            user=self.request.user,
            status="pending",  # 초기 상태
            attempts=1
        )
        
        # FastAPI에서 작업을 처리함
        return job
    
    def perform_update(self, serializer):
        """작업 업데이트 시 타임스탬프 자동 설정"""
        from django.utils import timezone
        import logging
        
        logger = logging.getLogger(__name__)
        
        status = serializer.validated_data.get("status")
        instance = serializer.instance
        update_fields = {}
        
        logger.info(f"[GenerationJob] Updating job {instance.id}: {instance.status} -> {status}")
        
        # processing으로 변경될 때 started_at 설정
        if status == "processing" and not instance.started_at:
            update_fields["started_at"] = timezone.now()
            logger.info(f"[GenerationJob] Setting started_at for job {instance.id}")
        
        # completed 또는 failed로 변경될 때 completed_at 설정
        elif status in ["completed", "failed"] and not instance.completed_at:
            update_fields["completed_at"] = timezone.now()
            logger.info(f"[GenerationJob] Setting completed_at for job {instance.id}")
        
        serializer.save(**update_fields)
        logger.info(f"[GenerationJob] Job {instance.id} updated successfully")
    
    @action(detail=False, methods=["get"])
    def my_jobs(self, request):
        """현재 사용자의 작업 조회"""
        jobs = GenerationJob.objects.filter(user=request.user).order_by("-created_at")
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """작업 재시도"""
        job = self.get_object()
        
        if job.user != request.user and request.user.role != "admin":
            raise PermissionDenied("이 작업을 재시도할 권한이 없습니다.")
        
        if job.status not in ["failed", "completed"]:
            return Response(
                {"detail": "실패하거나 완료된 작업만 재시도할 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 재시도 로직
        job.status = "pending"
        job.attempts += 1
        job.error_message = None
        job.save()
        
        # TODO: FastAPI 호출 또는 Celery 작업 재트리거
        
        serializer = self.get_serializer(job)
        return Response(serializer.data)
