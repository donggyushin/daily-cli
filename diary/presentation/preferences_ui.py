"""사용자 설정 관리 UI"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from diary.domain.services import UserPreferencesService


class PreferencesUI:
    """사용자 설정 관리 UI

    일기 작성 스타일 등 사용자 설정을 관리하는 UI를 제공합니다.
    """

    def __init__(self, preferences_service: UserPreferencesService, console: Console):
        """
        Args:
            preferences_service: 사용자 설정 관리 서비스 (Domain Layer)
            console: Rich Console 인스턴스
        """
        self.preferences_service = preferences_service
        self.console = console

    def show_preferences_menu(self, on_back_callback=None):
        """사용자 설정 관리 메뉴 표시

        Args:
            on_back_callback: 뒤로 가기 시 호출할 콜백 함수
        """
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]User Preferences Management[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print()

        # 현재 설정 표시
        current_style = self.preferences_service.get_current_writing_style()
        self.console.print(
            f"[bold]Current Writing Style:[/bold] "
            f"[green]{current_style.get_display_name()}[/green]"
        )
        self.console.print(f"[dim]  Example: {current_style.get_description()}[/dim]")
        self.console.print()

        # 모든 사용 가능한 스타일 표시
        available_styles = self.preferences_service.get_all_available_styles()

        self.console.print("[bold]Available Styles:[/bold]")
        for i, style_info in enumerate(available_styles, 1):
            marker = "⭐" if style_info.style == current_style else "  "
            self.console.print(
                f"  {i}. {marker} [cyan]{style_info.display_name}[/cyan]"
            )
            self.console.print(f"      [dim]{style_info.description}[/dim]")
        self.console.print()

        # 옵션 메뉴
        self.console.print("[bold]Options:[/bold]")
        self.console.print("  1. Change writing style")
        self.console.print("  2. Reset to default")
        self.console.print("  3. Back to main menu")
        self.console.print()

        choice = Prompt.ask("Choice", choices=["1", "2", "3"], default="3")

        if choice == "1":
            self.change_writing_style()
        elif choice == "2":
            self.reset_preferences()
        elif choice == "3":
            if on_back_callback:
                on_back_callback()

    def change_writing_style(self):
        """일기 작성 스타일 변경"""
        self.console.print()
        self.console.print("[bold]Select writing style:[/bold]")

        available_styles = self.preferences_service.get_all_available_styles()
        choices = []
        style_map = {}

        for i, style_info in enumerate(available_styles, 1):
            self.console.print(
                f"  {i}. [cyan]{style_info.display_name}[/cyan] - "
                f"[dim]{style_info.description}[/dim]"
            )
            choices.append(str(i))
            style_map[str(i)] = style_info.style

        self.console.print()
        choice = Prompt.ask("Select", choices=choices)

        selected_style = style_map[choice]

        try:
            self.preferences_service.update_writing_style(selected_style)
            self.console.print(
                f"[green]✓[/green] Writing style changed to "
                f"[cyan]{selected_style.get_display_name()}[/cyan]"
            )
            self.console.print()
            # 다시 설정 메뉴로
            self.show_preferences_menu()
        except ValueError as e:
            self.console.print(f"[red]✗[/red] Error: {e}")

    def reset_preferences(self):
        """사용자 설정 초기화"""
        self.console.print()
        confirm = Prompt.ask(
            "Do you want to reset all preferences to default? (yes/no)",
            choices=["yes", "no"],
            default="no",
        )

        if confirm == "yes":
            try:
                preferences = self.preferences_service.reset_to_default()
                self.console.print(
                    f"[green]✓[/green] Preferences reset to default. "
                    f"Writing style: [cyan]{preferences.writing_style.get_display_name()}[/cyan]"
                )
                self.console.print()
                # 다시 설정 메뉴로
                self.show_preferences_menu()
            except Exception as e:
                self.console.print(f"[red]✗[/red] Error: {e}")
        else:
            self.console.print("[dim]Cancelled.[/dim]")
            self.console.print()
            self.show_preferences_menu()
