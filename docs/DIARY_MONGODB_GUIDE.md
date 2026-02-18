# MongoDB Diary Repository 사용 가이드

MongoDB를 이용한 일기 저장소 사용 방법을 설명합니다.

## 🎯 핵심 기능

### 1. Cursor 기반 페이지네이션
- **효율적인 대량 데이터 처리** - Offset 방식보다 빠름
- **안정적인 페이징** - 새 데이터 추가 시에도 중복/누락 없음
- **무한 스크롤** - 모바일/웹 UI에 최적화

### 2. 날짜 기반 고유성
- **하루에 하나의 일기만** - diary_date를 unique 인덱스로 관리
- **자동 충돌 검증** - 같은 날짜에 중복 작성 방지

### 3. MongoDB 최적화
- **인덱스 자동 생성** - 조회 성능 최적화
- **효율적인 정렬** - 날짜 + 생성시각 복합 정렬

---

## 📦 설치 및 설정

### 1. MongoDB 시작

```bash
# 환경 변수 설정
make setup-env
vi .env  # 비밀번호 변경

# MongoDB 시작
make up-db
```

### 2. 의존성 설치

이미 `pyproject.toml`에 포함되어 있습니다:
```toml
dependencies = [
    "pymongo>=4.6.0",
    "python-dotenv>=1.0.0",
]
```

```bash
uv sync
```

---

## 🚀 기본 사용법

### 1. Repository 생성

```python
from diary.data.repositories import MongoDBDiaryRepository

# 기본 설정 (환경 변수 사용)
diary_repo = MongoDBDiaryRepository()

# 또는 직접 지정
diary_repo = MongoDBDiaryRepository(
    host="mongodb",
    port=27017,
    username="admin",
    password="your-password",
    database="daily_diary"
)
```

### 2. DiaryService 사용 (권장)

```python
from diary.domain.services import DiaryService
from datetime import date

# Service 생성 (비즈니스 로직 포함)
diary_service = DiaryService(diary_repo)

# 일기 작성
diary = diary_service.create_diary(
    diary_date=date.today(),
    content="오늘의 일기 내용"
)

# 같은 날짜에 중복 작성 시도 → ValueError 발생!
# diary_service.create_diary(date.today(), "중복") → 에러
```

---

## 📝 CRUD 예시

### Create - 일기 작성

```python
from datetime import date

# 방법 1: Service 사용 (권장)
diary = diary_service.create_diary(
    diary_date=date(2024, 2, 18),
    content="MongoDB Diary Repository를 구현했다."
)

# 방법 2: Repository 직접 사용
from diary.domain.entities import Diary

new_diary = Diary(
    diary_date=date(2024, 2, 18),
    content="직접 생성한 일기"
)
saved_diary = diary_repo.save(new_diary)
print(f"저장됨: {saved_diary.diary_id}")
```

### Read - 일기 조회

```python
from datetime import date

# 날짜로 조회
today_diary = diary_service.get_diary_by_date(date.today())
if today_diary:
    print(f"{today_diary.get_formatted_date()}")
    print(f"{today_diary.content}")

# ID로 조회
diary = diary_repo.get_by_id("diary-id-12345")

# 오늘의 일기
today_diary = diary_service.get_today_diary()
```

### Update - 일기 수정

```python
from datetime import date

# 방법 1: Service 사용 (권장)
updated_diary = diary_service.update_diary_by_date(
    diary_date=date.today(),
    new_content="수정된 내용"
)

# 방법 2: Repository 직접 사용
diary = diary_repo.get_by_date(date.today())
if diary:
    diary.update_content("수정된 내용")
    diary_repo.save(diary)
```

### Delete - 일기 삭제

```python
from datetime import date

# 방법 1: Service 사용 (권장)
deleted = diary_service.delete_diary_by_date(date.today())

# 방법 2: Repository 직접 사용
deleted = diary_repo.delete("diary-id-12345")
print(f"삭제 성공: {deleted}")
```

---

## 📄 Cursor 기반 페이지네이션

### 기본 사용법

```python
# 첫 페이지 (최신 10개)
diaries, next_cursor = diary_service.list_diaries(limit=10)

for diary in diaries:
    print(f"{diary.get_formatted_date()}: {diary.content[:50]}...")

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

# 최근 30일간의 일기
start_date = date.today() - timedelta(days=30)
end_date = date.today()

diaries, cursor = diary_service.list_diaries(
    start_date=start_date,
    end_date=end_date,
    limit=20
)
```

### 무한 스크롤 패턴

```python
def load_all_diaries():
    """모든 일기를 페이지별로 로드"""
    all_diaries = []
    cursor = None

    while True:
        diaries, cursor = diary_service.list_diaries(
            cursor=cursor,
            limit=30
        )

        all_diaries.extend(diaries)

        # 더 이상 데이터가 없으면 종료
        if not cursor:
            break

    return all_diaries

# 실행
all_diaries = load_all_diaries()
print(f"총 {len(all_diaries)}개의 일기")
```

---

## 🔍 Cursor 동작 원리

### Cursor 형식

```
base64(diary_date|created_at)
```

