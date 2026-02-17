"""인증 정보 관리 비즈니스 로직"""

from typing import List, Optional

from diary.domain.entities.ai_credential import AICredential, AIProvider
from diary.domain.interfaces.credential_repository import CredentialRepositoryInterface


class CredentialService:
    """AI 인증 정보 관리 서비스

    비즈니스 로직:
    - API 키 저장 시 기본 AI 자동 설정
    - 기본 AI 변경 시 기존 기본 AI 해제
    - API 키 삭제 시 기본 AI였다면 다른 AI를 기본으로 설정
    - 유효성 검증 등
    """

    def __init__(self, credential_repo: CredentialRepositoryInterface):
        """
        Args:
            credential_repo: 인증 정보 저장소 (인터페이스, 구현체는 모름)
        """
        self.credential_repo = credential_repo

    def save_credential(self, provider: AIProvider, api_key: str, name: Optional[str] = None) -> AICredential:
        """AI 인증 정보 저장

        비즈니스 규칙:
        - 이미 존재하는 provider면 업데이트
        - 첫 번째 저장된 credential은 자동으로 기본 AI로 설정

        Args:
            provider: AI 서비스 제공자
            api_key: API 키
            name: 사용자 지정 이름 (선택)

        Returns:
            저장된 인증 정보

        Raises:
            ValueError: API 키가 비어있는 경우
        """
        if not api_key or not api_key.strip():
            raise ValueError("API 키는 비어있을 수 없습니다")

        # 기존 credential이 있는지 확인
        existing = self.credential_repo.get_by_provider(provider)

        if existing:
            # 업데이트
            existing.update_api_key(api_key)
            if name:
                existing.name = name
            self.credential_repo.update(existing)
            return existing
        else:
            # 신규 생성
            all_credentials = self.credential_repo.get_all()
            is_first = len(all_credentials) == 0

            credential = AICredential(
                provider=provider,
                api_key=api_key.strip(),
                is_default=is_first,  # 첫 번째면 기본 AI로 설정
                name=name,
            )
            self.credential_repo.save(credential)
            return credential

    def set_default_provider(self, provider: AIProvider) -> AICredential:
        """기본 AI 변경

        비즈니스 규칙:
        - 기존 기본 AI는 자동으로 해제됨

        Args:
            provider: 기본으로 설정할 AI 서비스 제공자

        Returns:
            기본으로 설정된 인증 정보

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        credential = self.credential_repo.get_by_provider(provider)
        if not credential:
            raise ValueError(f"{provider.value} 인증 정보가 존재하지 않습니다")

        # 기존 기본 AI 해제
        current_default = self.credential_repo.get_default()
        if current_default and current_default.provider != provider:
            current_default.unset_as_default()
            self.credential_repo.update(current_default)

        # 새로운 기본 AI 설정
        credential.set_as_default()
        self.credential_repo.update(credential)

        return credential

    def get_default_credential(self) -> Optional[AICredential]:
        """기본 AI 인증 정보 조회

        Returns:
            기본 인증 정보 또는 None
        """
        return self.credential_repo.get_default()

    def get_credential(self, provider: AIProvider) -> Optional[AICredential]:
        """특정 AI 인증 정보 조회

        Args:
            provider: AI 서비스 제공자

        Returns:
            인증 정보 또는 None
        """
        return self.credential_repo.get_by_provider(provider)

    def list_all_credentials(self) -> List[AICredential]:
        """모든 AI 인증 정보 조회

        Returns:
            모든 인증 정보 리스트 (기본 AI가 맨 앞에 옴)
        """
        credentials = self.credential_repo.get_all()

        # 기본 AI를 맨 앞으로 정렬
        credentials.sort(key=lambda c: (not c.is_default, c.provider.value))

        return credentials

    def delete_credential(self, provider: AIProvider) -> None:
        """AI 인증 정보 삭제

        비즈니스 규칙:
        - 기본 AI를 삭제하면 남은 AI 중 하나를 자동으로 기본 AI로 설정

        Args:
            provider: 삭제할 AI 서비스 제공자

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        credential = self.credential_repo.get_by_provider(provider)
        if not credential:
            raise ValueError(f"{provider.value} 인증 정보가 존재하지 않습니다")

        was_default = credential.is_default

        # 삭제
        self.credential_repo.delete(provider)

        # 기본 AI였다면 다른 AI를 기본으로 설정
        if was_default:
            remaining = self.credential_repo.get_all()
            if remaining:
                first = remaining[0]
                first.set_as_default()
                self.credential_repo.update(first)

    def has_any_credential(self) -> bool:
        """등록된 AI 인증 정보가 있는지 확인

        Returns:
            하나라도 있으면 True
        """
        return len(self.credential_repo.get_all()) > 0

    def validate_api_key_format(self, provider: AIProvider, api_key: str) -> bool:
        """API 키 형식 검증 (간단한 규칙)

        Args:
            provider: AI 서비스 제공자
            api_key: 검증할 API 키

        Returns:
            유효하면 True
        """
        if not api_key or not api_key.strip():
            return False

        # 간단한 형식 검증 (실제 API 호출은 Data Layer에서)
        api_key = api_key.strip()

        if provider == AIProvider.OPENAI:
            # OpenAI: sk-proj-... 형식
            return api_key.startswith("sk-") and len(api_key) > 20
        elif provider == AIProvider.ANTHROPIC:
            # Anthropic: sk-ant-... 형식
            return api_key.startswith("sk-ant-") and len(api_key) > 20
        elif provider == AIProvider.GOOGLE:
            # Google: 다양한 형식 가능
            return len(api_key) > 20

        # 기타 provider는 길이만 검증
        return len(api_key) > 10
