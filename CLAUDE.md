# 프로젝트 아키텍처 가이드

## 아키텍처 원칙

이 프로젝트는 **레이어드 아키텍처(Layered Architecture)** + **의존성 역전 원칙(DIP)** 을 따릅니다.

**핵심 원칙**:
- **Domain Layer는 아무것도 의존하지 않습니다** (순수 비즈니스 로직)
- **Presentation Layer는 Domain에 의존**합니다
- **Data Layer는 Domain의 인터페이스를 구현**합니다 (의존성 역전)

확장 가능성을 고려하여 설계하되, 초기에는 단순하게 시작합니다.

---

## 레이어 구조

```
┌─────────────────────────────────┐
│   Presentation Layer            │  ← CLI UI, 사용자 인터랙션
│   (CLI, 명령어, UI 컴포넌트)      │
└────────────┬────────────────────┘
             │ depends on
             ↓
┌─────────────────────────────────┐
│   Domain Layer                  │  ← 비즈니스 로직, 엔티티, 인터페이스
│   (일기 작성, 대화 관리, 규칙)    │  ← 아무것도 의존하지 않음!
│   + Repository 인터페이스 정의   │
└────────────┬────────────────────┘
             ↑ implements
             │
┌────────────┴────────────────────┐
│   Data Layer                    │  ← 저장소, 외부 API 구현체
│   (파일 시스템, DB, AI API)       │  ← Domain 인터페이스를 구현
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
**책임**: 비즈니스 로직, 도메인 규칙, 인터페이스 정의

- 일기 작성 로직 (AI와 대화 → 일기 생성)
- 대화 흐름 관리 (언제 종료할지 판단)
- 일기 스타일 선택 및 적용
- 기분 트래킹, 요약 생성 등 핵심 로직
- **Repository 인터페이스 정의** (Data Layer가 구현할 계약)
- **외부 의존성 없음** - 프레임워크, DB, API 등 아무것도 모름

**주요 파일**:
- `entities/` - 일기, 대화, 기분 등 도메인 엔티티
- `services/` - 대화 서비스, 일기 생성 서비스
- `interfaces/` - Repository 인터페이스 (Domain에 속함!)

**핵심 원칙**:
- **Domain은 아무것도 의존하지 않음** - 가장 안쪽 레이어
- **인터페이스(추상)는 Domain이 정의**하고, Data Layer가 구현함 (의존성 역전)

**예시**:
```python
# domain/interfaces/diary_repository.py (인터페이스는 Domain에 정의!)
from abc import ABC, abstractmethod

class DiaryRepositoryInterface(ABC):
    @abstractmethod
    def save(self, diary: Diary) -> None:
        pass

    @abstractmethod
    def get_by_date(self, date: str) -> Diary:
        pass

# domain/services/conversation_service.py
class ConversationService:
    def __init__(self, diary_repo: DiaryRepositoryInterface):
        self.diary_repo = diary_repo  # 추상에만 의존 (구현체 모름!)

    def start_conversation(self):
        # 비즈니스 로직
        diary = self._generate_diary(conversation)
        self.diary_repo.save(diary)  # 누가 구현했는지 모름
        return diary
```

---

### 3. Data Layer
**책임**: 데이터 영속성, 외부 시스템 연동, **Domain 인터페이스 구현**

- **Domain의 Repository 인터페이스를 구현**
- 일기 저장/조회 (파일 시스템 or DB)
- AI API 호출 (OpenAI, Anthropic 등)
- 설정 파일 관리 (API Key 등)

**확장 전략** (같은 인터페이스, 다른 구현체):
```
초기 구현:
- FileSystemDiaryRepository (JSON 파일 저장)
- LocalConfigStorage (로컬 설정 파일)

확장 후:
- DatabaseDiaryRepository (PostgreSQL/MySQL)
- RemoteConfigStorage (서버에서 설정 가져오기)

→ Domain/Presentation 코드는 변경 없이 Data Layer만 교체!
```

**주요 파일**:
- `repositories/` - Repository 구현체 (Domain의 인터페이스를 implements)
  - `file_diary_repository.py` (초기)
  - `db_diary_repository.py` (확장 시)
- `api/` - AI API 클라이언트
- `config/` - 설정 관리

**예시**:
```python
# data/repositories/file_diary_repository.py
# Domain의 인터페이스를 구현 (Domain → Data 방향 의존성 역전!)
from domain.interfaces.diary_repository import DiaryRepositoryInterface

class FileSystemDiaryRepository(DiaryRepositoryInterface):
    def save(self, diary: Diary):
        # JSON 파일로 저장
        with open(f"data/{diary.date}.json", "w") as f:
            json.dump(diary.to_dict(), f)

    def get_by_date(self, date: str) -> Diary:
        # JSON 파일에서 읽기
        with open(f"data/{date}.json", "r") as f:
            return Diary.from_dict(json.load(f))

# data/repositories/db_diary_repository.py (확장 시)
# 같은 인터페이스, 다른 구현체!
from domain.interfaces.diary_repository import DiaryRepositoryInterface

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
# cli.py (Presentation Layer) - 의존성 조립은 여기서!

# 초기 (로컬 파일)
from data.repositories.file_diary_repository import FileSystemDiaryRepository
from domain.services.conversation_service import ConversationService

diary_repo = FileSystemDiaryRepository()  # Data Layer 구현체
conversation_service = ConversationService(diary_repo)  # Domain은 인터페이스만 알고 있음

# 확장 후 (DB) - Domain/Presentation 코드는 변경 없음!
from data.repositories.db_diary_repository import DatabaseDiaryRepository
from domain.services.conversation_service import ConversationService

diary_repo = DatabaseDiaryRepository(db_connection)  # Data Layer만 교체
conversation_service = ConversationService(diary_repo)  # Domain 코드 동일!
```

**핵심**: Domain은 구현체를 모르고, Presentation이 어떤 구현체를 주입할지 결정합니다.

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

1. **Domain은 아무것도 의존하지 않음**: 가장 안쪽, 순수 비즈니스 로직
2. **인터페이스는 Domain이 정의**: Data Layer가 이를 구현 (의존성 역전)
3. **Presentation은 Domain에만 의존**: UI는 비즈니스 로직 호출
4. **Data Layer는 교체 가능**: 파일 → DB → API로 쉽게 전환 (같은 인터페이스)
5. **확장 시 기존 코드는 최소 변경**: 새로운 구현체 추가로 확장

**의존성 흐름**:
```
Presentation → Domain ← Data
                ↑
            (인터페이스 정의)
```

이 구조를 따르면, CLI → 웹 → 모바일로 확장해도 핵심 로직은 재사용 가능합니다.
