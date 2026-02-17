"""CLI 명령어 인터페이스"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from diary.domain.services import CredentialService, UserPreferencesService
from diary.presentation.preferences_ui import PreferencesUI
from diary.presentation.api_key_ui import ApiKeyUI


class DiaryApp:
    """일기 CLI 애플리케이션

    생성자 주입(Constructor Injection)을 통해 의존성을 받습니다.
    """

    def __init__(
        self,
        credential_service: CredentialService,
        preferences_service: UserPreferencesService,
    ):
        """
        Args:
            credential_service: AI 인증 정보 관리 서비스 (Domain Layer)
            preferences_service: 사용자 설정 관리 서비스 (Domain Layer)
        """
        self.credential_service = credential_service
        self.preferences_service = preferences_service
        self.console = Console()

        # UI 컴포넌트 초기화
        self.preferences_ui = PreferencesUI(preferences_service, self.console)
        self.api_key_ui = ApiKeyUI(credential_service, self.console)

    def run(self):
        """애플리케이션 실행"""
        # API 키 확인 - 없으면 등록 플로우로 이동
        if not self.credential_service.has_any_credential():
            self.console.print(
                Panel.fit(
                    "[bold yellow]⚠️  There is not registered API Key[/bold yellow]\n\n"
                    "You need API Key.",
                    border_style="yellow",
                    title="API Key Required",
                )
            )
            self.console.print()

            if not self.api_key_ui.setup_api_key():
                self.console.print("[red]✗[/red] Fail to register API Key.")
                raise typer.Exit(1)

            self.console.print()

        # 메인 메뉴 실행
        self._show_menu()

    def _show_menu(self):
        """메인 메뉴 표시"""
        # 환영 메시지
        self.console.print(
            Panel.fit(
                "[bold cyan]Daily CLI - AI Diary Write Assistant[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print()

        # 현재 사용 중인 AI 표시
        default_cred = self.credential_service.get_default_credential()
        if default_cred:
            self.console.print(
                f"[dim]AI current used: {default_cred.provider.value} "
                f"({default_cred.mask_api_key()})[/dim]"
            )
            self.console.print()

        # 메뉴 선택
        self.console.print("[bold]What do you want to do?[/bold]")
        self.console.print("  1. Write Diary")
        self.console.print("  2. Manage API Keys")
        self.console.print("  3. Manage Preferences")
        self.console.print("  4. Exit")
        self.console.print()

        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"], default="1")

        if choice == "1":
            self._write_diary()
        elif choice == "2":
            self._manage_api_keys()
        elif choice == "3":
            self._manage_preferences()
        elif choice == "4":
            self.console.print("[dim]GoodBye![/dim]")
            raise typer.Exit(0)

    def _write_diary(self):
        """일기 작성 시작"""
        self.console.print("[bold green]일기 작성을 시작합니다...[/bold green]")
        self.console.print("[dim]이 기능은 아직 구현 중입니다.[/dim]")

    def _manage_api_keys(self):
        """API 키 관리 메뉴 (ApiKeyUI에 위임)"""
        self.api_key_ui.show_management_menu(on_back_callback=self._show_menu)

    def _manage_preferences(self):
        """사용자 설정 관리 메뉴 (PreferencesUI에 위임)"""
        self.preferences_ui.show_preferences_menu(on_back_callback=self._show_menu)
