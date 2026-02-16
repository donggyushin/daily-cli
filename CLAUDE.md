# 프로젝트 아키텍처 가이드

## 아키텍처 원칙

이 프로젝트는 **레이어드 아키텍처(Layered Architecture)** 패턴을 따릅니다.
각 레이어는 명확한 책임을 가지며, 의존성 방향은 항상 **외부(Presentation) → 내부(Domain)**로 흐릅니다.

확장 가능성을 고려하여 설계하되, 초기에는 단순하게 시작합니다.

---

## 레이어 구조

```
┌─────────────────────────────────┐
│   Presentation Layer            │  ← CLI UI, 사용자 인터랙션
│   (CLI, 명령어, UI 컴포넌트)      │
└────────────┬────────────────────┘
             │ 의존
┌────────────▼────────────────────┐
│   Domain Layer                  │  ← 비즈니스 로직, 엔티티
│   (일기 작성, 대화 관리, 규칙)    │
└────────────┬────────────────────┘
             │ 의존
┌────────────▼────────────────────┐
│   Data Layer                    │  ← 저장소, 외부 API
│   (파일 시스템, DB, AI API)       │
└─────────────────────────────────┘
```

---

## 각 레이어의 책임

### 1. Presentation Layer
**책임**: 사용자와의 상호작용, 입력/출력 처리

- CLI 명령어 파싱 (`diary`, `diary show`, `diary list` 등)
- Rich를 이용한 터미널 UI 렌더링
- 사용자 입력 받기 및 검증
- Domain Layer 호출 및 결과 표시

**주요 파일**:
- `cli.py` - Typer 기반 명령어 정의
- `ui.py` - Rich 기반 UI 컴포넌트 (테이블, 프롬프트 등)

**예시**:
```python
# cli.py
@app.command()
def write():
    """오늘의 일기 작성"""
    conversation_service = ConversationService()  # Domain
    result = conversation_service.start_conversation()
    ui.display_diary(result)  # Presentation
```

---

### 2. Domain Layer
**책임**: 비즈니스 로직, 도메인 규칙

- 일기 작성 로직 (AI와 대화 → 일기 생성)
- 대화 흐름 관리 (언제 종료할지 판단)
- 일기 스타일 선택 및 적용
- 기분 트래킹, 요약 생성 등 핵심 로직
- **외부 의존성 없음** (Data Layer를 인터페이스로만 의존)

**주요 파일**:
- `entities/` - 일기, 대화, 기분 등 도메인 엔티티
- `services/` - 대화 서비스, 일기 생성 서비스
- `interfaces/` - Repository 인터페이스 (추상화)

**핵심 원칙**:
- Data Layer의 **구현체를 직접 참조하지 않음**
- Repository **인터페이스**를 통해서만 데이터 접근

**예시**:
```python
# services/conversation_service.py
class ConversationService:
    def __init__(self, diary_repo: DiaryRepositoryInterface):
        self.diary_repo = diary_repo  # 인터페이스에만 의존

    def start_conversation(self):
        # 비즈니스 로직
        diary = self._generate_diary(conversation)
        self.diary_repo.save(diary)  # 저장은 Data Layer에 위임
        return diary
```

---

### 3. Data Layer
**책임**: 데이터 영속성, 외부 시스템 연동

- 일기 저장/조회 (파일 시스템 or DB)
- AI API 호출 (OpenAI, Anthropic 등)
- 설정 파일 관리 (API Key 등)

**확장 전략**:
```
초기 구현:
- FileSystemDiaryRepository (JSON 파일 저장)
- LocalConfigStorage (로컬 설정 파일)

확장 후:
- DatabaseDiaryRepository (PostgreSQL/MySQL)
- RemoteConfigStorage (서버에서 설정 가져오기)
```

**주요 파일**:
- `repositories/` - Repository 구현체
  - `file_diary_repository.py` (초기)
  - `db_diary_repository.py` (확장 시)
- `api/` - AI API 클라이언트
- `config/` - 설정 관리

