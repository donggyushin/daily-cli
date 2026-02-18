# Diary Repository 구현 요약

## 📦 구현 완료

### MongoDB Diary Repository ✅

**파일**: `diary/data/repositories/mongodb_diary_repository.py`

**핵심 기능**:
- ✅ CRUD 작업 (생성, 조회, 수정, 삭제)
- ✅ **Cursor 기반 페이지네이션** (효율적인 대량 데이터 처리)
- ✅ 날짜 기반 고유성 (하루에 하나의 일기)
- ✅ 날짜 범위 필터링
- ✅ Context Manager 지원
- ✅ 인덱스 자동 생성 (성능 최적화)

---

## 🎯 Cursor 기반 페이지네이션

### 왜 Cursor 방식인가?

#### Offset 방식의 문제점
```python
# Offset 방식
page1 = get_diaries(offset=0, limit=10)    # 1-10
page2 = get_diaries(offset=10, limit=10)   # 11-20
page100 = get_diaries(offset=990, limit=10)  # 991-1000

# 문제:
# - offset=990 → 990개를 건너뛰어야 함 (느림!)
# - 새 데이터 추가 시 중복/누락
```

#### Cursor 방식의 장점
```python
# Cursor 방식
diaries, cursor = get_diaries(limit=10)              # 최근 10개
more, cursor = get_diaries(cursor=cursor, limit=10)  # 다음 10개

# 장점:
# - 항상 O(1) 시작 (인덱스 사용)
# - 데이터 추가되어도 안정적
# - 무한 스크롤에 최적화
```

### Cursor 구조

```python
# Cursor = base64(diary_date|created_at)
cursor_value = "2024-02-18|2024-02-18T10:30:00"
cursor = base64.b64encode(cursor_value.encode()).decode()
# → "MjAyNC0wMi0xOHwyMDI0LTAyLTE4VDEwOjMwOjAw"
```

### MongoDB 쿼리 예시

```javascript
// 첫 페이지
db.diaries.find()
  .sort({ diary_date: -1, created_at: -1 })
  .limit(11)  // limit+1 (다음 페이지 존재 여부 확인)

// 두 번째 페이지
db.diaries.find({
  $or: [
    { diary_date: { $lt: "2024-02-18" } },
    {
      diary_date: "2024-02-18",
      created_at: { $lt: "2024-02-18T10:30:00" }
    }
  ]
})
  .sort({ diary_date: -1, created_at: -1 })
  .limit(11)
```

---

## 📊 인덱스 전략

```javascript
// 1. diary_date 고유 인덱스
{ "diary_date": 1 }  // unique: true

// 2. diary_id 고유 인덱스
{ "diary_id": 1 }  // unique: true

// 3. 날짜 정렬 인덱스 (페이지네이션용)
{ "diary_date": -1 }

// 4. 생성시각 정렬 인덱스 (같은 날짜 대비)
{ "created_at": -1 }
```

**복합 정렬**: `diary_date DESC, created_at DESC`
- 최신 날짜 우선
- 같은 날짜면 최신 생성 시각 우선

---

## 🚀 사용 예시

### 기본 CRUD

```python
from diary.data.repositories import MongoDBDiaryRepository
from diary.domain.services import DiaryService
from datetime import date

# Repository + Service 생성
diary_repo = MongoDBDiaryRepository()
diary_service = DiaryService(diary_repo)

# 생성
diary = diary_service.create_diary(
    diary_date=date.today(),
    content="MongoDB Diary Repository 구현 완료!"
)

# 조회
today_diary = diary_service.get_today_diary()

# 수정
updated = diary_service.update_diary_by_date(
    diary_date=date.today(),
    new_content="수정된 내용"
)

# 삭제
deleted = diary_service.delete_diary_by_date(date.today())
```

### Cursor 페이지네이션

