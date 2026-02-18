"""API Key 관리 UI"""

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table

from diary.domain.entities import AIProvider
from diary.domain.services import CredentialService


class ApiKeyUI:
    """API Key 관리 UI

    AI 서비스 인증 정보(API Key)를 관리하는 UI를 제공합니다.
    """

    def __init__(self, credential_service: CredentialService, console: Console):
        """
        Args:
            credential_service: AI 인증 정보 관리 서비스 (Domain Layer)
            console: Rich Console 인스턴스
        """
        self.credential_service = credential_service
        self.console = console
        self._on_back_callback = None  # 뒤로 가기 콜백 저장

    def setup_api_key(self) -> bool:
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

    def show_management_menu(self, on_back_callback=None):
        """API 키 관리 메뉴 표시

        Args:
            on_back_callback: 뒤로 가기 시 호출할 콜백 함수 (None이면 기존 저장된 콜백 사용)
        """
        # 새로운 콜백이 전달되면 저장
        if on_back_callback is not None:
            self._on_back_callback = on_back_callback

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
            self.setup_api_key()
            # 다시 관리 메뉴로
            self.show_management_menu()
        elif choice == "2":
            self.change_default_ai()
            # 다시 관리 메뉴로
            self.show_management_menu()
        elif choice == "3":
            self.delete_api_key()
            # 다시 관리 메뉴로
            self.show_management_menu()
        elif choice == "4":
            if self._on_back_callback:
                self._on_back_callback()

    def change_default_ai(self):
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

    def delete_api_key(self):
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
            choices=["y", "n"],
            default="n",
        )

        if confirm == "y":
            try:
                self.credential_service.delete_credential(provider)
                self.console.print(
                    f"[green]✓[/green] {provider.value} API Key deleted."
                )
            except ValueError as e:
                self.console.print(f"[red]✗[/red] error: {e}")
