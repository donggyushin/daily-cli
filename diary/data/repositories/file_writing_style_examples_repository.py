"""파일 시스템 기반 일기 작성 스타일 예시 문장 저장소 구현체 (Data Layer)"""

from pathlib import Path

from diary.domain.entities.writing_style import WritingStyle
from diary.domain.interfaces.writing_style_examples_repository import WritingStyleExamplesRepositoryInterface


class FileSystemWritingStyleExamplesRepository(WritingStyleExamplesRepositoryInterface):
    """파일 시스템 기반 일기 작성 스타일 예시 문장 저장소

    텍스트 파일로 스타일별 예시 문장을 관리합니다.
    Domain의 WritingStyleExamplesRepositoryInterface를 구현합니다 (의존성 역전).

    파일 구조:
    data/writing_examples/
    ├── emotional_literary.txt  (한 줄에 하나씩 예시 문장)
    ├── objective_third_person.txt
    └── first_person_autobiography.txt
    """

    def __init__(self, examples_dir: Path | None = None):
        """
        Args:
            examples_dir: 예시 문장 디렉토리 경로 (기본: data/writing_examples/)
        """
        if examples_dir is None:
            # 프로젝트 루트의 data/writing_examples/ 디렉토리 사용
            project_root = Path(__file__).parent.parent.parent.parent
            self.examples_dir = project_root / "data" / "writing_examples"
        else:
            self.examples_dir = examples_dir

        # 디렉토리가 없으면 생성
        self.examples_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, style: WritingStyle) -> Path:
        """스타일에 해당하는 예시 파일 경로 반환

        Args:
            style: 일기 작성 스타일

        Returns:
            예시 문장 파일 경로
        """
        return self.examples_dir / f"{style.value}.txt"

    def get_examples(self, style: WritingStyle) -> list[str]:
        """특정 스타일의 예시 문장 리스트 조회

        Args:
            style: 일기 작성 스타일

        Returns:
            예시 문장 리스트 (파일이 없거나 비어있으면 빈 리스트)
        """
        file_path = self._get_file_path(style)

        # 파일이 없으면 빈 리스트 반환
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                # 각 줄을 읽고, 빈 줄과 주석(#) 제거
                examples = [
                    line.strip()
                    for line in f.readlines()
                    if line.strip() and not line.strip().startswith("#")  # 빈 줄과 주석 제외
                ]
                return examples
        except Exception:
            # 읽기 실패 시 빈 리스트 반환 (에러를 던지지 않음)
            return []
