"""일기 작성 스타일 예시 문장 저장소 인터페이스

Domain Layer에서 정의하는 인터페이스입니다.
Data Layer가 이 인터페이스를 구현합니다 (의존성 역전).
"""

from abc import ABC, abstractmethod

from diary.domain.entities.writing_style import WritingStyle


class WritingStyleExamplesRepositoryInterface(ABC):
    """일기 작성 스타일 예시 문장 저장소 인터페이스

    각 스타일별 예시 문장을 로드하는 기능을 제공합니다.
    Domain은 이 인터페이스만 알고 있으며, 실제 구현체(파일, DB 등)는 모릅니다.
    """

    @abstractmethod
    def get_examples(self, style: WritingStyle) -> list[str]:
        """특정 스타일의 예시 문장 리스트 조회

        Args:
            style: 일기 작성 스타일

        Returns:
            예시 문장 리스트 (비어있을 수 있음)
        """
        pass
