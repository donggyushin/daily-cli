"""CLI 명령어 인터페이스"""

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from diary.domain.entities import AIProvider
from diary.domain.services import CredentialService, UserPreferencesService
from diary.presentation.preferences_ui import PreferencesUI


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

            if not self._setup_api_key():
                self.console.print("[red]✗[/red] Fail to register API Key.")
                raise typer.Exit(1)

            self.console.print()

        # 메인 메뉴 실행
        self._show_menu()

    def _setup_api_key(self) -> bool:
        """API 키 등록 플로우

        Returns:
            성공 여부
        """
        self.console.print("[bold]Choose AI service which you use:[/bold]")
        self.console.print("  1. OpenAI (GPT-4)")
        self.console.print("  2. Anthropic (Claude)")
        self.console.print("  3. Google (Gemini)")
        self.console.print()

        choice = Prompt.ask("Choices", choices=["1", "2", "3"], default="1")

        provider_map = {
            "1": (AIProvider.OPENAI, "OpenAI"),
            "2": (AIProvider.ANTHROPIC, "Anthropic"),
            "3": (AIProvider.GOOGLE, "Google"),
        }
        provider, provider_name = provider_map[choice]

        self.console.print()
        self.console.print(f"[dim]{provider_name} Input API Key.[/dim]")
        self.console.print(
            f"[dim]You can get API Key from {provider_name} website.[/dim]"
        )
        self.console.print()

        api_key = Prompt.ask(f"{provider_name} API Key", password=True)

        # 형식 검증
        if not self.credential_service.validate_api_key_format(provider, api_key):
            self.console.print("[red]✗[/red] Incorrect format of API Key.")
            return False

        # 저장
        try:
            credential = self.credential_service.save_credential(
                provider=provider,
                api_key=api_key,
                name=None,
            )
            self.console.print(
                f"[green]✓[/green] {provider_name} API saved successfully!"
            )
            self.console.print(f"[dim]Maked Key: {credential.mask_api_key()}[/dim]")
            return True
        except ValueError as e:
            self.console.print(f"[red]✗[/red] error: {e}")
            return False

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
        """API 키 관리 메뉴"""
        self.console.print()
        self.console.print(
            Panel.fit(
                "[bold cyan]API Key Management[/bold cyan]",
                border_style="cyan",
            )
        )
        self.console.print()

        # 등록된 API 키 목록 표시
        all_credentials = self.credential_service.list_all_credentials()

        if not all_credentials:
            self.console.print("[yellow]There is not reigstered API Key.[/yellow]")
            return

        table = Table(title="Registered API Keys")
        table.add_column("Default", justify="center", style="cyan")
        table.add_column("Provider", style="magenta")
        table.add_column("API Key", style="green")
        table.add_column("Name", style="white")

        for cred in all_credentials:
            table.add_row(
                "⭐" if cred.is_default else "",
                cred.provider.value,
                cred.mask_api_key(),
                cred.name or "-",
            )

        self.console.print(table)
        self.console.print()

        # 관리 옵션
        self.console.print("[bold]Options:[/bold]")
        self.console.print("  1. Add new API Key")
        self.console.print("  2. Change default AI")
        self.console.print("  3. Delete API Key")
        self.console.print("  4. Back to main menu")
        self.console.print()

        choice = Prompt.ask("Choice", choices=["1", "2", "3", "4"], default="4")

        if choice == "1":
            self._setup_api_key()
        elif choice == "2":
            self._change_default_ai()
        elif choice == "3":
            self._delete_api_key()
        elif choice == "4":
            self._show_menu()

    def _change_default_ai(self):
        """기본 AI 변경"""
        self.console.print()
        self.console.print("[bold]Change default AI:[/bold]")

        all_credentials = self.credential_service.list_all_credentials()
        choices = []
        provider_map = {}

        for i, cred in enumerate(all_credentials, 1):
            mark = "⭐ " if cred.is_default else "   "
            self.console.print(f"  {i}. {mark}{cred.provider.value}")
            choices.append(str(i))
            provider_map[str(i)] = cred.provider

        self.console.print()
        choice = Prompt.ask("Select", choices=choices)

        provider = provider_map[choice]
        try:
            self.credential_service.set_default_provider(provider)
            self.console.print(f"[green]✓[/green] Set {provider.value} as default AI.")
        except ValueError as e:
            self.console.print(f"[red]✗[/red] 오류: {e}")

    def _delete_api_key(self):
        """API 키 삭제"""
        self.console.print()
        self.console.print("[bold]Delete API Key:[/bold]")

        all_credentials = self.credential_service.list_all_credentials()
        choices = []
        provider_map = {}

        for i, cred in enumerate(all_credentials, 1):
            self.console.print(f"  {i}. {cred.provider.value}")
            choices.append(str(i))
            provider_map[str(i)] = cred.provider

        self.console.print()
        choice = Prompt.ask("Select", choices=choices)

        provider = provider_map[choice]

        # 확인
        confirm = Prompt.ask(
            f"Do you want to delete {provider.value}? (yes/no)",
            choices=["yes", "no"],
            default="no",
        )

        if confirm == "yes":
            try:
                self.credential_service.delete_credential(provider)
                self.console.print(
                    f"[green]✓[/green] {provider.value} API Key deleted."
                )
            except ValueError as e:
                self.console.print(f"[red]✗[/red] error: {e}")

    def _manage_preferences(self):
        """사용자 설정 관리 메뉴 (PreferencesUI에 위임)"""
        self.preferences_ui.show_preferences_menu(on_back_callback=self._show_menu)
