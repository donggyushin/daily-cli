#!/usr/bin/env python3
"""
파일 시스템 데이터를 MongoDB로 마이그레이션하는 스크립트

사용법:
    python scripts/migrate_to_mongodb.py
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from diary.data.repositories import FileSystemChatRepository, MongoDBChatRepository


def migrate_chat_data():
    """채팅 데이터 마이그레이션"""
    print("=== 채팅 데이터 마이그레이션 시작 ===\n")

    # 기존 파일 시스템 저장소
    file_repo = FileSystemChatRepository()
    print("✓ 파일 시스템 저장소 연결 완료")

    # MongoDB 저장소
    try:
        mongo_repo = MongoDBChatRepository()
        print("✓ MongoDB 연결 완료\n")
    except Exception as e:
        print(f"✗ MongoDB 연결 실패: {e}")
        print("\n힌트:")
        print("1. MongoDB가 실행 중인지 확인: docker compose ps")
        print("2. 환경 변수 확인: .env 파일 존재 여부")
        print("3. MongoDB 시작: make up-db")
        return

    # 세션 목록 가져오기
    sessions = file_repo.list_sessions(limit=100)
    if not sessions:
        print("마이그레이션할 세션이 없습니다.")
        return

    print(f"발견한 세션 수: {len(sessions)}\n")

    # 마이그레이션 진행
    success_count = 0
    fail_count = 0

    for i, session in enumerate(sessions, 1):
        try:
            # MongoDB에 저장
            mongo_repo.save_session(session)
            print(f"[{i}/{len(sessions)}] ✓ {session.session_id[:16]}... (메시지 {len(session.messages)}개)")
            success_count += 1
        except Exception as e:
            print(f"[{i}/{len(sessions)}] ✗ {session.session_id[:16]}... 실패: {e}")
            fail_count += 1

    # 활성 세션 마이그레이션
    print("\n활성 세션 마이그레이션 중...")
    active_session_id = file_repo.get_active_session_id()
    if active_session_id:
        try:
            mongo_repo.set_active_session_id(active_session_id)
            print(f"✓ 활성 세션 설정 완료: {active_session_id[:16]}...")
        except Exception as e:
            print(f"✗ 활성 세션 설정 실패: {e}")

    # 결과 요약
    print("\n=== 마이그레이션 완료 ===")
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    print(f"총 {len(sessions)}개 세션 처리")

    # 연결 종료
    mongo_repo.close()


def main():
    """메인 함수"""
    print("Daily CLI - MongoDB 마이그레이션 도구\n")

    try:
        migrate_chat_data()
    except KeyboardInterrupt:
        print("\n\n마이그레이션이 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