예시:
```python
# 원본 데이터
cursor_value = "2024-02-18|2024-02-18T10:30:00"

# Base64 인코딩
import base64
cursor = base64.b64encode(cursor_value.encode()).decode()
print(cursor)  # "MjAyNC0wMi0xOHwyMDI0LTAyLTE4VDEwOjMwOjAw"
```

### MongoDB 쿼리

```javascript
// 첫 페이지
db.diaries.find()
  .sort({ diary_date: -1, created_at: -1 })
  .limit(10)

// 두 번째 페이지 (cursor 사용)
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
  .limit(10)
```

### 장점

1. **성능**: 항상 인덱스 사용 (offset 방식의 SKIP 없음)
2. **안정성**: 새 데이터 추가 시에도 페이지 일관성 유지
3. **확장성**: 데이터가 많아져도 성능 저하 없음

---

## 🧪 테스트

### 테스트 스크립트 실행

```bash
# MongoDB가 실행 중인지 확인
make status-db

# 테스트 실행
make test-diary

# 또는 직접 실행
uv run python scripts/test_mongodb_diary.py
```

### 테스트 내용

1. ✅ 일기 작성
2. ✅ 여러 날짜의 일기 작성
3. ✅ 날짜로 조회
4. ✅ Cursor 기반 페이지네이션
5. ✅ 일기 수정
6. ✅ 날짜 범위 필터링
7. ✅ 일기 삭제

---

## 📊 MongoDB 데이터 구조

### diaries 컬렉션

```javascript
{
  "_id": ObjectId("..."),
  "diary_id": "uuid-string",
  "diary_date": "2024-02-18",  // ISO 8601 형식
  "content": "일기 내용",
  "created_at": "2024-02-18T10:30:00",
  "updated_at": "2024-02-18T10:30:00"
}
```

### 인덱스

```javascript
// 1. diary_date 고유 인덱스 (하루에 하나의 일기만)
{ "diary_date": 1 }  // unique: true

// 2. diary_id 고유 인덱스
{ "diary_id": 1 }  // unique: true

// 3. 날짜 기준 정렬 인덱스
{ "diary_date": -1 }

// 4. 생성 시각 정렬 인덱스
{ "created_at": -1 }
```

---

## 🔧 고급 기능

### Context Manager 사용

```python
# 자동으로 연결 종료
with MongoDBDiaryRepository() as diary_repo:
    diary_service = DiaryService(diary_repo)

    diary = diary_service.create_diary(
        diary_date=date.today(),
        content="Context Manager 사용 예시"
    )

# 여기서 자동으로 diary_repo.close() 호출됨
```

### 날짜 존재 여부 확인

```python
from datetime import date

# 특정 날짜에 일기가 있는지 확인
exists = diary_service.has_diary_on_date(date.today())
if exists:
    print("오늘 일기가 이미 있습니다.")
else:
    print("오늘 일기를 작성할 수 있습니다.")
```

---

## 🚨 주의사항

### 1. 날짜 중복

```python
# ❌ 같은 날짜에 두 번 작성 불가
diary1 = diary_service.create_diary(date.today(), "첫 번째")
diary2 = diary_service.create_diary(date.today(), "두 번째")  # ValueError!

# ✅ 수정을 사용하세요
diary_service.update_diary_by_date(date.today(), "두 번째 (수정됨)")
```

### 2. MongoDB 연결

```python
# ❌ 연결을 닫지 않으면 리소스 누수
diary_repo = MongoDBDiaryRepository()
# ... 작업 ...
# 연결이 열려있음!

# ✅ 명시적으로 닫기
diary_repo.close()

# ✅ 또는 Context Manager 사용
with MongoDBDiaryRepository() as diary_repo:
    # ... 작업 ...
    pass  # 자동으로 닫힘
```

### 3. Cursor 만료

Cursor는 영구적이지 않습니다. 클라이언트에서 적절히 관리해야 합니다.

```python
# ❌ 오래된 cursor는 무효화될 수 있음
cursor = get_cursor_from_cache()  # 1시간 전 cursor
diaries, _ = diary_service.list_diaries(cursor=cursor)  # 실패 가능

# ✅ cursor 파싱 실패 시 자동으로 처음부터 조회
# (MongoDBDiaryRepository 내부에서 처리)
```

---

## 🔄 마이그레이션

파일 시스템에서 MongoDB로 데이터를 이전하려면:

```python
# scripts/migrate_diary_to_mongodb.py
from diary.data.repositories import (
    FileSystemDiaryRepository,  # 구현 예정
    MongoDBDiaryRepository
)

# 파일에서 로드
file_repo = FileSystemDiaryRepository()
diaries = file_repo.list_all()

# MongoDB에 저장
mongo_repo = MongoDBDiaryRepository()
for diary in diaries:
    mongo_repo.save(diary)

print(f"마이그레이션 완료: {len(diaries)}개")
```

---

## 📚 관련 문서

- [CLAUDE.md](../CLAUDE.md) - 전체 아키텍처 가이드
- [MONGODB_SETUP.md](MONGODB_SETUP.md) - MongoDB 초기 설정
- [SECURITY.md](SECURITY.md) - 보안 가이드

---

**핵심**: MongoDB Diary Repository는 Cursor 기반 페이지네이션으로 효율적이고 안정적인 일기 관리를 제공합니다! 🚀
