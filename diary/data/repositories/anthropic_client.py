"""Anthropic Claude API 클라이언트 구현"""

from typing import List
from anthropic import Anthropic
from anthropic.types import TextBlock

from diary.domain.interfaces.ai_client import AIClientInterface


class AnthropicClient(AIClientInterface):
    """Anthropic Claude 모델을 사용하는 AI 클라이언트"""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5-20250929"):
        """
        Args:
            api_key: Anthropic API 키
            model: 사용할 모델 (기본: claude-sonnet-4-5, Smart and general)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

    def chat(self, messages: List[dict]) -> str:
        """
        Anthropic Messages API 호출

        Args:
            messages: [{"role": "user", "content": "..."}, ...]

        Returns:
            AI 응답 텍스트

        Raises:
            Exception: API 호출 실패 시
        """
        try:
            # Anthropic API는 system 메시지를 별도 파라미터로 받음
            system_message = None
            conversation_messages = []

            for msg in messages:
                # UTF-8 인코딩 문제 방지: 서로게이트 문자 제거
                content = msg["content"]
                if isinstance(content, str):
                    content = content.encode("utf-8", errors="ignore").decode("utf-8")

                if msg["role"] == "system":
                    system_message = content
                else:
                    conversation_messages.append(
                        {"role": msg["role"], "content": content}
                    )

            # API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.7,
                system=system_message if system_message else "",
                messages=conversation_messages,
            )

            # TextBlock만 추출 (타입 안전성)
            for block in response.content:
                if isinstance(block, TextBlock):
                    return block.text

            # TextBlock이 없으면 빈 문자열 반환
            return ""

        except Exception as e:
            raise Exception(f"Anthropic API 호출 실패: {str(e)}")
