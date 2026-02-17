"""AI 인증 정보 엔티티"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class AIProvider(Enum):
    """지원하는 AI 서비스 제공자"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    # 추가 가능: COHERE = "cohere", etc.


@dataclass
class AICredential:
    """AI 서비스 인증 정보

    Attributes:
        provider: AI 서비스 제공자 (OpenAI, Anthropic 등)
        api_key: API 키
        is_default: 기본 AI로 사용할지 여부 (한 개만 True)
        created_at: 생성 일시
        updated_at: 수정 일시
        name: 사용자 지정 이름 (선택, 예: "내 OpenAI 계정")
    """
    provider: AIProvider
    api_key: str
    is_default: bool = False
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    name: Optional[str] = None

    def __post_init__(self):
        """생성 시 타임스탬프 자동 설정"""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def update_api_key(self, new_api_key: str) -> None:
        """API 키 변경 (비즈니스 로직)"""
        if not new_api_key or not new_api_key.strip():
            raise ValueError("API 키는 비어있을 수 없습니다")

        self.api_key = new_api_key.strip()
        self.updated_at = datetime.now()

    def set_as_default(self) -> None:
        """기본 AI로 설정"""
        self.is_default = True
        self.updated_at = datetime.now()

    def unset_as_default(self) -> None:
        """기본 AI 해제"""
        self.is_default = False
        self.updated_at = datetime.now()

    def mask_api_key(self) -> str:
        """API 키 마스킹 (보안을 위해 일부만 표시)

        Returns:
            예: "sk-proj-...abc123" (앞 8자 + ... + 뒤 6자)
        """
        if len(self.api_key) <= 14:
            return "***" + self.api_key[-4:]

        return f"{self.api_key[:8]}...{self.api_key[-6:]}"

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (저장 시 사용)"""
        return {
            "provider": self.provider.value,
            "api_key": self.api_key,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AICredential":
        """딕셔너리에서 복원 (조회 시 사용)"""
        return cls(
            provider=AIProvider(data["provider"]),
            api_key=data["api_key"],
            is_default=data.get("is_default", False),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
            name=data.get("name"),
        )
