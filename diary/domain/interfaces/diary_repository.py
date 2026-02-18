"""
일기 저장소 인터페이스 - Domain이 정의, Data가 구현

의존성 역전 원칙(DIP):
- Domain Layer가 인터페이스를 정의
- Data Layer가 이 인터페이스를 구현 (파일, DB 등)
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List, Tuple
from diary.domain.entities.diary import Diary


class DiaryRepositoryInterface(ABC):
    """일기 저장 및 조회 인터페이스"""

    @abstractmethod
    def save(self, diary: Diary) -> Diary:
        """
        일기 저장

        Args:
            diary: 저장할 일기

        Returns:
            저장된 일기 (diary_id 포함)
        """
        pass

    @abstractmethod
    def get_by_date(self, diary_date: date) -> Optional[Diary]:
        """
        특정 날짜의 일기 조회

        Args:
            diary_date: 조회할 날짜

        Returns:
            일기 또는 None (존재하지 않을 경우)
        """
        pass

    @abstractmethod
    def get_by_id(self, diary_id: str) -> Optional[Diary]:
        """
        ID로 일기 조회

        Args:
            diary_id: 일기 ID

        Returns:
            일기 또는 None
        """
        pass

    @abstractmethod
    def list_diaries(
        self,
        cursor: Optional[str] = None,
        limit: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Diary], Optional[str]]:
        """
        일기 목록 조회 (Cursor 기반 페이지네이션)

        Args:
            cursor: 페이지네이션 커서 (None이면 처음부터)
            limit: 한 번에 가져올 개수
            start_date: 시작 날짜 필터 (선택적)
            end_date: 종료 날짜 필터 (선택적)

        Returns:
            (일기 리스트, 다음 커서)
            - 일기 리스트: 최신순으로 정렬된 일기들
            - 다음 커서: 다음 페이지를 가져올 커서 (더 이상 없으면 None)

        Example:
            # 첫 페이지
            diaries, next_cursor = repo.list_diaries(limit=10)

            # 다음 페이지
            more_diaries, next_cursor = repo.list_diaries(cursor=next_cursor, limit=10)
        """
        pass

    @abstractmethod
    def delete(self, diary_id: str) -> bool:
        """
        일기 삭제

        Args:
            diary_id: 삭제할 일기 ID

        Returns:
            삭제 성공 여부
        """
        pass

    @abstractmethod
    def exists_on_date(self, diary_date: date) -> bool:
        """
        특정 날짜에 일기가 존재하는지 확인

        Args:
            diary_date: 확인할 날짜

        Returns:
            존재 여부
        """
        pass
