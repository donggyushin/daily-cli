"""인증 정보 저장소 인터페이스 (Domain Layer에서 정의)"""

from abc import ABC, abstractmethod
from typing import List, Optional

from diary.domain.entities.ai_credential import AICredential, AIProvider


class CredentialRepositoryInterface(ABC):
    """AI 인증 정보 저장소 인터페이스

    Data Layer에서 이 인터페이스를 구현합니다 (의존성 역전).
    예: FileSystemCredentialRepository, DatabaseCredentialRepository
    """

    @abstractmethod
    def save(self, credential: AICredential) -> None:
        """AI 인증 정보 저장

        Args:
            credential: 저장할 인증 정보

        Raises:
            ValueError: 이미 동일한 provider의 credential이 존재하는 경우
        """
        pass

    @abstractmethod
    def get_by_provider(self, provider: AIProvider) -> Optional[AICredential]:
        """특정 AI provider의 인증 정보 조회

        Args:
            provider: AI 서비스 제공자

        Returns:
            인증 정보 또는 None (없는 경우)
        """
        pass

    @abstractmethod
    def get_default(self) -> Optional[AICredential]:
        """기본 AI 인증 정보 조회

        Returns:
            기본으로 설정된 인증 정보 또는 None
        """
        pass

    @abstractmethod
    def get_all(self) -> List[AICredential]:
        """모든 AI 인증 정보 조회

        Returns:
            모든 인증 정보 리스트
        """
        pass

    @abstractmethod
    def update(self, credential: AICredential) -> None:
        """AI 인증 정보 업데이트

        Args:
            credential: 업데이트할 인증 정보 (provider 기준으로 식별)

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        pass

    @abstractmethod
    def delete(self, provider: AIProvider) -> None:
        """AI 인증 정보 삭제

        Args:
            provider: 삭제할 AI 서비스 제공자

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        pass

    @abstractmethod
    def exists(self, provider: AIProvider) -> bool:
        """특정 provider의 인증 정보가 존재하는지 확인

        Args:
            provider: AI 서비스 제공자

        Returns:
            존재 여부
        """
        pass
