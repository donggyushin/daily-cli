"""채팅 UI 컴포넌트"""

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt

from diary.domain.services.chat_service import ChatService


class ChatUI:
    """채팅 대화 UI - 단일 책임 원칙 적용"""

    def __init__(self, chat_service: ChatService, console: Console):
        """
        Args:
            chat_service: 채팅 비즈니스 로직
            console: Rich Console 객체
        """
        self.chat_service = chat_service
        self.console = console

    def start_chat(self, on_back_callback):
        """
        대화형 채팅 시작

        Args:
            on_back_callback: 뒤로가기 콜백 함수
        """
        self.console.clear()
        self.console.print(Panel(
            "[bold cyan]일기 채팅[/bold cyan]\n\n"
            "AI와 대화하며 오늘 하루를 기록해보세요.\n"
            "종료: 'quit', 'exit', '그만'",
            border_style="cyan"
        ))

        # 새 세션 시작 또는 기존 세션 이어가기
        session = self.chat_service.get_current_session()

        if session:
            self.console.print("\n[yellow]이전 대화를 이어갑니다.[/yellow]\n")
            # 최근 대화 몇 개 표시
            self._display_recent_messages(session)
        else:
            self.console.print("\n[green]새로운 대화를 시작합니다.[/green]\n")
            session = self.chat_service.start_new_session()
            # AI 첫 인사 표시
            last_message = session.messages[-1]
            self._display_ai_message(last_message.content)

        # 대화 루프
        while True:
            # 사용자 입력
            try:
                user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]")
                # UTF-8 인코딩 문제 방지: 서로게이트 문자 제거
                user_input = user_input.encode('utf-8', errors='ignore').decode('utf-8')
            except (KeyboardInterrupt, EOFError):
                on_back_callback()
                return

            # 종료 명령어 확인
            if user_input.lower() in ["quit", "exit", "그만", "종료"]:
                self._end_chat_session(on_back_callback)
                return

            # 빈 입력 무시
            if not user_input.strip():
                continue

            # AI 응답 받기
            try:
                self.console.print("\n[dim]AI가 생각 중...[/dim]")
                ai_response, is_diary = self.chat_service.send_message(user_input)

                # 일기가 생성된 경우 특별 처리
                if is_diary:
                    self._display_diary(ai_response)
                else:
                    self._display_ai_message(ai_response)

            except Exception as e:
                self.console.print(f"\n[red]오류 발생: {str(e)}[/red]")
                self.console.print("[yellow]다시 시도해주세요.[/yellow]")

    def _display_ai_message(self, content: str):
        """AI 메시지 예쁘게 표시"""
        self.console.print()
        self.console.print(Panel(
            Markdown(content),
            title="[bold green]AI Assistant[/bold green]",
            border_style="green",
            padding=(1, 2)
        ))

    def _display_diary(self, content: str):
        """일기 생성 시 특별하게 표시"""
        # [DIARY_START]와 [DIARY_END] 마커 제거
        diary_content = content
        if "[DIARY_START]" in content and "[DIARY_END]" in content:
            start_idx = content.find("[DIARY_START]") + len("[DIARY_START]")
            end_idx = content.find("[DIARY_END]")
            diary_content = content[start_idx:end_idx].strip()

        self.console.print()
        self.console.print(Panel(
            Markdown(diary_content),
            title="[bold yellow]📖 일기가 작성되었습니다![/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        ))
        self.console.print("\n[green]✓ 일기 초안이 완성되었습니다![/green]")
        self.console.print("[dim]계속 대화하거나 'quit'로 종료하세요.[/dim]")

    def _display_recent_messages(self, session, count: int = 3):
        """최근 메시지 몇 개 표시"""
        recent_messages = session.messages[-count * 2:] if len(session.messages) > count * 2 else session.messages

        for msg in recent_messages:
            if msg.role.value == "user":
                self.console.print(f"\n[bold cyan]You:[/bold cyan] {msg.content}")
            elif msg.role.value == "assistant":
                self._display_ai_message(msg.content)

    def _end_chat_session(self, on_back_callback):
        """채팅 세션 종료"""
        self.console.print("\n[yellow]대화를 종료합니다.[/yellow]")

        # 세션 종료
        success = self.chat_service.end_current_session()
        if success:
            self.console.print("[green]대화 내용이 저장되었습니다.[/green]")
        else:
            self.console.print("[yellow]저장할 대화가 없습니다.[/yellow]")

        self.console.input("\n[dim]Enter를 눌러 계속...[/dim]")
        on_back_callback()
