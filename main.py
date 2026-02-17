"""애플리케이션 진입점 (Dependency Injection 조립)

모든 레이어의 의존성을 조립하고 앱을 시작합니다.
이 파일만 모든 레이어를 알고 있습니다.
"""

import typer

from diary.data.repositories import (
    FileSystemCredentialRepository,
    FileSystemUserPreferencesRepository,
    FileSystemWritingStyleExamplesRepository,
    FileSystemChatRepository,
    OpenAIClient,
    AnthropicClient,
    GoogleAIClient,
)
from diary.domain.services import CredentialService, UserPreferencesService, ChatService
from diary.domain.entities import AIProvider
from diary.presentation.cli import DiaryApp

app = typer.Typer()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Daily CLI - AI 일기 작성 도우미

    레이어드 아키텍처 + 의존성 주입 패턴:
    1. Data Layer 구현체 생성
    2. Domain Layer 서비스에 주입
    3. Presentation Layer에 주입
    """
    if ctx.invoked_subcommand is None:
        # 의존성 조립 (Dependency Assembly)
        # Data Layer - Repository 구현체
        credential_repo = FileSystemCredentialRepository()
        preferences_repo = FileSystemUserPreferencesRepository()
        examples_repo = FileSystemWritingStyleExamplesRepository()

        # Domain Layer - Business Logic (인터페이스에만 의존)
        credential_service = CredentialService(credential_repo)
        preferences_service = UserPreferencesService(preferences_repo, examples_repo)

        # AI Client 선택 (기본 AI 기준)
        default_ai = credential_service.get_default_credential()
        if default_ai:
            if default_ai.provider == AIProvider.OPENAI:
                ai_client = OpenAIClient(api_key=default_ai.api_key)
            elif default_ai.provider == AIProvider.ANTHROPIC:
                ai_client = AnthropicClient(api_key=default_ai.api_key)
            elif default_ai.provider == AIProvider.GOOGLE:
                ai_client = GoogleAIClient(api_key=default_ai.api_key)
            else:
                ai_client = None

            # Chat Repository 및 Chat Service 생성
            chat_repo = FileSystemChatRepository()
            chat_service = ChatService(
                chat_repo=chat_repo,
                ai_client=ai_client,
                preferences_service=preferences_service,
            )
        else:
            # AI 설정이 없으면 None (첫 실행 시)
            chat_service = None

        # Presentation Layer - CLI (Domain에만 의존)
        diary_app = DiaryApp(credential_service, preferences_service, chat_service)

        # 실행
        diary_app.run()


if __name__ == "__main__":
    app()
