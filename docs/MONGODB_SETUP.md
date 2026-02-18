# MongoDB 설정 가이드

이 문서는 Daily CLI에서 MongoDB를 데이터 저장소로 사용하는 방법을 설명합니다.

## 1. MongoDB 시작하기

### 🔐 초기 설정 (보안 - 필수!)

**처음 MongoDB를 사용하기 전에 반드시 수행:**

```bash
# Step 1: 환경 변수 파일 생성
make setup-env

# Step 2: 비밀번호 변경 (⚠️ 필수!)
vi .env
# MONGODB_PASSWORD=CHANGE_THIS_PASSWORD  →  강력한 비밀번호로 변경
# ME_CONFIG_BASICAUTH_PASSWORD=CHANGE_THIS_PASSWORD  →  변경

# Step 3: 보안 검증
make check-env
```

**⚠️ 중요:**
- 기본 비밀번호(`CHANGE_THIS_PASSWORD`)를 절대 그대로 사용하지 마세요!
- `.env` 파일은 Git에 커밋되지 않습니다 (`.gitignore`에 포함됨)
- 자세한 내용: [docs/SECURITY.md](SECURITY.md)

### Docker Compose로 MongoDB 실행

```bash
# MongoDB + Mongo Express 시작 (자동으로 보안 검증)
make up-db

# 또는 직접 실행
docker compose up -d mongodb mongo-express
```

서비스 확인:
- **MongoDB**: `localhost:27017`
- **Mongo Express** (웹 UI): `http://localhost:8081`
  - Username/Password: `.env` 파일에 설정한 값

### MongoDB 중지

```bash
# MongoDB 서비스 중지
make down-db

# 또는 직접 실행
docker compose down mongodb mongo-express
```

---

## 2. 환경 변수 설정

### .env 파일 생성

```bash
# 예시 파일 복사
cp .env.example .env
```

### .env 파일 내용

```bash
# MongoDB 연결 정보
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USERNAME=admin
MONGODB_PASSWORD=admin123
MONGODB_DATABASE=daily_diary

# Mongo Express 인증 정보
ME_CONFIG_BASICAUTH_USERNAME=admin
ME_CONFIG_BASICAUTH_PASSWORD=admin123

# 애플리케이션 설정
TZ=Asia/Seoul
```

---

## 3. 애플리케이션에서 MongoDB 사용

### main.py 수정 (기존 파일 시스템 → MongoDB)

```python
# main.py

# 기존: FileSystem 저장소
# from diary.data.repositories import FileSystemChatRepository
# chat_repo = FileSystemChatRepository()

# 변경: MongoDB 저장소
from diary.data.repositories import MongoDBChatRepository

chat_repo = MongoDBChatRepository()  # 환경 변수에서 자동 설정

# 또는 직접 지정
chat_repo = MongoDBChatRepository(
    host="mongodb",
    port=27017,
    username="admin",
    password="admin123",
    database="daily_diary"
)

# ChatService 생성 (동일)
chat_service = ChatService(
    chat_repo=chat_repo,
    ai_client=ai_client,
    preferences_service=preferences_service
)
```

---

## 4. MongoDB 직접 접속

### MongoDB Shell 접속

```bash
# Makefile 이용
make mongo-shell

# 또는 직접 실행
docker compose exec mongodb mongosh -u admin -p admin123
```

### 기본 명령어

```javascript
// 데이터베이스 선택
use daily_diary

// 컬렉션 목록 보기
show collections

// 채팅 세션 조회
db.chat_sessions.find().pretty()

// 특정 세션 조회
db.chat_sessions.findOne({ session_id: "your-session-id" })

// 활성 세션 확인
db.active_session.findOne()

// 전체 데이터 삭제 (주의!)
db.chat_sessions.deleteMany({})
```

---

## 5. Mongo Express 웹 UI 사용

브라우저에서 `http://localhost:8081` 접속

1. **로그인**
   - Username: `admin`
   - Password: `admin123`

2. **데이터베이스 선택**: `daily_diary`

3. **컬렉션 확인**
   - `chat_sessions`: 채팅 세션 데이터
   - `active_session`: 현재 활성 세션

4. **GUI로 데이터 조회/편집**
   - 각 컬렉션 클릭 → 문서 확인
   - 필터링, 정렬, 편집 가능

---

## 6. 데이터 마이그레이션 (파일 → MongoDB)

기존 파일 시스템 데이터를 MongoDB로 이전하려면:

```python
# migration_script.py (예시)
from diary.data.repositories import FileSystemChatRepository, MongoDBChatRepository

# 기존 데이터 로드
file_repo = FileSystemChatRepository()
sessions = file_repo.list_sessions()

# MongoDB에 저장
mongo_repo = MongoDBChatRepository()
for session in sessions:
    mongo_repo.save_session(session)

print(f"마이그레이션 완료: {len(sessions)}개 세션")
```

---

## 7. 트러블슈팅

### 연결 실패 시

```bash
# MongoDB 상태 확인
docker compose ps

# MongoDB 로그 확인
make logs-db

# 또는 직접 실행
docker compose logs -f mongodb
```

### 인증 오류

- `.env` 파일의 `MONGODB_USERNAME`, `MONGODB_PASSWORD` 확인
- docker-compose.yml의 `MONGO_INITDB_ROOT_USERNAME/PASSWORD`와 일치 확인

### 네트워크 오류

```bash
# 네트워크 재생성
docker compose down
docker compose up -d
```

---

## 8. 프로덕션 배포 시 주의사항

### 보안
- **절대 기본 비밀번호 사용 금지** (`admin/admin123` 변경)
- `.env` 파일을 `.gitignore`에 추가 (이미 포함됨)
- 프로덕션에서는 환경 변수를 안전한 방법으로 관리 (AWS Secrets Manager 등)

### 성능
- MongoDB 버전: 8.0 사용 (최신 안정 버전)
- 인덱스 자동 생성 (`_create_indexes()`)
- 필요시 추가 인덱스 생성

### 백업
```bash
# MongoDB 데이터 백업
docker compose exec mongodb mongodump -u admin -p admin123 -o /data/backup

# 복구
docker compose exec mongodb mongorestore -u admin -p admin123 /data/backup
```

---

## 9. 아키텍처 장점 (DIP 덕분)

```
┌──────────────────────────────┐
│  Presentation Layer (CLI)    │
└──────────┬───────────────────┘
           │
           ↓
┌──────────────────────────────┐
│  Domain Layer                │
│  - ChatService               │
│  - ChatRepositoryInterface   │  ← 인터페이스만 정의
└──────────┬───────────────────┘
           ↑ implements
           │
┌──────────┴───────────────────┐
│  Data Layer                  │
│  - FileSystemChatRepository  │  ← 파일 시스템 구현
│  - MongoDBChatRepository     │  ← MongoDB 구현 ⭐
└──────────────────────────────┘
```

**핵심**:
- Domain/Presentation 코드는 **전혀 수정 없음**
- `main.py`에서 Repository만 교체
- 같은 인터페이스 → 다른 구현체

```python
# Before
chat_repo = FileSystemChatRepository()

# After
chat_repo = MongoDBChatRepository()

# 나머지 코드는 동일!
chat_service = ChatService(chat_repo, ai_client, preferences_service)
```

---

## 10. 다음 단계

- [ ] MongoDB Atlas (클라우드) 연동
- [ ] 다른 Repository도 MongoDB로 마이그레이션
  - `CredentialRepository`
  - `UserPreferencesRepository`
- [ ] 백업 자동화 스크립트
- [ ] 모니터링 (Prometheus + Grafana)
