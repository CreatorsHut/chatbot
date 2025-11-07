from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Character
from .utils import generate_system_prompt, validate_prompt

User = get_user_model()


class CharacterListSerializer(serializers.ModelSerializer):
    """캐릭터 목록 조회용 간단한 Serializer"""
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    owner_type = serializers.CharField(source="owner.role", read_only=True)
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    subject_display = serializers.CharField(
        source="get_subject_display", read_only=True
    )

    class Meta:
        model = Character
        fields = [
            "id",
            "name",
            "short_description",
            "category",
            "category_display",
            "subject",
            "subject_display",
            "avatar_url",
            "owner_name",
            "owner_type",
            "status",
            "visibility",
            "tags",
            "usage_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "usage_count", "owner_type"]


class CharacterDetailSerializer(serializers.ModelSerializer):
    """캐릭터 상세 조회/수정용 Serializer - 전체 필드"""
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    owner_role = serializers.CharField(source="owner.role", read_only=True)
    approved_by_name = serializers.CharField(
        source="approved_by.username", read_only=True, allow_null=True
    )
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    subject_display = serializers.CharField(
        source="get_subject_display", read_only=True
    )
    narration_style_display = serializers.CharField(
        source="get_narration_style_display", read_only=True
    )
    moderation_level_display = serializers.CharField(
        source="get_moderation_level_display", read_only=True
    )

    class Meta:
        model = Character
        fields = [
            "id",
            "name",
            "short_description",
            "category",
            "category_display",
            "subject",
            "subject_display",
            "personality_traits",
            "background_story",
            "world_setting",
            "teaching_style",
            "example_conversations",
            "greeting_message",
            "narration_style",
            "narration_style_display",
            "narration_template",
            "avatar_url",
            "system_prompt",
            "creativity",
            "context_length",
            "moderation_level",
            "moderation_level_display",
            "owner",
            "owner_name",
            "owner_role",
            "organization",
            "status",
            "visibility",
            "version",
            "tags",
            "usage_count",
            "approved_by",
            "approved_by_name",
            "approved_at",
            "rejection_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "owner",
            "owner_role",
            "status",
            "approved_by",
            "approved_at",
            "usage_count",
            "created_at",
            "updated_at",
        ]


class CharacterCreateUpdateSerializer(serializers.ModelSerializer):
    """캐릭터 생성/수정용 Serializer - 프롬프트 튜닝 중심"""
    auto_generate_prompt = serializers.BooleanField(
        write_only=True,
        required=False,
        default=True,
        help_text="성격, 배경 등에서 자동으로 시스템 프롬프트 생성할지 여부"
    )
    avatar_url = serializers.URLField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="아바타 이미지 URL"
    )

    class Meta:
        model = Character
        fields = [
            "name",
            "short_description",
            "category",
            "subject",
            "personality_traits",
            "background_story",
            "world_setting",
            "teaching_style",
            "example_conversations",
            "greeting_message",
            "narration_style",
            "narration_template",
            "avatar_url",
            "system_prompt",
            "creativity",
            "context_length",
            "moderation_level",
            "organization",
            "visibility",
            "tags",
            "auto_generate_prompt",
        ]

    def validate_avatar_url(self, value):
        """avatar_url 검증 - 빈 문자열은 None으로 변환"""
        if value == '' or value is None:
            return None
        return value

    def create(self, validated_data):
        """캐릭터 생성"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"[CharacterSerializer] Creating character with data: {list(validated_data.keys())}")
        
        auto_generate = validated_data.pop("auto_generate_prompt", True)

        # 요청자 정보에서 owner 설정
        request = self.context.get("request")
        validated_data["owner"] = request.user

        # 자동 프롬프트 생성
        if auto_generate and not validated_data.get("system_prompt"):
            try:
                character = Character(**validated_data)
                validated_data["system_prompt"] = character.build_system_prompt()
                logger.info(f"[CharacterSerializer] System prompt generated successfully")
            except Exception as e:
                logger.error(f"[CharacterSerializer] Error generating system prompt: {e}")
                raise

        try:
            character = Character.objects.create(**validated_data)
            logger.info(f"[CharacterSerializer] Character created successfully: {character.id}")
            return character
        except Exception as e:
            logger.error(f"[CharacterSerializer] Error creating character: {e}")
            raise

    def update(self, instance, validated_data):
        """캐릭터 수정"""
        auto_generate = validated_data.pop("auto_generate_prompt", True)

        # 필드 업데이트
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)

        # 자동 프롬프트 생성
        if auto_generate:
            instance.system_prompt = instance.build_system_prompt()

        instance.save()
        return instance


class CharacterApprovalSerializer(serializers.ModelSerializer):
    """캐릭터 승인/반려용 Serializer (관리자 전용)"""

    class Meta:
        model = Character
        fields = [
            "id",
            "status",
            "rejection_reason",
        ]

    def update(self, instance, validated_data):
        """승인/반려 처리"""
        from django.utils import timezone

        request = self.context.get("request")
        status = validated_data.get("status", instance.status)

        if status == "approved":
            instance.status = "approved"
            instance.approved_by = request.user
            instance.approved_at = timezone.now()
            instance.rejection_reason = None
        elif status == "rejected":
            instance.status = "rejected"
            instance.rejection_reason = validated_data.get("rejection_reason", "")

        instance.save()
        return instance


class CharacterPromptPreviewSerializer(serializers.Serializer):
    """프롬프트 미리보기용 Serializer"""
    name = serializers.CharField()
    short_description = serializers.CharField(required=False, allow_blank=True)
    personality_traits = serializers.JSONField(required=False)
    background_story = serializers.CharField(required=False, allow_blank=True)
    world_setting = serializers.CharField(required=False, allow_blank=True)
    teaching_style = serializers.CharField(required=False, allow_blank=True)
    example_conversations = serializers.ListField(required=False)
    narration_style = serializers.CharField(required=False, default="novel")
    moderation_level = serializers.CharField(required=False, default="high")

    def to_representation(self, instance):
        """프롬프트 미리보기 결과"""
        # utils의 generate_system_prompt 사용
        prompt = generate_system_prompt(instance)
        validation = validate_prompt(prompt)

        return {
            "system_prompt": prompt,
            "validation": validation,
            "character_info": {
                "name": instance.get("name"),
                "short_description": instance.get("short_description"),
                "category": instance.get("category", "educator"),
            }
        }
