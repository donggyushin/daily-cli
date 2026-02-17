"""일기 작성 스타일 엔티티"""

from enum import Enum
from dataclasses import dataclass


class WritingStyle(Enum):
    """일기 작성 스타일

    사용자가 선택할 수 있는 3가지 일기 작성 스타일
    """
    OBJECTIVE_THIRD_PERSON = "objective_third_person"  # 객관적 3인칭
    FIRST_PERSON_AUTOBIOGRAPHY = "first_person_autobiography"  # 1인칭 자서전
    EMOTIONAL_LITERARY = "emotional_literary"  # 감성적/문학적

    def get_display_name(self) -> str:
        """사용자에게 보여줄 스타일 이름"""
        display_names = {
            WritingStyle.OBJECTIVE_THIRD_PERSON: "객관적 3인칭",
            WritingStyle.FIRST_PERSON_AUTOBIOGRAPHY: "1인칭 자서전",
            WritingStyle.EMOTIONAL_LITERARY: "감성적/문학적",
        }
        return display_names[self]

    def get_description(self) -> str:
        """스타일 설명"""
        descriptions = {
            WritingStyle.OBJECTIVE_THIRD_PERSON: "그는 오늘 피곤한 하루를 보냈다",
            WritingStyle.FIRST_PERSON_AUTOBIOGRAPHY: "오늘은 피곤한 하루였다",
            WritingStyle.EMOTIONAL_LITERARY: "긴 회의들 사이로 피로가 밀려왔다",
        }
        return descriptions[self]

    def get_prompt_instruction(self, examples: list[str] | None = None) -> str:
        """AI에게 전달할 프롬프트 지시사항

        각 스타일에 맞는 일기 작성 방식을 AI에게 설명

        Args:
            examples: 추가 예시 문장 리스트 (EMOTIONAL_LITERARY 스타일에서 활용)

        Returns:
            AI 프롬프트 지시사항
        """
        instructions = {
            WritingStyle.OBJECTIVE_THIRD_PERSON: (
                "일기를 객관적인 3인칭 시점으로 작성해주세요. "
                "주어를 '그', '그녀'로 하여 마치 관찰자가 기록하는 것처럼 써주세요. "
                "예: '그는 오늘 피곤한 하루를 보냈다.'"
            ),
            WritingStyle.FIRST_PERSON_AUTOBIOGRAPHY: (
                "일기를 1인칭 자서전 스타일로 작성해주세요. "
                "'나는', '오늘은'과 같은 표현을 사용하여 자연스럽게 써주세요. "
                "예: '오늘은 피곤한 하루였다.'"
            ),
            WritingStyle.EMOTIONAL_LITERARY: (
                "일기를 감성적이고 문학적인 스타일로 작성해주세요. "
                "비유, 은유, 서정적인 표현을 사용하여 감정을 풍부하게 담아주세요. "
                "예: '긴 회의들 사이로 피로가 밀려왔다.'"
            ),
        }

        base_instruction = instructions[self]

        # EMOTIONAL_LITERARY 스타일이고 예시가 있으면 강화된 프롬프트 생성
        if self == WritingStyle.EMOTIONAL_LITERARY and examples:
            examples_text = "\n".join([f"- {ex}" for ex in examples])
            return (
                f"{base_instruction}\n\n"
                f"다음은 참고할 수 있는 문학적 표현 예시입니다:\n{examples_text}\n\n"
                f"이러한 스타일을 참고하여 깊이 있고 감성적인 일기를 작성해주세요."
            )

        return base_instruction


@dataclass
class WritingStyleInfo:
    """스타일 정보 (UI 표시용)

    Attributes:
        style: 스타일 Enum
        display_name: 표시 이름
        description: 예시 문장
        prompt_instruction: AI 프롬프트 지시사항
    """
    style: WritingStyle
    display_name: str
    description: str
    prompt_instruction: str

    @classmethod
    def from_style(cls, style: WritingStyle) -> "WritingStyleInfo":
        """WritingStyle Enum으로부터 정보 객체 생성"""
        return cls(
            style=style,
            display_name=style.get_display_name(),
            description=style.get_description(),
            prompt_instruction=style.get_prompt_instruction(),
        )

    @classmethod
    def get_all_styles(cls) -> list["WritingStyleInfo"]:
        """모든 스타일 정보 리스트 반환"""
        return [cls.from_style(style) for style in WritingStyle]
