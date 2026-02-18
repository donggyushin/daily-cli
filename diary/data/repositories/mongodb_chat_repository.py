"""
MongoDB 기반 채팅 저장소 구현체

아키텍처:
- Domain Layer의 ChatRepositoryInterface를 구현
- MongoDB를 이용한 채팅 세션 영속화
- 의존성 역전 원칙(DIP) 적용
"""

import os
from datetime import datetime
from typing import Optional, List
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from diary.domain.entities import ChatSession, ChatMessage, MessageRole
from diary.domain.interfaces import ChatRepositoryInterface


class MongoDBChatRepository(ChatRepositoryInterface):
    """MongoDB를 사용한 채팅 저장소 구현체"""

    def __init__(
        self,
        host: str = "mongodb",
        port: int = 27017,
        username: str = "admin",
        password: str = "admin123",
        database: str = "daily_diary",
    ):
        """
        MongoDB 연결 초기화

        Args:
            host: MongoDB 호스트 (기본: mongodb - Docker Compose 서비스명)
            port: MongoDB 포트 (기본: 27017)
            username: 사용자명
            password: 비밀번호
            database: 데이터베이스명
        """
        # 환경 변수 우선 사용 (Docker Compose 환경 지원)
        self.host = os.getenv("MONGODB_HOST", host)
        self.port = int(os.getenv("MONGODB_PORT", port))
        self.username = os.getenv("MONGODB_USERNAME", username)
        self.password = os.getenv("MONGODB_PASSWORD", password)
        self.database_name = os.getenv("MONGODB_DATABASE", database)

        # MongoDB 연결
        connection_string = (
            f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
        )
        self.client: MongoClient = MongoClient(connection_string)
        self.db: Database = self.client[self.database_name]
        self.sessions: Collection = self.db["chat_sessions"]
        self.active_session: Collection = self.db["active_session"]

        # 인덱스 생성 (성능 최적화)
        self._create_indexes()

    def _create_indexes(self) -> None:
        """MongoDB 인덱스 생성 (성능 최적화)"""
        # session_id 고유 인덱스
        self.sessions.create_index("session_id", unique=True)
        # created_at 인덱스 (최신순 정렬용)
        self.sessions.create_index("created_at", background=True)
        # is_active 인덱스 (활성 세션 조회용)
        self.sessions.create_index("is_active", background=True)

    def save_session(self, session: ChatSession) -> None:
        """채팅 세션 저장"""
        session_doc = {
            "session_id": session.session_id,
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in session.messages
            ],
            "created_at": session.created_at.isoformat(),
            "is_active": session.is_active,
        }

        # Upsert (없으면 생성, 있으면 업데이트)
        self.sessions.update_one(
            {"session_id": session.session_id},
            {"$set": session_doc},
            upsert=True,
        )

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """세션 ID로 채팅 세션 조회"""
        doc = self.sessions.find_one({"session_id": session_id})
        if not doc:
            return None

        return self._doc_to_session(doc)

    def get_active_session_id(self) -> Optional[str]:
        """현재 활성 세션 ID 조회"""
        doc = self.active_session.find_one({"type": "active"})
        if not doc:
            return None
        return doc.get("session_id")

    def set_active_session_id(self, session_id: Optional[str]) -> None:
        """활성 세션 ID 설정"""
        if session_id is None:
            # 활성 세션 삭제
            self.active_session.delete_one({"type": "active"})
        else:
            # 활성 세션 업데이트
            self.active_session.update_one(
                {"type": "active"},
                {"$set": {"session_id": session_id, "updated_at": datetime.now().isoformat()}},
                upsert=True,
            )

    def list_sessions(self, limit: int = 10) -> List[ChatSession]:
        """채팅 세션 목록 조회 (최신순)"""
        cursor = self.sessions.find().sort("created_at", -1).limit(limit)
        return [self._doc_to_session(doc) for doc in cursor]

    def delete_session(self, session_id: str) -> bool:
        """채팅 세션 삭제"""
        result = self.sessions.delete_one({"session_id": session_id})
        return result.deleted_count > 0

    def _doc_to_session(self, doc: dict) -> ChatSession:
        """MongoDB 문서를 ChatSession 엔티티로 변환"""
        messages = [
            ChatMessage(
                role=MessageRole(msg["role"]),
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"]),
            )
            for msg in doc.get("messages", [])
        ]

        return ChatSession(
            session_id=doc["session_id"],
            messages=messages,
            created_at=datetime.fromisoformat(doc["created_at"]),
            is_active=doc.get("is_active", True),
        )

    def close(self) -> None:
        """MongoDB 연결 종료 (리소스 정리)"""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager 지원"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager 종료 시 연결 닫기"""
        self.close()
