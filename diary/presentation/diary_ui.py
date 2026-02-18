"""일기 관리 UI 컴포넌트"""

from typing import Optional, List
from datetime import date
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from diary.domain.services import DiaryService
from diary.domain.entities import Diary


class DiaryUI:
    """일기 관리 UI - 단일 책임 원칙 적용"""

    def __init__(self, diary_service: DiaryService, console: Console):
        """
        Args:
            diary_service: 일기 비즈니스 로직
            console: Rich Console 객체
        """
        self.diary_service = diary_service
        self.console = console
        self._current_cursor: Optional[str] = None
        self._current_diaries: List[Diary] = []

    def show_diary_list(self, on_back_callback=None, limit: int = 10):
        """
        일기 목록 표시 (Cursor 기반 페이지네이션)

        Args:
            on_back_callback: 뒤로가기 콜백 함수
            limit: 한 페이지당 표시할 일기 개수
        """

        if on_back_callback:
            self.on_back_callback = on_back_callback

        self.console.clear()
        self.console.print(
            Panel(
                "[bold cyan]일기 목록[/bold cyan]\n\n"
                "작성된 일기를 조회하고 관리할 수 있습니다.",
                border_style="cyan",
            )
        )

        # 첫 페이지 로드
        self._load_diaries(cursor=None, limit=limit)

        while True:
            # 일기 목록 표시
            self._display_diaries()

            # 메뉴 선택
            self.console.print("\n[bold]옵션:[/bold]")
            self.console.print("  [cyan]1-9[/cyan]  - 일기 상세 보기 (번호 입력)")
            if self._current_cursor:
                self.console.print("  [cyan]n[/cyan]    - 다음 페이지")
            self.console.print("  [cyan]r[/cyan]    - 날짜 범위 검색")
            self.console.print("  [cyan]b[/cyan]    - 뒤로가기")

            choice = Prompt.ask("\n선택", default="b").strip().lower()

            if choice == "b":
                if self.on_back_callback:
                    self.on_back_callback()
                break
            elif choice == "n" and self._current_cursor:
                # 다음 페이지
                self._load_diaries(cursor=self._current_cursor, limit=limit)
            elif choice == "r":
                # 날짜 범위 검색
                self._search_by_date_range(limit=limit)
            elif choice.isdigit():
                # 일기 상세 보기
                index = int(choice) - 1
                if 0 <= index < len(self._current_diaries):
                    self._show_diary_detail(
                        self._current_diaries[index], self.show_diary_list
                    )
                else:
                    self.console.print(
                        "[red]잘못된 번호입니다. 다시 선택해주세요.[/red]"
                    )
                    input("\nEnter를 눌러 계속...")
            else:
                self.console.print("[red]잘못된 선택입니다.[/red]")
                input("\nEnter를 눌러 계속...")

    def _load_diaries(
        self,
        cursor: Optional[str] = None,
        limit: int = 10,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ):
        """
        일기 목록 로드

        Args:
            cursor: 페이지네이션 커서
            limit: 로드할 개수
            start_date: 시작 날짜 (필터)
            end_date: 종료 날짜 (필터)
        """
        try:
            diaries, next_cursor = self.diary_service.list_diaries(
                cursor=cursor, limit=limit, start_date=start_date, end_date=end_date
            )
            self._current_diaries = diaries
            self._current_cursor = next_cursor

            if not diaries:
                self.console.print("\n[yellow]일기가 없습니다.[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]오류 발생: {e}[/red]")
            self._current_diaries = []
            self._current_cursor = None

    def _display_diaries(self):
        """현재 로드된 일기 목록 표시"""
        if not self._current_diaries:
            return

        self.console.print("\n")

        # Rich Table 생성
        table = Table(title="📔 일기 목록", show_header=True, header_style="bold cyan")
        table.add_column("번호", style="dim", width=6, justify="center")
        table.add_column("날짜", style="cyan", width=30)
        table.add_column("내용 미리보기", style="white")
        table.add_column("글자 수", justify="right", width=10)

        for i, diary in enumerate(self._current_diaries, 1):
            # 내용 미리보기 (50자)
            preview = (
                diary.content[:50] + "..." if len(diary.content) > 50 else diary.content
            )

            table.add_row(
                str(i),
                diary.get_formatted_date(),
                preview,
                f"{diary.get_word_count()}자",
            )

        self.console.print(table)

        # 페이지네이션 정보
        if self._current_cursor:
            self.console.print(
                "\n[dim]다음 페이지가 있습니다. 'n'을 입력하여 더 보기[/dim]"
            )
        else:
            self.console.print("\n[dim]마지막 페이지입니다.[/dim]")

    def _show_diary_detail(self, diary: Diary, on_back_callback_detail=None):
        """
        일기 상세 보기

        Args:
            diary: 조회할 일기
        """
        self.console.clear()

        if diary.created_at and diary.updated_at:
            self.console.print(
                Panel(
                    f"[bold cyan]{diary.get_formatted_date()}[/bold cyan]\n\n"
                    f"{diary.content}\n\n"
                    f"[dim]글자 수: {diary.get_word_count()}자[/dim]\n"
                    f"[dim]작성: {diary.created_at.strftime('%Y-%m-%d %H:%M')}[/dim]\n"
                    f"[dim]수정: {diary.updated_at.strftime('%Y-%m-%d %H:%M')}[/dim]",
                    border_style="cyan",
                    title="📖 일기 상세",
                )
            )
        else:
            self.console.print(
                Panel(
                    f"[bold cyan]{diary.get_formatted_date()}[/bold cyan]\n\n"
                    f"{diary.content}\n\n"
                    f"[dim]글자 수: {diary.get_word_count()}자[/dim]\n",
                    border_style="cyan",
                    title="📖 일기 상세",
                )
            )

        # 옵션 메뉴
        self.console.print("\n[bold]옵션:[/bold]")
        self.console.print("  [cyan]e[/cyan] - 수정")
        self.console.print("  [cyan]d[/cyan] - 삭제")
        self.console.print("  [cyan]b[/cyan] - 뒤로가기")

        choice = Prompt.ask("\n선택", default="b").strip().lower()

        if choice == "e":
            self._edit_diary(diary)
        elif choice == "d":
            self._delete_diary(diary)
        elif choice == "b":
            if on_back_callback_detail:
                on_back_callback_detail()
                return
        else:
            self.console.print("[red]잘못된 선택입니다.[/red]")
            input("\nEnter를 눌러 계속...")

    def _edit_diary(self, diary: Diary):
        """
        일기 수정

        Args:
            diary: 수정할 일기
        """
        self.console.print("\n[cyan]새로운 내용을 입력하세요 (취소: 빈 입력)[/cyan]")
        self.console.print("[dim]현재 내용:[/dim]")
        self.console.print(f"[dim]{diary.content}[/dim]\n")

        new_content = Prompt.ask("새 내용")

        if not new_content.strip():
            self.console.print("[yellow]수정이 취소되었습니다.[/yellow]")
            input("\nEnter를 눌러 계속...")
            return

        try:
            if diary.diary_id:
                updated_diary = self.diary_service.update_diary(
                    diary.diary_id, new_content
                )
                self.console.print(
                    f"\n[green]✓ 일기가 수정되었습니다.[/green]\n"
                    f"[dim]수정 시각: {updated_diary.updated_at.strftime('%Y-%m-%d %H:%M')}[/dim]"
                )
            else:
                self.console.print("[red]일기 ID가 없어 수정할 수 없습니다.[/red]")
        except Exception as e:
            self.console.print(f"[red]오류 발생: {e}[/red]")

        input("\nEnter를 눌러 계속...")

    def _delete_diary(self, diary: Diary):
        """
        일기 삭제

        Args:
            diary: 삭제할 일기
        """
        self.console.print(
            f"\n[red]정말 삭제하시겠습니까?[/red]\n"
            f"날짜: {diary.get_formatted_date()}\n"
            f"내용: {diary.content[:50]}..."
        )

        confirm = Prompt.ask("삭제 확인 (yes/no)", default="no").strip().lower()

        if confirm not in ["yes", "y"]:
            self.console.print("[yellow]삭제가 취소되었습니다.[/yellow]")
            input("\nEnter를 눌러 계속...")
            return

        try:
            if diary.diary_id:
                deleted = self.diary_service.delete_diary(diary.diary_id)
                if deleted:
                    self.console.print("\n[green]✓ 일기가 삭제되었습니다.[/green]")
                    # 목록에서 제거
                    self._current_diaries.remove(diary)
                else:
                    self.console.print("[red]일기 삭제에 실패했습니다.[/red]")
            else:
                self.console.print("[red]일기 ID가 없어 삭제할 수 없습니다.[/red]")
        except Exception as e:
            self.console.print(f"[red]오류 발생: {e}[/red]")

        input("\nEnter를 눌러 계속...")

    def _search_by_date_range(self, limit: int = 10):
        """
        날짜 범위로 검색

        Args:
            limit: 한 페이지당 표시할 개수
        """
        self.console.print("\n[cyan]날짜 범위 검색[/cyan]")
        self.console.print("[dim]형식: YYYY-MM-DD (예: 2024-02-18)[/dim]")
        self.console.print("[dim]빈 입력 시 제한 없음[/dim]\n")

        # 시작 날짜
        start_input = Prompt.ask("시작 날짜", default="").strip()
        start_date = None
        if start_input:
            try:
                start_date = date.fromisoformat(start_input)
            except ValueError:
                self.console.print("[red]잘못된 날짜 형식입니다.[/red]")
                input("\nEnter를 눌러 계속...")
                return

        # 종료 날짜
        end_input = Prompt.ask("종료 날짜", default="").strip()
        end_date = None
        if end_input:
            try:
                end_date = date.fromisoformat(end_input)
            except ValueError:
                self.console.print("[red]잘못된 날짜 형식입니다.[/red]")
                input("\nEnter를 눌러 계속...")
                return

        # 날짜 범위 유효성 검사
        if start_date and end_date and start_date > end_date:
            self.console.print(
                "[red]시작 날짜는 종료 날짜보다 이전이어야 합니다.[/red]"
            )
            input("\nEnter를 눌러 계속...")
            return

        # 검색 실행
        self._load_diaries(
            cursor=None, limit=limit, start_date=start_date, end_date=end_date
        )

        if self._current_diaries:
            self.console.print(
                f"\n[green]✓ {len(self._current_diaries)}개의 일기를 찾았습니다.[/green]"
            )
        else:
            self.console.print("\n[yellow]검색 결과가 없습니다.[/yellow]")

        input("\nEnter를 눌러 계속...")
