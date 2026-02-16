"""CLI 명령어 인터페이스"""
import typer
from rich.console import Console

app = typer.Typer(help="Daily CLI - AI 일기 작성 도우미")
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """일기 앱을 시작합니다."""
    # 서브커맨드가 없으면 기본 동작 실행
    if ctx.invoked_subcommand is None:
        console.print("[bold green]hello world![/bold green]")


if __name__ == "__main__":
    app()
