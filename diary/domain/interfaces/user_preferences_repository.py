"""사용자 설정 저장소 인터페이스

Domain Layer에서 정의하는 인터페이스입니다.
Data Layer가 이 인터페이스를 구현합니다 (의존성 역전).
"""

from abc import ABC, abstractmethod
from typing import Optional

from diary.domain.entities.user_preferences import UserPreferences


class UserPreferencesRepositoryInterface(ABC):
    """사용자 설정 저장/조회 인터페이스

    Domain은 이 인터페이스만 알고 있으며, 실제 구현체(파일, DB 등)는 모릅니다.
    """

    @abstractmethod
    def save(self, preferences: UserPreferences) -> None:
        """사용자 설정 저장

        Args:
            preferences: 저장할 사용자 설정

        Raises:
            Exception: 저장 실패 시
        """
        pass

    @abstractmethod
    def get(self) -> Optional[UserPreferences]:
        """사용자 설정 조회

        Returns:
            저장된 설정이 있으면 UserPreferences 객체, 없으면 None

        Raises:
            Exception: 조회 실패 시
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        """사용자 설정 존재 여부 확인

        Returns:
            설정이 저장되어 있으면 True, 없으면 False
        """
        pass

    @abstractmethod
    def delete(self) -> None:
        """사용자 설정 삭제

        Raises:
            Exception: 삭제 실패 시
        """
        pass
