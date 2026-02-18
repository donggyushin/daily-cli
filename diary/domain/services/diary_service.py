"""
일기 도메인 서비스 - 비즈니스 로직 처리

Domain Layer의 서비스로, 일기 관련 비즈니스 로직을 관리합니다.
"""

from datetime import date
from typing import Optional, List, Tuple
from diary.domain.entities.diary import Diary
from diary.domain.interfaces.diary_repository import DiaryRepositoryInterface


class DiaryService:
    """
    일기 비즈니스 로직 서비스

    의존성:
    - DiaryRepositoryInterface: 일기 저장소 (인터페이스에만 의존)
    """

    def __init__(self, diary_repo: DiaryRepositoryInterface):
        """
        Args:
            diary_repo: 일기 저장소 구현체
        """
        self.diary_repo = diary_repo

    def create_diary(self, diary_date: date, content: str) -> Diary:
        """
        새 일기 작성

        Args:
            diary_date: 일기 날짜
            content: 일기 내용

        Returns:
            저장된 일기

        Raises:
            ValueError: 내용이 비어있거나 해당 날짜에 이미 일기가 존재하는 경우
        """
        # 비즈니스 규칙 검증
        if not content or not content.strip():
            raise ValueError("일기 내용은 비어있을 수 없습니다.")

        if self.diary_repo.exists_on_date(diary_date):
            raise ValueError(
                f"{diary_date} 날짜의 일기가 이미 존재합니다. 수정을 원하시면 update를 사용하세요."
            )

        # 일기 엔티티 생성
        diary = Diary(diary_date=diary_date, content=content.strip())

        # 저장
        return self.diary_repo.save(diary)

    def update_diary(self, diary_id: str, new_content: str) -> Diary:
        """
        일기 수정

        Args:
            diary_id: 일기 ID
            new_content: 새로운 내용

        Returns:
            수정된 일기

        Raises:
            ValueError: 일기가 존재하지 않거나 내용이 비어있는 경우
        """
        # 일기 조회
        diary = self.diary_repo.get_by_id(diary_id)
        if not diary:
            raise ValueError(f"ID {diary_id}의 일기를 찾을 수 없습니다.")

        # 엔티티의 비즈니스 로직 사용
        diary.update_content(new_content)

        # 저장
        return self.diary_repo.save(diary)

    def update_diary_by_date(self, diary_date: date, new_content: str) -> Diary:
        """
        날짜로 일기 수정

        Args:
            diary_date: 일기 날짜
            new_content: 새로운 내용

        Returns:
            수정된 일기

        Raises:
            ValueError: 해당 날짜의 일기가 존재하지 않는 경우
        """
        diary = self.diary_repo.get_by_date(diary_date)
        if not diary:
            raise ValueError(f"{diary_date} 날짜의 일기를 찾을 수 없습니다.")

        diary.update_content(new_content)
        return self.diary_repo.save(diary)

    def get_diary_by_date(self, diary_date: date) -> Optional[Diary]:
        """
        특정 날짜의 일기 조회

        Args:
            diary_date: 조회할 날짜

        Returns:
            일기 또는 None
        """
        return self.diary_repo.get_by_date(diary_date)

    def get_diary_by_id(self, diary_id: str) -> Optional[Diary]:
        """
        ID로 일기 조회

        Args:
            diary_id: 조회할 일기 ID

        Returns:
            일기 또는 None
        """
        return self.diary_repo.get_by_id(diary_id)

    def get_today_diary(self) -> Optional[Diary]:
        """오늘의 일기 조회"""
        return self.diary_repo.get_by_date(date.today())

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
            cursor: 페이지네이션 커서
            limit: 한 번에 가져올 개수
            start_date: 시작 날짜 필터
            end_date: 종료 날짜 필터

        Returns:
            (일기 리스트, 다음 커서)
        """
        return self.diary_repo.list_diaries(
            cursor=cursor, limit=limit, start_date=start_date, end_date=end_date
        )

    def delete_diary(self, diary_id: str) -> bool:
        """
        일기 삭제

        Args:
            diary_id: 삭제할 일기 ID

        Returns:
            삭제 성공 여부
        """
        return self.diary_repo.delete(diary_id)

    def delete_diary_by_date(self, diary_date: date) -> bool:
        """
        날짜로 일기 삭제

        Args:
            diary_date: 삭제할 날짜

        Returns:
            삭제 성공 여부

        Raises:
            ValueError: 해당 날짜의 일기가 존재하지 않는 경우
        """
        diary = self.diary_repo.get_by_date(diary_date)
        if not diary:
            raise ValueError(f"{diary_date} 날짜의 일기를 찾을 수 없습니다.")

        if diary.diary_id:
            return self.diary_repo.delete(diary.diary_id)
        else:
            return False

    def has_diary_on_date(self, diary_date: date) -> bool:
        """특정 날짜에 일기가 있는지 확인"""
        return self.diary_repo.exists_on_date(diary_date)
