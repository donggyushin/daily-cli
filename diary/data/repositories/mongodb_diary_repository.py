"""
MongoDB 기반 일기 저장소 구현체

아키텍처:
- Domain Layer의 DiaryRepositoryInterface를 구현
- MongoDB를 이용한 일기 영속화
- Cursor 기반 페이지네이션 (효율적인 대량 데이터 처리)
- 의존성 역전 원칙(DIP) 적용
"""

import os
import base64
from datetime import date, datetime
from typing import Optional, List, Tuple
from uuid import uuid4
from pymongo import MongoClient, DESCENDING
from pymongo.database import Database
from pymongo.collection import Collection

from diary.domain.entities import Diary
from diary.domain.interfaces import DiaryRepositoryInterface


class MongoDBDiaryRepository(DiaryRepositoryInterface):
    """MongoDB를 사용한 일기 저장소 구현체"""

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
        self.diaries: Collection = self.db["diaries"]

        # 인덱스 생성 (성능 최적화)
        self._create_indexes()

    def _create_indexes(self) -> None:
        """MongoDB 인덱스 생성 (성능 최적화)"""
        # diary_date 고유 인덱스 (하루에 하나의 일기만)
        self.diaries.create_index("diary_date", unique=True)
        # diary_id 고유 인덱스
        self.diaries.create_index("diary_id", unique=True)
        # 날짜 기준 정렬용 (최신순)
        self.diaries.create_index([("diary_date", DESCENDING)])
        # 생성 시각 정렬용 (같은 날짜일 경우 대비)
        self.diaries.create_index([("created_at", DESCENDING)])

    def save(self, diary: Diary) -> Diary:
        """일기 저장 (생성 또는 수정)"""
        # diary_id가 없으면 새로 생성 (UUID)
        if not diary.diary_id:
            diary.diary_id = str(uuid4())
            diary.created_at = datetime.now()

        # 수정 시각 갱신
        diary.updated_at = datetime.now()

        # diary_date가 datetime 타입이면 date로 변환 (안전장치)
        diary_date_value = diary.diary_date
        if isinstance(diary_date_value, datetime):
            diary_date_value = diary_date_value.date()

        # created_at, updated_at이 None인 경우 현재 시각으로 설정 (안전장치)
        if not diary.created_at:
            diary.created_at = datetime.now()
        if not diary.updated_at:
            diary.updated_at = datetime.now()

        # MongoDB 문서로 변환
        diary_doc = {
            "diary_id": diary.diary_id,
            "diary_date": diary_date_value.isoformat(),
            "content": diary.content,
            "created_at": diary.created_at.isoformat(),
            "updated_at": diary.updated_at.isoformat(),
        }

        # Upsert (diary_id 기준으로 업데이트 또는 생성)
        self.diaries.update_one(
            {"diary_id": diary.diary_id},
            {"$set": diary_doc},
            upsert=True,
        )

        return diary

    def get_by_date(self, diary_date: date) -> Optional[Diary]:
        """특정 날짜의 일기 조회"""
        doc = self.diaries.find_one({"diary_date": diary_date.isoformat()})
        if not doc:
            return None

        return self._doc_to_diary(doc)

    def get_by_id(self, diary_id: str) -> Optional[Diary]:
        """ID로 일기 조회"""
        doc = self.diaries.find_one({"diary_id": diary_id})
        if not doc:
            return None

        return self._doc_to_diary(doc)

    def list_diaries(
        self,
        cursor: Optional[str] = None,
        limit: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Diary], Optional[str]]:
        """
        일기 목록 조회 (Cursor 기반 페이지네이션)

        Cursor 형식: base64(diary_date|created_at)
        정렬 순서: diary_date DESC, created_at DESC (최신순)
        """
        # 필터 조건 구성
        query = {}

        # 날짜 범위 필터
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date.isoformat()
            if end_date:
                date_filter["$lte"] = end_date.isoformat()
            query["diary_date"] = date_filter

        # Cursor 디코딩 (이전 페이지의 마지막 항목)
        if cursor:
            try:
                decoded = base64.b64decode(cursor).decode("utf-8")
                cursor_date, cursor_created = decoded.split("|")

                # Cursor 이후의 데이터만 조회
                query["$or"] = [
                    {"diary_date": {"$lt": cursor_date}},
                    {
                        "diary_date": cursor_date,
                        "created_at": {"$lt": cursor_created},
                    },
                ]
            except (ValueError, UnicodeDecodeError):
                # Cursor 파싱 실패 시 무시하고 처음부터 조회
                pass

        # MongoDB 쿼리 실행 (최신순 정렬, limit+1개 조회)
        cursor_obj = (
            self.diaries.find(query)
            .sort([("diary_date", DESCENDING), ("created_at", DESCENDING)])
            .limit(limit + 1)
        )

        # 결과 변환
        results = [self._doc_to_diary(doc) for doc in cursor_obj]

        # 다음 커서 생성
        next_cursor = None
        if len(results) > limit:
            # limit+1개를 조회했으므로, 다음 페이지가 있음
            results = results[:limit]  # limit개만 반환
            last_diary = results[-1]

            # 다음 커서 생성 (마지막 항목의 날짜와 생성시각)
            # created_at이 None인 경우 현재 시각 사용 (안전장치)
            created_at_value = last_diary.created_at or datetime.now()
            cursor_value = f"{last_diary.diary_date.isoformat()}|{created_at_value.isoformat()}"
            next_cursor = base64.b64encode(cursor_value.encode("utf-8")).decode("utf-8")

        return results, next_cursor

    def delete(self, diary_id: str) -> bool:
        """일기 삭제"""
        result = self.diaries.delete_one({"diary_id": diary_id})
        return result.deleted_count > 0

    def exists_on_date(self, diary_date: date) -> bool:
        """특정 날짜에 일기가 존재하는지 확인"""
        count = self.diaries.count_documents({"diary_date": diary_date.isoformat()})
        return count > 0

    def _doc_to_diary(self, doc: dict) -> Diary:
        """MongoDB 문서를 Diary 엔티티로 변환"""
        # diary_date 파싱 (datetime 형식도 처리)
        diary_date_str = doc["diary_date"]
        if "T" in diary_date_str:
            # datetime 형식인 경우 (예: 2026-02-18T12:36:28.786555)
            diary_date_value = datetime.fromisoformat(diary_date_str).date()
        else:
            # date 형식인 경우 (예: 2026-02-18)
            diary_date_value = date.fromisoformat(diary_date_str)

        return Diary(
            diary_id=doc["diary_id"],
            diary_date=diary_date_value,
            content=doc["content"],
            created_at=datetime.fromisoformat(doc["created_at"]),
            updated_at=datetime.fromisoformat(doc["updated_at"]),
        )

    def close(self) -> None:
        """MongoDB 연결 종료 (리소스 정리)"""
        if self.client:
            self.client.close()

    def __enter__(self):
        """Context manager 지원"""
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager 종료 시 연결 닫기"""
        self.close()
