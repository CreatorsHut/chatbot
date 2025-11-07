from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 시리얼라이저"""
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'password', 'password_confirm']

    def validate(self, data):
        """비밀번호 일치 검증"""
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError({
                'password': '비밀번호가 일치하지 않습니다.'
            })
        return data

    def validate_email(self, value):
        """이메일 중복 검증"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return value

    def validate_username(self, value):
        """username 중복 검증"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('이미 사용 중인 username입니다.')
        return value

    def create(self, validated_data):
        """사용자 생성"""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            password=validated_data['password'],
            role='student'  # 기본 역할은 학생
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """로그인 시리얼라이저"""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        """이메일과 비밀번호로 사용자 인증"""
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')

        if not user.check_password(password):
            raise serializers.ValidationError('이메일 또는 비밀번호가 올바르지 않습니다.')

        if not user.is_active:
            raise serializers.ValidationError('비활성화된 계정입니다.')

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """사용자 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserDetailSerializer(serializers.ModelSerializer):
    """사용자 상세 정보 시리얼라이저"""
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'phone', 'role', 'credit', 'created_at']
        read_only_fields = ['id', 'created_at', 'credit']


class UserUpdateSerializer(serializers.ModelSerializer):
    """사용자 정보 수정 시리얼라이저"""
    class Meta:
        model = User
        fields = ['first_name', 'phone']


class TokenSerializer(serializers.Serializer):
    """토큰 응답 시리얼라이저"""
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
