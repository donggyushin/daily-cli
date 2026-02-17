"""사용자 설정 관리 서비스

비즈니스 로직을 담당하는 Domain Service입니다.
"""

from typing import Optional

from diary.domain.entities.user_preferences import UserPreferences
from diary.domain.entities.writing_style import WritingStyle, WritingStyleInfo
from diary.domain.interfaces.user_preferences_repository import UserPreferencesRepositoryInterface


class UserPreferencesService:
    """사용자 설정 관리 서비스

    사용자 설정과 관련된 비즈니스 로직을 처리합니다.
    Repository 인터페이스에만 의존하며, 구체적인 구현체는 모릅니다.

    Attributes:
        preferences_repo: 사용자 설정 저장소 인터페이스
    """

    def __init__(self, preferences_repo: UserPreferencesRepositoryInterface):
        """서비스 초기화

        Args:
            preferences_repo: 사용자 설정 저장소 (인터페이스)
        """
        self.preferences_repo = preferences_repo

    def get_preferences(self) -> UserPreferences:
        """사용자 설정 조회

        저장된 설정이 없으면 기본 설정을 반환하고 저장합니다.

        Returns:
            사용자 설정 객체
        """
        preferences = self.preferences_repo.get()

        if preferences is None:
            # 설정이 없으면 기본 설정 생성 및 저장
            preferences = UserPreferences.create_default()
            self.preferences_repo.save(preferences)

        return preferences

    def update_writing_style(self, new_style: WritingStyle) -> UserPreferences:
        """일기 작성 스타일 변경

        Args:
            new_style: 새로운 스타일

        Returns:
            업데이트된 사용자 설정

        Raises:
            ValueError: 유효하지 않은 스타일인 경우
        """
        preferences = self.get_preferences()
        preferences.change_writing_style(new_style)
        self.preferences_repo.save(preferences)
        return preferences

    def get_current_writing_style(self) -> WritingStyle:
        """현재 선택된 일기 작성 스타일 조회

        Returns:
            현재 스타일
        """
        preferences = self.get_preferences()
        return preferences.writing_style

    def get_style_prompt_instruction(self) -> str:
        """현재 스타일의 AI 프롬프트 지시사항 반환

        AI에게 일기를 작성하도록 요청할 때 사용할 지시사항입니다.

        Returns:
            프롬프트 지시사항
        """
        preferences = self.get_preferences()
        return preferences.get_style_prompt_instruction()

    def get_all_available_styles(self) -> list[WritingStyleInfo]:
        """사용 가능한 모든 스타일 정보 반환

        UI에서 스타일 선택지를 표시할 때 사용합니다.

        Returns:
            모든 스타일 정보 리스트
        """
        return WritingStyleInfo.get_all_styles()

    def reset_to_default(self) -> UserPreferences:
        """설정을 기본값으로 초기화

        Returns:
            초기화된 사용자 설정
        """
        preferences = UserPreferences.create_default()
        self.preferences_repo.save(preferences)
        return preferences

    def has_preferences(self) -> bool:
        """사용자 설정 존재 여부 확인

        Returns:
            설정이 저장되어 있으면 True, 없으면 False
        """
        return self.preferences_repo.exists()
