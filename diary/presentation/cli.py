"""CLI 명령어 인터페이스"""
import typer
from rich.console import Console

app = typer.Typer(help="Daily CLI - AI 일기 작성 도우미")
console = Console()


@app.command()
def main():
    """일기 앱을 시작합니다."""
    console.print("[bold green]hello world![/bold green]")


if __name__ == "__main__":
    app()
