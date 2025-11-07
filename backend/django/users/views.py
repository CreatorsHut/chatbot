from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import (
    UserRegisterSerializer,
    UserLoginSerializer,
    UserSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    TokenSerializer,
)


class AuthViewSet(viewsets.ViewSet):
    """
    인증 관련 엔드포인트
    - register: 회원가입
    - login: 로그인
    - logout: 로그아웃
    - refresh: 토큰 갱신
    """
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        회원가입
        POST /api/v1/auth/register/
        {
            "email": "user@example.com",
            "username": "username",
            "first_name": "이름",
            "password": "password123",
            "password_confirm": "password123"
        }
        """
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': '회원가입이 완료되었습니다.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        로그인
        POST /api/v1/auth/login/
        {
            "email": "user@example.com",
            "password": "password123"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'message': '로그인이 완료되었습니다.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'user': UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        로그아웃 (토큰 블랙리스트에 추가)
        POST /api/v1/auth/logout/
        """
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response(
                {'message': '로그아웃이 완료되었습니다.'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        현재 사용자 정보 조회
        GET /api/v1/auth/me/
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    사용자 관련 엔드포인트
    - list: 사용자 목록 (관리자만)
    - retrieve: 사용자 상세 정보
    - update: 사용자 정보 수정
    """
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """관리자만 모든 사용자 조회 가능"""
        if self.request.user.role == 'admin':
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=True, methods=['put', 'patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request, pk=None):
        """
        사용자 정보 수정
        PUT /api/v1/users/{id}/update_profile/
        {
            "first_name": "새로운 이름",
            "phone": "01012345678"
        }
        """
        user = self.get_object()

        # 자신의 정보만 수정 가능
        if user.id != request.user.id:
            return Response(
                {'error': '자신의 정보만 수정할 수 있습니다.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': '사용자 정보가 수정되었습니다.', 'data': UserDetailSerializer(user).data},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_account(self, request):
        """
        계정 삭제
        DELETE /api/v1/users/delete_account/
        """
        user = request.user
        user.delete()
        return Response(
            {'message': '계정이 삭제되었습니다.'},
            status=status.HTTP_200_OK,
        )