**예시**:
```python
# repositories/file_diary_repository.py
class FileSystemDiaryRepository(DiaryRepositoryInterface):
    def save(self, diary: Diary):
        # JSON 파일로 저장
        with open(f"data/{diary.date}.json", "w") as f:
            json.dump(diary.to_dict(), f)

    def get_by_date(self, date: str) -> Diary:
        # JSON 파일에서 읽기
        with open(f"data/{date}.json", "r") as f:
            return Diary.from_dict(json.load(f))

# repositories/db_diary_repository.py (확장 시)
class DatabaseDiaryRepository(DiaryRepositoryInterface):
    def save(self, diary: Diary):
        # PostgreSQL에 저장
        conn.execute("INSERT INTO diaries ...", diary.to_dict())

    def get_by_date(self, date: str) -> Diary:
        # PostgreSQL에서 조회
        row = conn.execute("SELECT * FROM diaries WHERE date = ?", date)
        return Diary.from_dict(row)
```

---

## 확장 시나리오

### Phase 1: CLI 로컬 앱 (초기)
```
Presentation: CLI (Typer + Rich)
Domain: 대화 로직, 일기 생성
Data: 로컬 파일 시스템 (JSON)
```

### Phase 2: 서버 + DB 추가
```
Presentation: CLI (동일)
Domain: 대화 로직, 일기 생성 (동일)
Data: PostgreSQL + API Server
```
**변경사항**: `FileSystemDiaryRepository` → `DatabaseDiaryRepository`로 교체만

### Phase 3: 웹/모바일 앱 추가
```
Presentation: CLI + Web(React) + Mobile(Swift)
Domain: 대화 로직, 일기 생성 (동일, API로 제공)
Data: PostgreSQL + API Server (동일)
```
**변경사항**: Presentation Layer만 추가, 나머지는 재사용

---

## 의존성 주입 (Dependency Injection)

각 레이어 간 결합도를 낮추기 위해 **의존성 주입** 사용:

```python
# 초기 (로컬 파일)
diary_repo = FileSystemDiaryRepository()
conversation_service = ConversationService(diary_repo)

# 확장 후 (DB)
diary_repo = DatabaseDiaryRepository(db_connection)
conversation_service = ConversationService(diary_repo)  # 코드 동일!
```

---

## 디렉토리 구조 (예상)

```
diary-cli/
├── diary/
│   ├── presentation/           # Presentation Layer
│   │   ├── cli.py              # CLI 명령어
│   │   └── ui.py               # UI 컴포넌트
│   ├── domain/                 # Domain Layer
│   │   ├── entities/           # 도메인 엔티티
│   │   │   ├── diary.py
│   │   │   ├── conversation.py
│   │   │   └── mood.py
│   │   ├── services/           # 비즈니스 로직
│   │   │   ├── conversation_service.py
│   │   │   ├── diary_writer_service.py
│   │   │   └── mood_tracker_service.py
│   │   └── interfaces/         # Repository 인터페이스
│   │       └── diary_repository.py
│   └── data/                   # Data Layer
│       ├── repositories/       # Repository 구현체
│       │   ├── file_diary_repository.py
│       │   └── db_diary_repository.py (확장 시)
│       ├── api/                # 외부 API
│       │   └── ai_client.py
│       └── config/             # 설정 관리
│           └── config_manager.py
├── data/                       # 실제 데이터 저장 (로컬)
├── tests/
├── requirements.txt
└── README.md
```

---

## 핵심 원칙 요약

1. **레이어 간 의존성은 단방향**: Presentation → Domain → Data
2. **Domain은 Data를 직접 참조하지 않음**: 인터페이스로만 의존
3. **Data Layer는 교체 가능**: 파일 → DB → API로 쉽게 전환
4. **Domain Layer는 순수 비즈니스 로직만**: 프레임워크, 라이브러리 독립적
5. **확장 시 기존 코드는 최소 변경**: 새로운 구현체 추가로 확장

이 구조를 따르면, CLI → 웹 → 모바일로 확장해도 핵심 로직은 재사용 가능합니다.
