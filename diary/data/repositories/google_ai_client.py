"""Google Gemini API 클라이언트 구현"""

from typing import List
import google.generativeai as genai

from diary.domain.interfaces.ai_client import AIClientInterface


class GoogleAIClient(AIClientInterface):
    """Google Gemini 모델을 사용하는 AI 클라이언트"""

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        """
        Args:
            api_key: Google AI API 키
            model: 사용할 모델 (기본: gemini-1.5-flash)
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def chat(self, messages: List[dict]) -> str:
        """
        Google Gemini API 호출

        Args:
            messages: [{"role": "user", "content": "..."}, ...]

        Returns:
            AI 응답 텍스트

        Raises:
            Exception: API 호출 실패 시
        """
        try:
            # Gemini API는 system 메시지를 별도로 처리
            system_instruction = None
            chat_history = []
            last_user_message = None

            for msg in messages:
                # UTF-8 인코딩 문제 방지: 서로게이트 문자 제거
                content = msg["content"]
                if isinstance(content, str):
                    content = content.encode('utf-8', errors='ignore').decode('utf-8')

                if msg["role"] == "system":
                    system_instruction = content
                elif msg["role"] == "user":
                    last_user_message = content
                elif msg["role"] == "assistant":
                    if last_user_message:
                        chat_history.append({
                            "role": "user",
                            "parts": [last_user_message]
                        })
                        last_user_message = None
                    chat_history.append({
                        "role": "model",
                        "parts": [content]
                    })

            # 채팅 세션 시작
            chat = self.model.start_chat(history=chat_history)

            # 시스템 지시사항을 첫 메시지에 포함
            if system_instruction and not chat_history:
                last_user_message = f"{system_instruction}\n\n{last_user_message}"

            # 메시지 전송
            response = chat.send_message(last_user_message)
            return response.text

        except Exception as e:
            raise Exception(f"Google AI API 호출 실패: {str(e)}")
