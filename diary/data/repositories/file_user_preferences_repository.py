"""파일 시스템 기반 사용자 설정 저장소 구현체 (Data Layer)"""

import json
from pathlib import Path
from typing import Optional

from diary.domain.entities.user_preferences import UserPreferences
from diary.domain.interfaces.user_preferences_repository import UserPreferencesRepositoryInterface


class FileSystemUserPreferencesRepository(UserPreferencesRepositoryInterface):
    """파일 시스템 기반 사용자 설정 저장소

    JSON 파일로 사용자 설정을 저장합니다.
    Domain의 UserPreferencesRepositoryInterface를 구현합니다 (의존성 역전).

    파일 구조:
    {
        "writing_style": "first_person_autobiography",
        "created_at": "2024-02-17T12:00:00",
        "updated_at": "2024-02-17T12:00:00"
    }
    """

    def __init__(self, file_path: Optional[str] = None):
        """
        Args:
            file_path: preferences JSON 파일 경로 (기본: data/user_preferences.json)
        """
        if file_path is None:
            # 프로젝트 루트의 data/ 디렉토리 사용
            project_root = Path(__file__).parent.parent.parent.parent
            self.file_path = project_root / "data" / "user_preferences.json"
        else:
            self.file_path = Path(file_path)

        # data 디렉토리가 없으면 생성
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, preferences: UserPreferences) -> None:
        """사용자 설정 저장

        Args:
            preferences: 저장할 사용자 설정

        Raises:
            IOError: 파일 쓰기 실패 시
        """
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(preferences.to_dict(), f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"사용자 설정 저장 실패: {e}")

    def get(self) -> Optional[UserPreferences]:
        """사용자 설정 조회

        Returns:
            저장된 설정이 있으면 UserPreferences 객체, 없으면 None

        Raises:
            IOError: 파일 읽기 실패 시 (파일 손상 등)
        """
        if not self.file_path.exists():
            return None

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return UserPreferences.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            # 파일이 손상되었거나 형식이 잘못된 경우
            raise IOError(f"사용자 설정 파일이 손상되었습니다: {e}")

    def exists(self) -> bool:
        """사용자 설정 존재 여부 확인

        Returns:
            설정 파일이 존재하면 True, 없으면 False
        """
        return self.file_path.exists()

    def delete(self) -> None:
        """사용자 설정 삭제

        Raises:
            FileNotFoundError: 삭제할 파일이 없는 경우
            IOError: 파일 삭제 실패 시
        """
        if not self.file_path.exists():
            raise FileNotFoundError("삭제할 사용자 설정이 없습니다")

        try:
            self.file_path.unlink()
        except IOError as e:
            raise IOError(f"사용자 설정 삭제 실패: {e}")
