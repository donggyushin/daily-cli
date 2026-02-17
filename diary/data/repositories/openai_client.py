"""OpenAI API 클라이언트 구현"""

from typing import List
from openai import OpenAI

from diary.domain.interfaces.ai_client import AIClientInterface


class OpenAIClient(AIClientInterface):
    """OpenAI GPT 모델을 사용하는 AI 클라이언트"""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Args:
            api_key: OpenAI API 키
            model: 사용할 모델 (기본: gpt-4o-mini, 비용 효율적)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def chat(self, messages: List[dict]) -> str:
        """
        OpenAI Chat Completion API 호출

        Args:
            messages: [{"role": "user", "content": "..."}, ...]

        Returns:
            AI 응답 텍스트

        Raises:
            Exception: API 호출 실패 시
        """
        try:
            # UTF-8 인코딩 문제 방지: 서로게이트 문자 제거
            cleaned_messages = []
            for msg in messages:
                content = msg["content"]
                if isinstance(content, str):
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')

                cleaned_messages.append({
                    "role": msg["role"],
                    "content": content
                })

            response = self.client.chat.completions.create(
                model=self.model,
                messages=cleaned_messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content

        except Exception as e:
            raise Exception(f"OpenAI API 호출 실패: {str(e)}")
