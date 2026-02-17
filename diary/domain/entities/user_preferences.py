"""사용자 설정 엔티티"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .writing_style import WritingStyle


@dataclass
class UserPreferences:
    """사용자 설정

    일기 작성과 관련된 사용자의 개인 설정을 관리합니다.

    Attributes:
        writing_style: 선택한 일기 작성 스타일
        created_at: 설정 생성 일시
        updated_at: 설정 수정 일시
    """
    writing_style: WritingStyle = WritingStyle.FIRST_PERSON_AUTOBIOGRAPHY  # 기본값: 1인칭 자서전
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """생성 시 타임스탬프 자동 설정"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def change_writing_style(self, new_style: WritingStyle) -> None:
        """일기 작성 스타일 변경 (비즈니스 로직)

        Args:
            new_style: 새로운 스타일

        Raises:
            ValueError: 유효하지 않은 스타일인 경우
        """
        if not isinstance(new_style, WritingStyle):
            raise ValueError("유효한 WritingStyle을 선택해야 합니다")

        self.writing_style = new_style
        self.updated_at = datetime.now()

    def get_style_prompt_instruction(self) -> str:
        """현재 선택된 스타일의 AI 프롬프트 지시사항 반환

        Returns:
            AI에게 전달할 스타일 지시사항
        """
        return self.writing_style.get_prompt_instruction()

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (저장 시 사용)"""
        return {
            "writing_style": self.writing_style.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "UserPreferences":
        """딕셔너리에서 복원 (조회 시 사용)"""
        return cls(
            writing_style=WritingStyle(data.get("writing_style", WritingStyle.FIRST_PERSON_AUTOBIOGRAPHY.value)),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )

    @classmethod
    def create_default(cls) -> "UserPreferences":
        """기본 설정으로 생성

        Returns:
            기본 설정이 적용된 UserPreferences 객체
        """
        return cls()
