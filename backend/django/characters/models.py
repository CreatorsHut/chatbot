from django.db import models
from django.conf import settings


class Character(models.Model):
    """
    캐릭터 모델 - 소설형 대화 중심
    - 관리자/교사/학생이 생성 가능 (단계적)
    - 생동감 있는 성격, 배경, 연출 스타일 포함
    - 교사 승인 후 사용 가능
    """

    # ========== 선택지 ==========
    CATEGORY_CHOICES = [
        ("educator", "교육자"),  # 선생님, 멘토
        ("historical", "역사인물"),  # 장영실, 클레오파트라
        ("fictional", "가상인물"),  # 판타지, 만화 캐릭터
        ("mentor", "멘토"),  # 상담, 진로
        ("friend", "친구"),  # 친구 관계
        ("other", "기타"),
    ]

    STATUS_CHOICES = [
        ("draft", "임시저장"),
        ("pending", "승인대기"),
        ("approved", "승인됨"),
        ("rejected", "반려됨"),
    ]

    VISIBILITY_CHOICES = [
        ("private", "비공개"),
        ("draft", "임시"),
        ("public", "공개"),
    ]

    SUBJECT_CHOICES = [
        ("korean", "국어"),
        ("math", "수학"),
        ("english", "영어"),
        ("science", "과학"),
        ("history", "역사"),
        ("social_studies", "사회"),
        ("general", "일반"),
    ]

    NARRATION_STYLE_CHOICES = [
        ("none", "연출 없음"),
        ("minimal", "최소 (*행동* 가끔)"),
        ("novel", "소설형 (전체 서술)"),
        ("screenplay", "시나리오형"),
    ]

    # ========== 기본 정보 ==========
    name = models.CharField(
        max_length=100,
        verbose_name="캐릭터 이름",
        help_text="예: 장영실, 수학 쌤 리사"
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="characters",
        verbose_name="생성자"
    )

    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="characters",
        verbose_name="소속 조직"
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="educator",
        verbose_name="카테고리"
    )

    subject = models.CharField(
        max_length=20,
        choices=SUBJECT_CHOICES,
        default="general",
        verbose_name="담당 과목"
    )

    short_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="한 줄 설명",
        help_text="예: '수학을 사랑하는 친절한 선생님'"
    )

    avatar_url = models.URLField(
        max_length=500,  # DALL-E URL은 매우 길 수 있음
        blank=True,
        null=True,
        verbose_name="아바타 URL"
    )

    # ========== 🎨 성격 설정 (Character Traits) ==========
    personality_traits = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="성격/특성",
        help_text="""
        {
            "core_traits": ["친절함", "유머러스", "진지함"],
            "speech_style": "~요, ~네, 존댓말",
            "catchphrase": "항상 응원할게!",
            "tone": "밝고 긍정적인"
        }
        """
    )

    # ========== 📖 배경 스토리 ==========
    background_story = models.TextField(
        blank=True,
        verbose_name="배경 스토리",
        help_text="""
        출신, 경력, 과거 경험
        예: '저는 조선시대 과학자 장영실입니다. 천문과 시계 연구에...'
        """
    )

    world_setting = models.TextField(
        blank=True,
        verbose_name="세계관/배경",
        help_text="현재 시간, 장소, 상황 등. 예: '현대 한국 서울, 고등학교 3학년 교실'"
    )

    teaching_style = models.TextField(
        blank=True,
        verbose_name="교수법/학습 스타일",
        help_text="예: '소크라테스식 질문, 단계적 설명, 실생활 사례 중심'"
    )

    # ========== 💬 예시 대화 (Few-shot learning) ==========
    example_conversations = models.JSONField(
        default=list,
        blank=True,
        verbose_name="예시 대화",
        help_text="""
        [
            {"user": "안녕?", "char": "*밝게 웃으며* 안녕! 오늘 기분이 어때?"},
            {"user": "힘들어", "char": "*걱정스러운 표정으로* 무슨 일 있어? 말해봐, 들어줄게."}
        ]
        캐릭터의 말투를 학습할 수 있는 예시 (5개 이상 권장)
        """
    )

    greeting_message = models.TextField(
        blank=True,
        verbose_name="첫 대사",
        help_text="첫 대화 시작 멘트. 예: '*방문을 열고 밝게 인사한다* 안녕! 오늘은 뭘 배우고 싶어?'"
    )

    # ========== 🎭 연출 스타일 ==========
    narration_style = models.CharField(
        max_length=20,
        choices=NARRATION_STYLE_CHOICES,
        default="novel",
        verbose_name="연출 스타일",
        help_text="소설형으로 선택하면 행동(*), 배경([]), 심리()를 자동으로 포함"
    )

    narration_template = models.TextField(
        blank=True,
        verbose_name="연출 표기법",
        help_text="""
        행동: *별표로 감싸기*
        배경: [대괄호로 감싸기]
        심리: (소괄호로 감싸기)
        """
    )

    # ========== 🤖 AI 프롬프트 ==========
    system_prompt = models.TextField(
        blank=True,
        default="",
        verbose_name="시스템 프롬프트",
        help_text="AI 모델에 전달될 최종 프롬프트 (비워두면 자동 생성됨)"
    )

    # ========== ⚙️ 제어 설정 ==========
    creativity = models.FloatField(
        default=0.7,
        verbose_name="창의성 (temperature)",
        help_text="0.0(결정적) ~ 1.0(창의적)"
    )

    context_length = models.IntegerField(
        default=50,
        verbose_name="대화 기억 범위 (턴)",
        help_text="이전 몇 턴까지 기억할지 (10~100)"
    )

    moderation_level = models.CharField(
        max_length=20,
        choices=[("low", "낮음"), ("medium", "중간"), ("high", "높음")],
        default="high",
        verbose_name="안전 수준",
        help_text="교육용은 높음 권장"
    )

    # ========== 상태 관리 ==========
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name="상태"
    )

    visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default="private",
        verbose_name="공개 범위"
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_characters",
        verbose_name="승인자"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="승인일시"
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True,
        verbose_name="반려 사유"
    )

    # ========== 메타데이터 ==========
    version = models.CharField(
        max_length=20,
        default="1.0",
        verbose_name="버전"
    )

    tags = models.JSONField(
        default=list,
        blank=True,
        verbose_name="태그",
        help_text="검색용 태그. 예: ['친절', '재미있는', '초등학생용']"
    )

    usage_count = models.IntegerField(
        default=0,
        verbose_name="사용 횟수"
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
        db_table = "characters"
        verbose_name = "캐릭터"
        verbose_name_plural = "캐릭터"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["subject", "visibility"]),
            models.Index(fields=["category", "visibility"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def build_system_prompt(self) -> str:
        """
        성격, 배경, 연출 스타일을 조합하여 최종 시스템 프롬프트 생성
        """
        parts = [
            f"당신은 '{self.name}'이라는 AI 캐릭터입니다.",
            ""
        ]

        # 1. 기본 정보
        if self.short_description:
            parts.append(f"## 소개\n{self.short_description}")

        # 2. 성격
        traits = self.personality_traits
        if traits:
            parts.append("## 성격")
            if traits.get("core_traits"):
                parts.append(f"기본 특성: {', '.join(traits['core_traits'])}")
            if traits.get("tone"):
                parts.append(f"톤: {traits['tone']}")
            if traits.get("speech_style"):
                parts.append(f"말투: {traits['speech_style']}")
            if traits.get("catchphrase"):
                parts.append(f"대표 멘트: {traits['catchphrase']}")

        # 3. 배경
        if self.background_story:
            parts.append(f"## 배경 이야기\n{self.background_story}")

        # 4. 세계관
        if self.world_setting:
            parts.append(f"## 세계관\n{self.world_setting}")

        # 5. 교수법
        if self.teaching_style:
            parts.append(f"## 학습 스타일\n{self.teaching_style}")

        # 6. 연출 스타일
        if self.narration_style != "none":
            parts.append("## 대화 스타일 - 연출 표기법")
            parts.append("""
**표기 규칙:**
- 행동/표정: *별표로 감싸기* (예: *활짝 웃으며 손을 흔든다*, *진지한 표정으로 팔짱을 낀다*)
- 배경/상황: [대괄호로 감싸기] (예: [조용한 도서관, 오후의 따뜻한 햇살], [복잡한 복도, 학생들의 웃음소리])
- 심리/감정: (소괄호로 감싸기) (예: (뿌듯한 마음으로), (걱정스러운 눈빛으로))

**표정과 감정 표현 - 상황에 따라 다양하게:**
- 긍정적: 환하게 웃다, 미소 짓다, 눈을 반짝이다, 신나게, 기쁜 표정으로, 뿌듯해하며
- 중립적: 고개를 끄덕이다, 생각에 잠기다, 턱을 괴다, 잠시 멈추다, 진지하게
- 부정적: 걱정스럽게, 미간을 찌푸리다, 고개를 갸우뚱하다, 한숨을 쉬다, 안타까워하며
- 강조: 열정적으로, 단호하게, 자신감 있게, 확신에 차서, 힘주어
- 섬세함: 조심스럽게, 부드럽게, 따뜻하게, 차분하게, 천천히

**이모지 사용 규칙 (매우 중요!):**
⚠️ 절대 같은 이모지를 연속해서 사용하지 마세요! 매 응답마다 다른 이모지를 선택하세요!

상황별 이모지 가이드:
- 기쁨/흥분: 😊 😃 😄 😁 🙂 🤗 😍 🥰 🤩 ✨ 💫 🌟 ⭐
- 사랑/애정: 😍 🥰 😘 💕 💖 💗 💝 💞 💓
- 생각/고민: 🤔 🧐 💭 🤨 😯 😮
- 중립/평온: 😌 🙂 😐 😑 😶
- 놀람: 😮 😯 😲 🤯 😳 
- 슬픔/걱정: 😔 😕 🙁 ☹️ 😢 😥 😰 😨
- 화남/짜증: 😤 😠 😡 😣 😖 😫 😩
- 장난/재미: 😏 😜 😝 😛 🤪 😋
- 피곤/지침: 😪 😴 🥱 😓
- 특별/강조: ✨ 💫 🌟 ⭐ 🎯 🎉 🎊

**이모지 배치:**
- *행동* 시작 부분에 배치: *✨ 눈을 반짝이며*
- 또는 행동 끝에 배치: *활짝 웃으며 손을 흔든다 👋*
- 절대 문장 중간이나 대사에 넣지 말 것

**작성 지침:**
- 대사 70%, 서술 30% 정도의 균형 유지
- 같은 표현 반복 피하기
- 상황과 감정에 맞는 구체적이고 생동감 있는 묘사
- 소설처럼 읽히도록 자연스러운 흐름

**❌ 나쁜 예시 (절대 하지 말 것!):**
"*😊 웃으며* 안녕하세요!"
"*😊 웃으며* 좋은 생각이에요!"
"*😊 웃으며* 그렇군요!"
→ 같은 이모지와 표현을 계속 반복!

**✅ 좋은 예시 (이렇게 다양하게!):**
1번 응답: "*✨ 눈을 반짝이며* 안녕하세요! 오늘은 무엇을 배워볼까요?"
2번 응답: "*🤔 턱을 괴며 생각에 잠겨* 음... 좋은 질문이네요!"
3번 응답: "*😄 활짝 웃으며 손뼉을 친다* 정말 훌륭해요!"
4번 응답: "*💫 신나게* 와! 그거 정말 재미있는 생각인데요?"
5번 응답: "*😌 부드럽게 미소 지으며* 괜찮아요, 천천히 해봐요."
6번 응답: "*🌟 자신감 있게 고개를 끄덕이며* 네, 맞아요! 잘 이해했어요!"

매 응답마다 다른 이모지와 다른 행동 표현을 사용하세요!
""")

        # 7. 예시 대화
        if self.example_conversations:
            parts.append("## 예시 대화")
            for ex in self.example_conversations[:5]:  # 최대 5개
                parts.append(f"- 사용자: \"{ex.get('user', '')}\"")
                parts.append(f"  당신: \"{ex.get('char', '')}\"")

        # 8. 주의사항
        parts.append("## 주의사항")
        parts.append(f"""
- 항상 '{self.name}'의 성격과 말투를 유지하세요
- {self.name}의 관점에서만 이야기하세요
- 교육용 서비스이므로 부적절한 내용은 피하세요
- 안전 수준: {self.get_moderation_level_display()}
""")

        return "\n".join(parts)
