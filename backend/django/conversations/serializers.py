from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, Message, ConversationReport
from characters.models import Character

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """메시지 Serializer"""

    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "role",
            "content",
            "token_usage",
            "safety_status",
            "filtered",
            "filter_reason",
            "model_version",
            "citations",
            "error_code",
            "retry_count",
            "metadata",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "conversation",  # conversation은 add_message 액션에서 자동 설정
            "token_usage",
            "safety_status",
            "filtered",
            "filter_reason",
            "model_version",
            "prompt_hash",
            "error_code",
            "retry_count",
            "created_at",
        ]


class ConversationListSerializer(serializers.ModelSerializer):
    """대화 목록용 간단한 Serializer"""
    character_name = serializers.CharField(source="character.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    message_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "character",
            "character_name",
            "user_name",
            "title",
            "subject",
            "message_count",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "message_count",
        ]

    def get_message_count(self, obj):
        """메시지 개수 반환"""
        return obj.messages.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """대화 상세 조회용 Serializer"""
    character_name = serializers.CharField(source="character.name", read_only=True)
    user_name = serializers.CharField(source="user.username", read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = [
            "id",
            "user",
            "user_name",
            "character",
            "character_name",
            "classroom",
            "title",
            "subject",
            "policy_snapshot_ref",
            "is_active",
            "messages",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "character",
            "created_at",
            "updated_at",
        ]


class ConversationCreateSerializer(serializers.ModelSerializer):
    """대화 생성용 Serializer"""

    class Meta:
        model = Conversation
        fields = [
            "character",
            "classroom",
            "title",
            "subject",
            "policy_snapshot_ref",
        ]

    def create(self, validated_data):
        """대화 생성 - 사용자는 요청자로 자동 설정"""
        request = self.context.get("request")
        validated_data["user"] = request.user
        return super().create(validated_data)


class ConversationReportSerializer(serializers.ModelSerializer):
    """대화 리포트 Serializer"""

    class Meta:
        model = ConversationReport
        fields = [
            "id",
            "conversation",
            "summary",
            "quiz_data",
            "pdf_url",
            "generated_at",
        ]
        read_only_fields = [
            "id",
            "generated_at",
        ]
