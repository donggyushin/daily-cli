"""CLI 명령어 인터페이스"""

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

app = typer.Typer(help="Daily CLI - AI 일기 작성 도우미")
console = Console()


def write():
    """일기 작성 시작"""
    console.print("[bold green]Start Write[/bold green]")


def menu():
    # 환영 메시지
    console.print(
        Panel.fit(
            "[bold cyan]Daily CLI - AI Diary Write Assistant[/bold cyan]",
            border_style="cyan",
        )
    )
    console.print()

    # 선택지 표시
    console.print("[bold]What do you want to do?[/bold]")
    console.print("1. Write Diary")
    console.print()

    # 사용자 선택 받기
    choice = Prompt.ask("Choice", choices=["1"], default="1")

    # 선택에 따라 실행
    if choice == "1":
        write()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """일기 앱을 시작합니다."""
    # 서브커맨드가 없으면 기본 동작 실행
    if ctx.invoked_subcommand is None:
        menu()


if __name__ == "__main__":
    app()