```python
# 첫 페이지
diaries, next_cursor = diary_service.list_diaries(limit=10)
for diary in diaries:
    print(f"{diary.get_formatted_date()}: {diary.content}")

# 다음 페이지
if next_cursor:
    more_diaries, next_cursor = diary_service.list_diaries(
        cursor=next_cursor,
        limit=10
    )
```

### 날짜 범위 필터링

```python
from datetime import date, timedelta

# 최근 30일
start_date = date.today() - timedelta(days=30)
end_date = date.today()

diaries, cursor = diary_service.list_diaries(
    start_date=start_date,
    end_date=end_date,
    limit=20
)
```

---

## 🧪 테스트

```bash
# MongoDB 시작
make up-db

# 테스트 실행
make test-diary

# 수동 테스트
uv run python scripts/test_mongodb_diary.py
```

**테스트 시나리오**:
1. ✅ 일기 작성 (날짜 중복 검증)
2. ✅ 여러 날짜의 일기 생성
3. ✅ 날짜로 조회
4. ✅ Cursor 페이지네이션 (첫 페이지, 다음 페이지)
5. ✅ 일기 수정
6. ✅ 날짜 범위 필터링
7. ✅ 일기 삭제

---

## 📐 아키텍처

```
┌─────────────────────────────────┐
│   Domain Layer                  │
│   ┌───────────────────────────┐ │
│   │ DiaryRepositoryInterface  │ │  ← 인터페이스 정의
│   │ - save()                  │ │
│   │ - get_by_date()           │ │
│   │ - list_diaries()          │ │  ← Cursor 기반
│   │ - delete()                │ │
│   │ - exists_on_date()        │ │
│   └───────────────────────────┘ │
└────────────┬────────────────────┘
             ↑ implements
             │
┌────────────┴────────────────────┐
│   Data Layer                    │
│   ┌───────────────────────────┐ │
│   │ MongoDBDiaryRepository    │ │  ← 구현체 ✅
│   │                           │ │
│   │ MongoDB 컬렉션:           │ │
│   │ - diaries                 │ │
│   │                           │ │
│   │ 인덱스:                   │ │
│   │ - diary_date (unique)     │ │
│   │ - diary_id (unique)       │ │
│   │ - diary_date DESC         │ │
│   │ - created_at DESC         │ │
│   └───────────────────────────┘ │
└─────────────────────────────────┘
```

**의존성 역전 원칙(DIP)**:
- Domain이 인터페이스 정의 ✅
- Data Layer가 구현 ✅
- Domain은 MongoDB를 전혀 모름 ✅

---

## 🔄 확장 계획

### 현재 구현됨 ✅
- MongoDBDiaryRepository (MongoDB)
- Cursor 기반 페이지네이션

### 향후 구현 예정
- FileSystemDiaryRepository (JSON 파일)
- PostgreSQLDiaryRepository (PostgreSQL)

**교체 방법** (의존성 주입):
```python
# Before: MongoDB
diary_repo = MongoDBDiaryRepository()

# After: 파일 시스템
diary_repo = FileSystemDiaryRepository()

# Service는 동일!
diary_service = DiaryService(diary_repo)
```

---

## 📚 관련 문서

- [DIARY_MONGODB_GUIDE.md](DIARY_MONGODB_GUIDE.md) - 상세 사용 가이드
- [CLAUDE.md](../CLAUDE.md) - 전체 아키텍처
- [MONGODB_SETUP.md](MONGODB_SETUP.md) - MongoDB 초기 설정

---

## ✨ 핵심 성과

1. ✅ **Cursor 기반 페이지네이션** - 효율적이고 안정적
2. ✅ **날짜 고유성** - 하루에 하나의 일기만
3. ✅ **의존성 역전** - Domain이 인터페이스 정의
4. ✅ **확장 가능** - 같은 인터페이스로 다른 저장소 추가 가능

**MongoDB Diary Repository로 확장 가능하고 성능 좋은 일기 관리 시스템 완성!** 🚀
