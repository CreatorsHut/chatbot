"""
캐릭터 프롬프트 생성 유틸리티
- 성격, 배경, 연출 스타일을 조합하여 최종 프롬프트 생성
"""


def generate_system_prompt(character_data: dict) -> str:
    """
    캐릭터 데이터로부터 시스템 프롬프트를 자동 생성합니다.

    Args:
        character_data: {
            'name': str,
            'short_description': str,
            'personality_traits': dict,
            'background_story': str,
            'world_setting': str,
            'teaching_style': str,
            'example_conversations': list,
            'narration_style': str,
            'moderation_level': str
        }

    Returns:
        str: 최종 시스템 프롬프트
    """
    parts = [
        f"당신은 '{character_data.get('name', 'Assistant')}'이라는 AI 캐릭터입니다.",
        ""
    ]

    # 1. 기본 정보
    if character_data.get('short_description'):
        parts.append(f"## 소개\n{character_data['short_description']}")

    # 2. 성격
    traits = character_data.get('personality_traits', {})
    if traits:
        parts.append("## 성격")
        if traits.get("core_traits"):
            parts.append(f"기본 특성: {', '.join(traits['core_traits'])}")
        if traits.get("tone"):
            parts.append(f"톤: {traits['tone']}")
        if traits.get("speech_style"):
            parts.append(f"말투: {traits['speech_style']}")
        if traits.get("catchphrase"):
            parts.append(f"대표 멘트: \"{traits['catchphrase']}\"")

    # 3. 배경
    if character_data.get('background_story'):
        parts.append(f"## 배경 이야기\n{character_data['background_story']}")

    # 4. 세계관
    if character_data.get('world_setting'):
        parts.append(f"## 세계관\n{character_data['world_setting']}")

    # 5. 교수법
    if character_data.get('teaching_style'):
        parts.append(f"## 학습 스타일\n{character_data['teaching_style']}")

    # 6. 연출 스타일
    narration_style = character_data.get('narration_style', 'none')
    if narration_style != "none":
        parts.append("## 대화 스타일 - 연출 표기법")
        parts.append("""
- 행동/표정: *별표로 감싸기* (예: *웃으며*, *고개를 끄덕인다*)
- 배경/상황: [대괄호로 감싸기] (예: [조용한 도서관], [햇빛이 들어오는 창문])
- 심리/생각: (소괄호로 감싸기) (예: (진지한 표정으로), (자랑스러운 미소))

대사 70%, 서술 30% 정도의 균형으로 생동감 있게 작성하세요.""")

    # 7. 예시 대화
    conversations = character_data.get('example_conversations', [])
    if conversations:
        parts.append("## 예시 대화")
        for ex in conversations[:5]:  # 최대 5개
            parts.append(f"- 사용자: \"{ex.get('user', '')}\"")
            parts.append(f"  당신: \"{ex.get('char', '')}\"")

    # 8. 주의사항
    parts.append("## 주의사항")
    moderation = character_data.get('moderation_level', 'high')
    moderation_text = {
        'low': '낮음 (일반)',
        'medium': '중간',
        'high': '높음 (교육용)'
    }.get(moderation, '높음')

    parts.append(f"""
- 항상 '{character_data.get('name', '')}'의 성격과 말투를 유지하세요
- {character_data.get('name', '')}의 관점에서만 이야기하세요
- 교육용 서비스이므로 부적절한 내용은 피하세요
- 안전 수준: {moderation_text}""")

    return "\n".join(parts)


def validate_prompt(prompt: str) -> dict:
    """
    프롬프트 유효성 검사

    Returns:
        {
            'is_valid': bool,
            'errors': list,
            'warnings': list,
            'length': int
        }
    """
    errors = []
    warnings = []

    if not prompt or len(prompt.strip()) == 0:
        errors.append("프롬프트가 비어있습니다.")

    if len(prompt) < 100:
        warnings.append("프롬프트가 너무 짧습니다. (최소 100자 권장)")

    if len(prompt) > 10000:
        warnings.append("프롬프트가 너무 깁니다. (최대 10000자 권장)")

    # 필수 섹션 확인
    required_sections = ["## 성격", "## 배경", "## 주의사항"]
    for section in required_sections:
        if section not in prompt:
            warnings.append(f"'{section}' 섹션이 없습니다.")

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'length': len(prompt)
    }


def format_example_conversations(conversations: list) -> str:
    """
    예시 대화를 포맷팅합니다.
    """
    if not conversations:
        return ""

    formatted = []
    for i, conv in enumerate(conversations[:5], 1):
        formatted.append(f"{i}. 사용자: \"{conv.get('user', '')}\"")
        formatted.append(f"   {conv.get('name', 'Assistant')}: \"{conv.get('char', '')}\"")

    return "\n".join(formatted)


def build_narration_guide(narration_style: str) -> str:
    """
    연출 스타일 가이드를 생성합니다.
    """
    guides = {
        "none": "연출을 사용하지 않습니다. 순수 대사만 제공하세요.",

        "minimal": """최소한의 연출을 사용합니다.
        - 간단한 행동만 가끔 추가 (예: *웃으며*, *고개를 끄덕인다*)
        - 대부분은 대사 중심
        """,

        "novel": """소설형 연출을 사용합니다 (추천).
        - 행동/표정: *별표로 감싸기*
        - 배경/상황: [대괄호로 감싸기]
        - 심리/생각: (소괄호로 감싸기)

        예시:
        *교실 문을 열고 들어오며 밝게 웃는다*
        "안녕! 오늘 날씨 정말 좋지 않아?"
        *창밖을 가리키며 햇살이 들어오는 곳을 바라본다*
        """,

        "screenplay": """시나리오형 연출을 사용합니다.
        [배경: 도서관 구석 자리, 고요한 오후]
        장영실: "흠... 이 천문도를 보게. 별의 움직임이 참으로 신비롭지 않나?"
        (책장을 넘기며 옛 기억에 잠긴 표정)
        """
    }

    return guides.get(narration_style, guides["none"])
