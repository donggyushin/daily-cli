"""채팅 저장소 인터페이스 - Domain이 정의, Data가 구현"""

from abc import ABC, abstractmethod
from typing import Optional, List
from diary.domain.entities.chat_session import ChatSession


class ChatRepositoryInterface(ABC):
    """채팅 세션 저장 및 조회 인터페이스"""

    @abstractmethod
    def save_session(self, session: ChatSession) -> None:
        """
        채팅 세션 저장

        Args:
            session: 저장할 채팅 세션
        """
        pass

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """
        특정 세션 조회

        Args:
            session_id: 세션 ID

        Returns:
            ChatSession 또는 None (존재하지 않을 경우)
        """
        pass

    @abstractmethod
    def get_active_session(self) -> Optional[ChatSession]:
        """
        현재 활성화된 세션 반환

        Returns:
            활성 세션 또는 None
        """
        pass

    @abstractmethod
    def list_sessions(self, limit: int = 10) -> List[ChatSession]:
        """
        세션 목록 조회 (최신순)

        Args:
            limit: 조회할 최대 개수

        Returns:
            세션 리스트
        """
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> bool:
        """
        세션 삭제

        Args:
            session_id: 삭제할 세션 ID

        Returns:
            삭제 성공 여부
        """
        pass
