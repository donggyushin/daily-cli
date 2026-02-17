"""AI 클라이언트 인터페이스 - Domain이 정의, Data가 구현"""

from abc import ABC, abstractmethod
from typing import List


class AIClientInterface(ABC):
    """AI API 호출 인터페이스 (OpenAI, Anthropic, Google 등)"""

    @abstractmethod
    def chat(self, messages: List[dict]) -> str:
        """
        대화 히스토리를 받아 AI 응답 생성

        Args:
            messages: [{"role": "user", "content": "..."}, ...] 형식의 대화 기록

        Returns:
            AI 응답 텍스트

        Raises:
            Exception: AI API 호출 실패 시
        """
        pass
