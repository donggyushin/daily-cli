#!/usr/bin/env python3
"""
MongoDB Diary Repository 테스트 스크립트

사용법:
    python scripts/test_mongodb_diary.py
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from diary.data.repositories import MongoDBDiaryRepository
from diary.domain.services import DiaryService
from diary.domain.entities import Diary


def test_mongodb_diary():
    """MongoDB Diary Repository 테스트"""
    print("=== MongoDB Diary Repository 테스트 시작 ===\n")

    # MongoDB Repository 생성
    try:
        diary_repo = MongoDBDiaryRepository()
        print("✓ MongoDB 연결 완료\n")
    except Exception as e:
        print(f"✗ MongoDB 연결 실패: {e}")
        print("\n힌트:")
        print("1. MongoDB가 실행 중인지 확인: docker compose ps")
        print("2. 환경 변수 확인: .env 파일 존재 여부")
        print("3. MongoDB 시작: make up-db")
        return

    # DiaryService 생성
    diary_service = DiaryService(diary_repo)
    print("✓ DiaryService 생성 완료\n")

    # 테스트 1: 일기 작성
    print("📝 테스트 1: 일기 작성")
    try:
        today = date.today()
        diary1 = diary_service.create_diary(
            diary_date=today,
            content="오늘은 MongoDB Diary Repository를 구현했다. Cursor 기반 페이지네이션이 핵심이다."
        )
        print(f"✓ 일기 작성 완료: {diary1.diary_id}")
        print(f"  날짜: {diary1.get_formatted_date()}")
        print(f"  글자 수: {diary1.get_word_count()}자")
        print()
    except ValueError as e:
        print(f"⚠️  이미 오늘 일기가 존재합니다: {e}\n")

    # 테스트 2: 여러 날짜의 일기 작성
    print("📝 테스트 2: 여러 날짜의 일기 작성")
    test_diaries = [
        (today - timedelta(days=1), "어제는 Domain Layer를 설계했다."),
        (today - timedelta(days=2), "그저께는 MongoDB를 Docker에 추가했다."),
        (today - timedelta(days=3), "3일 전에는 프로젝트 구조를 정리했다."),
        (today - timedelta(days=4), "4일 전에는 AI 채팅 기능을 만들었다."),
        (today - timedelta(days=5), "5일 전에는 아키텍처를 고민했다."),
    ]

    for diary_date, content in test_diaries:
        try:
            diary = diary_service.create_diary(diary_date=diary_date, content=content)
            print(f"✓ {diary.get_formatted_date()}: {content[:30]}...")
        except ValueError:
            print(f"⚠️  {diary_date}: 이미 존재")

    print()

    # 테스트 3: 날짜로 조회
    print("🔍 테스트 3: 날짜로 조회")
    today_diary = diary_service.get_diary_by_date(today)
    if today_diary:
        print(f"✓ 오늘의 일기:")
        print(f"  {today_diary.get_formatted_date()}")
        print(f"  {today_diary.content}")
    else:
        print("✗ 오늘의 일기가 없습니다.")
    print()

    # 테스트 4: Cursor 기반 페이지네이션
    print("📄 테스트 4: Cursor 기반 페이지네이션")

    # 첫 페이지 (3개씩)
    print("\n첫 페이지 (limit=3):")
    diaries, next_cursor = diary_service.list_diaries(limit=3)
    for i, diary in enumerate(diaries, 1):
        print(f"  {i}. {diary.get_formatted_date()}: {diary.content[:40]}...")
    print(f"\n다음 커서: {next_cursor[:20] if next_cursor else 'None'}...")

    # 두 번째 페이지
    if next_cursor:
        print("\n두 번째 페이지 (limit=3):")
        diaries2, next_cursor2 = diary_service.list_diaries(cursor=next_cursor, limit=3)
        for i, diary in enumerate(diaries2, 1):
            print(f"  {i}. {diary.get_formatted_date()}: {diary.content[:40]}...")
        print(f"\n다음 커서: {next_cursor2[:20] if next_cursor2 else 'None'}...")

    print()

    # 테스트 5: 일기 수정
    print("✏️  테스트 5: 일기 수정")
    if today_diary:
        updated_diary = diary_service.update_diary_by_date(
            diary_date=today,
            new_content=today_diary.content + " 그리고 테스트도 성공했다!"
        )
        print(f"✓ 일기 수정 완료:")
        print(f"  {updated_diary.content}")
    print()

    # 테스트 6: 날짜 범위 필터링
    print("📅 테스트 6: 날짜 범위 필터링")
    start_date = today - timedelta(days=3)
    end_date = today
    diaries, _ = diary_service.list_diaries(
        start_date=start_date,
        end_date=end_date,
        limit=10
    )
    print(f"✓ {start_date} ~ {end_date} 기간의 일기: {len(diaries)}개")
    for diary in diaries:
        print(f"  - {diary.get_formatted_date()}")
    print()

    # 테스트 7: 일기 삭제 (선택적)
    print("🗑️  테스트 7: 일기 삭제 (마지막 테스트 일기만)")
    delete_date = today - timedelta(days=5)
    try:
        deleted = diary_service.delete_diary_by_date(delete_date)
        if deleted:
            print(f"✓ {delete_date} 일기 삭제 완료")
        else:
            print(f"✗ {delete_date} 일기가 없습니다.")
    except ValueError as e:
        print(f"✗ 삭제 실패: {e}")
    print()

    # 연결 종료
    diary_repo.close()
    print("=== 테스트 완료 ===")


def main():
    """메인 함수"""
    print("MongoDB Diary Repository 테스트 도구\n")

    try:
        test_mongodb_diary()
    except KeyboardInterrupt:
        print("\n\n테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
