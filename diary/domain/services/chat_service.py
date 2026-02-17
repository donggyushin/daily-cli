"""채팅 비즈니스 로직 서비스"""

from typing import Optional
import uuid

from diary.domain.entities.chat_session import ChatSession
from diary.domain.entities.chat_message import MessageRole
from diary.domain.interfaces.chat_repository import ChatRepositoryInterface
from diary.domain.interfaces.ai_client import AIClientInterface
from diary.domain.services.user_preferences_service import UserPreferencesService


class ChatService:
    """채팅 세션 관리 및 AI 대화 로직"""

    def __init__(
        self,
        chat_repo: ChatRepositoryInterface,
        ai_client: AIClientInterface,
        preferences_service: UserPreferencesService
    ):
        """
        Args:
            chat_repo: 채팅 저장소 (인터페이스)
            ai_client: AI 클라이언트 (인터페이스)
            preferences_service: 사용자 설정 서비스
        """
        self.chat_repo = chat_repo
        self.ai_client = ai_client
        self.preferences_service = preferences_service

    def start_new_session(self) -> ChatSession:
        """
        새 채팅 세션 시작

        Returns:
            생성된 ChatSession (AI 첫 인사 포함)
        """
        session_id = str(uuid.uuid4())
        session = ChatSession(session_id=session_id)

        # 시스템 프롬프트 추가 (AI의 역할 정의)
        system_prompt = self._get_system_prompt()
        session.add_message(MessageRole.SYSTEM, system_prompt)

        # AI의 첫 인사 생성
        greeting = self._get_ai_greeting(session)
        # UTF-8 정제
        greeting = greeting.encode('utf-8', errors='ignore').decode('utf-8')
        session.add_message(MessageRole.ASSISTANT, greeting)

        # 세션 저장
        self.chat_repo.save_session(session)

        return session

    def send_message(self, user_message: str) -> str:
        """
        사용자 메시지 전송 → AI 응답 받기

        Args:
            user_message: 사용자 입력 메시지

        Returns:
            AI 응답 텍스트

        Raises:
            Exception: AI API 호출 실패 시
        """
        # UTF-8 인코딩 문제 방지: 서로게이트 문자 제거
        user_message = user_message.encode('utf-8', errors='ignore').decode('utf-8')

        # 활성 세션 가져오기 (없으면 새로 생성)
        session = self.chat_repo.get_active_session()
        if not session:
            session = self.start_new_session()

        # 사용자 메시지 추가
        session.add_message(MessageRole.USER, user_message)

        # AI 응답 생성 (Full Context 전달)
        conversation_history = session.get_conversation_history()
        ai_response = self.ai_client.chat(conversation_history)

        # AI 응답도 UTF-8 정제
        ai_response = ai_response.encode('utf-8', errors='ignore').decode('utf-8')

        # AI 응답 저장
        session.add_message(MessageRole.ASSISTANT, ai_response)

        # 세션 저장
        self.chat_repo.save_session(session)

        return ai_response

    def get_current_session(self) -> Optional[ChatSession]:
        """
        현재 활성 세션 조회

        Returns:
            활성 세션 또는 None
        """
        return self.chat_repo.get_active_session()

    def end_current_session(self) -> bool:
        """
        현재 세션 종료

        Returns:
            종료 성공 여부
        """
        session = self.chat_repo.get_active_session()
        if not session:
            return False

        session.end_session()
        self.chat_repo.save_session(session)
        return True

    def _get_system_prompt(self) -> str:
        """
        시스템 프롬프트 생성
        AI를 "일기 작성을 위한 친절한 인터뷰어"로 설정
        """
        # 사용자가 선택한 스타일의 상세한 설명 + 예시 문장 가져오기
        style_instruction = self.preferences_service.get_style_prompt_instruction()

        return f"""당신은 사용자의 하루를 듣고 일기를 작성하는 친절한 인터뷰어입니다.

목표:
1. 사용자와 자연스럽게 대화하며 하루 일과를 듣기
2. 구체적인 사건, 감정, 생각을 파악하기
3. 충분한 정보가 모이면 아래 스타일로 일기 초안 제안

일기 작성 스타일:
{style_instruction}

대화 스타일:
- 친근하고 공감적으로 대화
- 짧고 자연스러운 질문 (긴 설명 X)
- 사용자가 편하게 답변할 수 있도록 유도
- "오늘 어땠어요?", "그때 기분이 어땠나요?" 등 자연스러운 질문

중요:
- 사용자가 충분히 이야기했다고 판단되면, "오늘 대화를 바탕으로 일기를 작성해드릴까요?"라고 물어보세요.
- 항상 한국어로 대화하세요.
- 짧고 간결하게 한 번에 하나의 질문만 하세요.
"""

    def _get_ai_greeting(self, session: ChatSession) -> str:
        """
        AI의 첫 인사 생성

        Args:
            session: 현재 세션 (시스템 프롬프트 포함)

        Returns:
            AI 인사말
        """
        conversation_history = session.get_conversation_history()
        greeting_prompt = [
            *conversation_history,
            {"role": "user", "content": "대화를 시작해줘. 간단하고 친근하게 인사하고 오늘 하루에 대해 물어봐줘."}
        ]
        return self.ai_client.chat(greeting_prompt)
