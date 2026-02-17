"""파일 시스템 기반 인증 정보 저장소 구현체 (Data Layer)"""

import json
from pathlib import Path
from typing import List, Optional

from diary.domain.entities.ai_credential import AICredential, AIProvider
from diary.domain.interfaces.credential_repository import CredentialRepositoryInterface


class FileSystemCredentialRepository(CredentialRepositoryInterface):
    """파일 시스템 기반 AI 인증 정보 저장소

    JSON 파일로 credentials를 저장합니다.
    Domain의 CredentialRepositoryInterface를 구현합니다 (의존성 역전).

    파일 구조:
    {
        "credentials": [
            {
                "provider": "openai",
                "api_key": "sk-proj-xxx",
                "is_default": true,
                "created_at": "2024-02-17T12:00:00",
                "updated_at": "2024-02-17T12:00:00",
                "name": "My OpenAI Account"
            }
        ]
    }
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Args:
            file_path: credentials JSON 파일 경로 (기본: data/credentials.json)
        """
        if file_path is None:
            # 프로젝트 루트의 data/ 디렉토리 사용
            project_root = Path(__file__).parent.parent.parent.parent
            self.file_path = project_root / "data" / "credentials.json"
        else:
            self.file_path = Path(file_path)

        # data 디렉토리가 없으면 생성
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # 파일이 없으면 빈 구조로 초기화
        if not self.file_path.exists():
            self._write_data({"credentials": []})

    def _read_data(self) -> dict:
        """JSON 파일 읽기"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # 파일이 손상되었거나 없으면 빈 구조 반환
            return {"credentials": []}

    def _write_data(self, data: dict) -> None:
        """JSON 파일 쓰기"""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _get_credentials_list(self) -> List[dict]:
        """credentials 리스트 조회"""
        data = self._read_data()
        return data.get("credentials", [])

    def _save_credentials_list(self, credentials: List[dict]) -> None:
        """credentials 리스트 저장"""
        self._write_data({"credentials": credentials})

    def save(self, credential: AICredential) -> None:
        """AI 인증 정보 저장

        Args:
            credential: 저장할 인증 정보

        Raises:
            ValueError: 이미 동일한 provider의 credential이 존재하는 경우
        """
        credentials = self._get_credentials_list()

        # 중복 확인
        for cred_dict in credentials:
            if cred_dict["provider"] == credential.provider.value:
                raise ValueError(f"{credential.provider.value} 인증 정보가 이미 존재합니다")

        # 추가
        credentials.append(credential.to_dict())
        self._save_credentials_list(credentials)

    def get_by_provider(self, provider: AIProvider) -> Optional[AICredential]:
        """특정 AI provider의 인증 정보 조회

        Args:
            provider: AI 서비스 제공자

        Returns:
            인증 정보 또는 None (없는 경우)
        """
        credentials = self._get_credentials_list()

        for cred_dict in credentials:
            if cred_dict["provider"] == provider.value:
                return AICredential.from_dict(cred_dict)

        return None

    def get_default(self) -> Optional[AICredential]:
        """기본 AI 인증 정보 조회

        Returns:
            기본으로 설정된 인증 정보 또는 None
        """
        credentials = self._get_credentials_list()

        for cred_dict in credentials:
            if cred_dict.get("is_default", False):
                return AICredential.from_dict(cred_dict)

        return None

    def get_all(self) -> List[AICredential]:
        """모든 AI 인증 정보 조회

        Returns:
            모든 인증 정보 리스트
        """
        credentials = self._get_credentials_list()
        return [AICredential.from_dict(cred_dict) for cred_dict in credentials]

    def update(self, credential: AICredential) -> None:
        """AI 인증 정보 업데이트

        Args:
            credential: 업데이트할 인증 정보 (provider 기준으로 식별)

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        credentials = self._get_credentials_list()

        updated = False
        for i, cred_dict in enumerate(credentials):
            if cred_dict["provider"] == credential.provider.value:
                credentials[i] = credential.to_dict()
                updated = True
                break

        if not updated:
            raise ValueError(f"{credential.provider.value} 인증 정보가 존재하지 않습니다")

        self._save_credentials_list(credentials)

    def delete(self, provider: AIProvider) -> None:
        """AI 인증 정보 삭제

        Args:
            provider: 삭제할 AI 서비스 제공자

        Raises:
            ValueError: 해당 provider의 credential이 존재하지 않는 경우
        """
        credentials = self._get_credentials_list()

        initial_count = len(credentials)
        credentials = [
            cred_dict for cred_dict in credentials
            if cred_dict["provider"] != provider.value
        ]

        if len(credentials) == initial_count:
            raise ValueError(f"{provider.value} 인증 정보가 존재하지 않습니다")

        self._save_credentials_list(credentials)

    def exists(self, provider: AIProvider) -> bool:
        """특정 provider의 인증 정보가 존재하는지 확인

        Args:
            provider: AI 서비스 제공자

        Returns:
            존재 여부
        """
        credentials = self._get_credentials_list()

        for cred_dict in credentials:
            if cred_dict["provider"] == provider.value:
                return True

        return False
