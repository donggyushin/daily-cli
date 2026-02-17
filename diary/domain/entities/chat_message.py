"""채팅 메시지 엔티티"""

from enum import Enum
from datetime import datetime
from dataclasses import dataclass


class MessageRole(Enum):
    """메시지 역할 구분"""
    SYSTEM = "system"        # 시스템 프롬프트
    USER = "user"            # 사용자 메시지
    ASSISTANT = "assistant"  # AI 응답


@dataclass
class ChatMessage:
    """개별 채팅 메시지"""
    role: MessageRole
    content: str
    timestamp: datetime

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (저장용)"""
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatMessage":
        """딕셔너리에서 복원 (로드용)"""
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )
