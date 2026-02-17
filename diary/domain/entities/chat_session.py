"""채팅 세션 엔티티"""

from typing import List, Optional
from datetime import datetime
from .chat_message import ChatMessage, MessageRole


class ChatSession:
    """대화 세션 - 하루치 대화를 관리"""

    def __init__(
        self,
        session_id: str,
        messages: Optional[List[ChatMessage]] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        metadata: Optional[dict] = None,
        is_active: bool = True
    ):
        self.session_id = session_id
        self.messages = messages or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.metadata = metadata or {}
        self.is_active = is_active

    def add_message(self, role: MessageRole, content: str) -> None:
        """
        비즈니스 로직: 메시지 추가

        새 메시지를 추가하고 업데이트 시간을 갱신합니다.
        """
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now()
        )
        self.messages.append(message)
        self.updated_at = datetime.now()

    def get_conversation_history(self) -> List[dict]:
        """
        AI API 호출용 대화 히스토리 반환

        Returns:
            [{"role": "user", "content": "..."}, ...] 형식
        """
        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in self.messages
        ]

    def get_user_messages_only(self) -> List[str]:
        """사용자 메시지만 추출"""
        return [
            msg.content
            for msg in self.messages
            if msg.role == MessageRole.USER
        ]

    def get_message_count(self) -> int:
        """총 메시지 수"""
        return len(self.messages)

    def get_user_message_count(self) -> int:
        """사용자 메시지 수만 카운트"""
        return len(self.get_user_messages_only())

    def end_session(self) -> None:
        """세션 종료"""
        self.is_active = False
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        """딕셔너리로 변환 (저장용)"""
        return {
            "session_id": self.session_id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
            "is_active": self.is_active
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatSession":
        """딕셔너리에서 복원 (로드용)"""
        from .chat_message import ChatMessage

        return cls(
            session_id=data["session_id"],
            messages=[ChatMessage.from_dict(msg) for msg in data["messages"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            metadata=data.get("metadata", {}),
            is_active=data.get("is_active", True)
        )
