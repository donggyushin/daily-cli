"""
일기 엔티티 - 비즈니스 로직 포함

Domain Layer의 핵심 엔티티로, 일기 데이터와 관련 비즈니스 규칙을 정의합니다.
"""

from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass


@dataclass
class Diary:
    """
    일기 엔티티

    Attributes:
        diary_date: 일기 날짜 (YYYY-MM-DD)
        content: 일기 내용
        diary_id: 일기 고유 ID (저장소에서 생성)
        created_at: 생성 시각
        updated_at: 수정 시각
    """

    diary_date: date
    content: str
    diary_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """생성 후 초기화"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_content(self, new_content: str) -> None:
        """
        일기 내용 수정 (비즈니스 로직)

        Args:
            new_content: 새로운 일기 내용

        Raises:
            ValueError: 내용이 비어있는 경우
        """
        if not new_content or not new_content.strip():
            raise ValueError("일기 내용은 비어있을 수 없습니다.")

        self.content = new_content.strip()
        self.updated_at = datetime.now()

    def is_today(self) -> bool:
        """오늘 작성한 일기인지 확인"""
        return self.diary_date == date.today()

    def get_formatted_date(self) -> str:
        """포맷된 날짜 반환 (예: 2024년 2월 18일 월요일)"""
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        weekday = weekdays[self.diary_date.weekday()]
        return f"{self.diary_date.year}년 {self.diary_date.month}월 {self.diary_date.day}일 {weekday}요일"

    def get_word_count(self) -> int:
        """글자 수 반환"""
        return len(self.content)

    def to_dict(self) -> dict:
        """
        딕셔너리로 변환 (저장용)

        Returns:
            일기 데이터 딕셔너리
        """
        return {
            "diary_id": self.diary_id,
            "diary_date": self.diary_date.isoformat(),
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Diary":
        """
        딕셔너리에서 생성 (로드용)

        Args:
            data: 일기 데이터 딕셔너리

        Returns:
            Diary 인스턴스
        """
        return cls(
            diary_id=data.get("diary_id"),
            diary_date=date.fromisoformat(data["diary_date"]),
            content=data["content"],
            created_at=datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None,
            updated_at=datetime.fromisoformat(data["updated_at"])
            if data.get("updated_at")
            else None,
        )

    def __str__(self) -> str:
        """문자열 표현"""
        return f"[{self.get_formatted_date()}] {self.content[:50]}{'...' if len(self.content) > 50 else ''}"
