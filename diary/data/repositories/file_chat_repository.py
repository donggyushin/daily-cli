"""파일 시스템 기반 채팅 저장소 구현"""

import json
from pathlib import Path
from typing import Optional, List

from diary.domain.interfaces.chat_repository import ChatRepositoryInterface
from diary.domain.entities.chat_session import ChatSession


class FileSystemChatRepository(ChatRepositoryInterface):
    """
    채팅 세션을 JSON 파일로 저장하는 구현체

    파일 구조:
    - data/chats/{session_id}.json : 각 세션 데이터
    - data/chats/active_session.json : 현재 활성 세션 ID
    """

    def __init__(self, data_dir: Path = Path("data/chats")):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.active_session_file = self.data_dir / "active_session.json"

    def save_session(self, session: ChatSession) -> None:
        """세션을 JSON 파일로 저장"""
        session_file = self.data_dir / f"{session.session_id}.json"

        try:
            # 세션 데이터 저장
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)

            # 활성 세션인 경우 active_session.json 업데이트
            if session.is_active:
                with open(self.active_session_file, "w", encoding="utf-8") as f:
                    json.dump({"session_id": session.session_id}, f, ensure_ascii=False)
            else:
                # 비활성화된 세션이 현재 활성 세션이면 active_session.json 제거
                if self.active_session_file.exists():
                    with open(self.active_session_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("session_id") == session.session_id:
                            self.active_session_file.unlink()

        except (UnicodeEncodeError, TypeError) as e:
            print(f"Warning: Failed to save session {session.session_id}: {e}")
            # 손상된 파일 삭제
            if session_file.exists():
                session_file.unlink()

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """특정 세션 조회"""
        session_file = self.data_dir / f"{session_id}.json"

        if not session_file.exists():
            return None

        try:
            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return ChatSession.from_dict(data)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(e)
            # JSON 파일이 손상된 경우 None 반환하고 파일 삭제
            print(f"Warning: Corrupted session file {session_id}, removing it.")
            session_file.unlink()
            return None

    def get_active_session(self) -> Optional[ChatSession]:
        """현재 활성화된 세션 반환"""
        if not self.active_session_file.exists():
            return None

        try:
            with open(self.active_session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                session_id = data.get("session_id")
                if session_id:
                    return self.get_session(session_id)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # active_session.json이 손상된 경우 파일 삭제
            print(f"Warning: Corrupted active_session.json, removing it.")
            self.active_session_file.unlink()

        return None

    def list_sessions(self, limit: int = 10) -> List[ChatSession]:
        """세션 목록 조회 (최신순)"""
        session_files = sorted(
            self.data_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True
        )

        sessions = []
        for session_file in session_files:
            # active_session.json은 제외
            if session_file.name == "active_session.json":
                continue

            if len(sessions) >= limit:
                break

            with open(session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                sessions.append(ChatSession.from_dict(data))

        return sessions

    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        session_file = self.data_dir / f"{session_id}.json"

        if not session_file.exists():
            return False

        # 활성 세션이면 active_session.json도 제거
        if self.active_session_file.exists():
            with open(self.active_session_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("session_id") == session_id:
                    self.active_session_file.unlink()

        # 세션 파일 삭제
        session_file.unlink()
        return True
