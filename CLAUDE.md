# 프로젝트 아키텍처 가이드

## 개발 환경 설정

### 패키지 매니저: uv

이 프로젝트는 **uv**를 패키지 매니저로 사용합니다.

```bash
# 의존성 설치
uv sync

# 애플리케이션 실행
uv run python main.py

# 특정 명령 실행 (uv 가상환경 내에서)
uv run <command>
```

**중요**: `pip install`이 아닌 `uv sync`를 사용하세요.

### Docker 사용

Docker를 사용한 실행도 지원합니다.

```bash
# 빌드
make build

# 실행
make run

# 개발 모드 (소스 코드 마운트)
make dev
```

자세한 내용은 [README.md](./README.md) 참조.

---

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
│   (CLI, UI 컴포넌트)             │  ← 단일 책임 원칙 적용
└────────────┬────────────────────┘
             │ depends on
             ↓
┌─────────────────────────────────┐
│   Domain Layer                  │  ← 비즈니스 로직, 엔티티, 인터페이스
│   (일기 작성, 스타일 관리)        │  ← 아무것도 의존하지 않음!
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

- CLI 명령어 파싱 및 실행
- Rich를 이용한 터미널 UI 렌더링
- 사용자 입력 받기 및 검증
- Domain Layer 호출 및 결과 표시
- **UI 컴포넌트 분리** (단일 책임 원칙)

**주요 파일**:
- `cli.py` - 메인 CLI 앱 (오케스트레이션만 담당)
- `api_key_ui.py` - API Key 관리 UI
- `preferences_ui.py` - 사용자 설정 UI
- `chat_ui.py` - AI 채팅 UI ⭐ NEW

**아키텍처 패턴** (UI 컴포넌트 분리):
```python
# cli.py - 간결한 오케스트레이터
class DiaryApp:
    def __init__(self, credential_service, preferences_service):
        self.credential_service = credential_service
        self.preferences_service = preferences_service
        self.console = Console()

        # UI 컴포넌트 초기화 (의존성 주입)
        self.api_key_ui = ApiKeyUI(credential_service, self.console)
        self.preferences_ui = PreferencesUI(preferences_service, self.console)

    def _manage_api_keys(self):
        # 복잡한 로직은 전문 UI 클래스에 위임
        self.api_key_ui.show_management_menu(on_back_callback=self._show_menu)
```

**장점**:
- 각 UI 컴포넌트가 독립적으로 관리됨
- `cli.py`가 간결해짐 (110줄, 원래 272줄)
- 테스트 및 유지보수 용이

---

### 2. Domain Layer
**책임**: 비즈니스 로직, 도메인 규칙, 인터페이스 정의

#### 2.1 Entities (도메인 엔티티)
현재 구현된 엔티티:

**AICredential** - AI 서비스 인증 정보
```python
class AICredential:
    provider: AIProvider  # OpenAI, Anthropic, Google
    api_key: str
    is_default: bool

    def mask_api_key(self) -> str:
        """보안을 위해 API 키 마스킹"""
        return f"{self.api_key[:8]}...{self.api_key[-6:]}"
```

**UserPreferences** - 사용자 설정
```python
class UserPreferences:
    writing_style: WritingStyle  # 선택한 일기 작성 스타일

    def change_writing_style(self, new_style: WritingStyle):
        """비즈니스 로직: 스타일 변경"""
        self.writing_style = new_style
        self.updated_at = datetime.now()
```

**WritingStyle** - 일기 작성 스타일
```python
class WritingStyle(Enum):
    OBJECTIVE_THIRD_PERSON = "objective_third_person"      # 객관적 3인칭
    FIRST_PERSON_AUTOBIOGRAPHY = "first_person_autobiography"  # 1인칭 자서전
    EMOTIONAL_LITERARY = "emotional_literary"              # 감성적/문학적

    def get_prompt_instruction(self, examples: list[str] = None) -> str:
        """AI 프롬프트 생성 (Few-shot learning 지원)"""
        # EMOTIONAL_LITERARY + 예시 문장 → 강화된 프롬프트
```

**ChatMessage** - 채팅 메시지 ⭐ NEW
```python
class ChatMessage:
    role: MessageRole     # user, assistant, system
    content: str
    timestamp: datetime

    def to_dict(self) -> dict:
        """저장을 위한 직렬화"""
```

**ChatSession** - 채팅 세션 ⭐ NEW
```python
class ChatSession:
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    is_active: bool

    def add_message(self, role: MessageRole, content: str) -> None:
        """비즈니스 로직: 메시지 추가"""

    def get_conversation_history(self) -> List[dict]:
        """AI API 호출용 대화 히스토리 반환"""
```

**Diary** - 일기 ⭐ NEW
```python
class Diary:
    diary_date: date          # 일기 날짜 (YYYY-MM-DD)
    content: str              # 일기 내용
    diary_id: Optional[str]   # 일기 고유 ID
    created_at: datetime      # 생성 시각
    updated_at: datetime      # 수정 시각

    def update_content(self, new_content: str) -> None:
        """비즈니스 로직: 내용 수정 및 시각 갱신"""

    def is_today(self) -> bool:
        """오늘 작성한 일기인지 확인"""

    def get_formatted_date(self) -> str:
        """포맷된 날짜 반환 (예: 2024년 2월 18일 월요일)"""

    def get_word_count(self) -> int:
        """글자 수 반환"""
```

#### 2.2 Services (비즈니스 로직)
- `CredentialService` - API Key 관리, 검증, 기본 AI 설정
- `UserPreferencesService` - 사용자 설정 관리, 강화된 프롬프트 생성
- `ChatService` - AI 대화 세션 관리, 메시지 전송/응답 처리 ⭐ NEW
- `DiaryService` - 일기 CRUD, 날짜 중복 검증, 페이지네이션 ⭐ NEW

#### 2.3 Interfaces (Repository 인터페이스)
Domain이 정의하고, Data Layer가 구현:
- `CredentialRepositoryInterface`
- `UserPreferencesRepositoryInterface`
- `WritingStyleExamplesRepositoryInterface`
- `AIClientInterface` - AI API 호출 추상화 ⭐ NEW
- `ChatRepositoryInterface` - 채팅 저장소 추상화 ⭐ NEW
- `DiaryRepositoryInterface` - 일기 저장소 (Cursor 기반 페이지네이션) ⭐ NEW

**핵심 원칙**:
- **Domain은 아무것도 의존하지 않음** - 가장 안쪽 레이어
- **인터페이스(추상)는 Domain이 정의**하고, Data Layer가 구현함 (의존성 역전)

**실제 예시 1 - UserPreferencesRepository**:
```python
# domain/interfaces/user_preferences_repository.py
from abc import ABC, abstractmethod

class UserPreferencesRepositoryInterface(ABC):
    @abstractmethod
    def save(self, preferences: UserPreferences) -> None:
        pass

    @abstractmethod
    def get(self) -> Optional[UserPreferences]:
        pass

# domain/services/user_preferences_service.py
class UserPreferencesService:
    def __init__(
        self,
        preferences_repo: UserPreferencesRepositoryInterface,  # 인터페이스에만 의존
        examples_repo: Optional[WritingStyleExamplesRepositoryInterface] = None
    ):
        self.preferences_repo = preferences_repo
        self.examples_repo = examples_repo  # 선택적 의존성

    def get_style_prompt_instruction(self) -> str:
        """현재 스타일의 AI 프롬프트 생성 (예시 포함)"""
        current_style = self.get_current_writing_style()

        # 예시 문장 로드 (Few-shot learning)
        examples = []
        if self.examples_repo:
            examples = self.examples_repo.get_examples(current_style)

        return current_style.get_prompt_instruction(examples)
```

**실제 예시 2 - DiaryRepository (Cursor 기반 페이지네이션)** ⭐ NEW:
```python
# domain/interfaces/diary_repository.py
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from datetime import date

class DiaryRepositoryInterface(ABC):
    @abstractmethod
    def save(self, diary: Diary) -> Diary:
        """일기 저장"""
        pass

    @abstractmethod
    def get_by_date(self, diary_date: date) -> Optional[Diary]:
        """특정 날짜의 일기 조회"""
        pass

    @abstractmethod
    def list_diaries(
        self,
        cursor: Optional[str] = None,
        limit: int = 30,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Tuple[List[Diary], Optional[str]]:
        """
        일기 목록 조회 (Cursor 기반 페이지네이션)

        Returns:
            (일기 리스트, 다음 커서)
            - 일기 리스트: 최신순으로 정렬된 일기들
            - 다음 커서: 다음 페이지를 가져올 커서 (더 이상 없으면 None)
        """
        pass

# domain/services/diary_service.py
class DiaryService:
    def __init__(self, diary_repo: DiaryRepositoryInterface):
        self.diary_repo = diary_repo

    def create_diary(self, diary_date: date, content: str) -> Diary:
        """일기 작성 (날짜 중복 검증 포함)"""
        if self.diary_repo.exists_on_date(diary_date):
            raise ValueError("해당 날짜의 일기가 이미 존재합니다.")

        diary = Diary(diary_date=diary_date, content=content)
        return self.diary_repo.save(diary)

    def list_diaries(self, cursor: Optional[str] = None, limit: int = 30):
        """Cursor 기반 페이지네이션"""
        return self.diary_repo.list_diaries(cursor=cursor, limit=limit)
```

---

### 3. Data Layer
**책임**: 데이터 영속성, 외부 시스템 연동, **Domain 인터페이스 구현**

#### 3.1 현재 구현된 Repository

**FileSystemCredentialRepository**
- AI API Key를 JSON 파일로 저장 (`data/credentials.json`)
- 중복 방지, 기본 AI 설정 관리

**FileSystemUserPreferencesRepository**
- 사용자 설정을 JSON 파일로 저장 (`data/user_preferences.json`)

**FileSystemWritingStyleExamplesRepository**
- 스타일별 예시 문장을 텍스트 파일로 관리
- `data/writing_examples/emotional_literary.txt`
- 주석(`#`) 지원, 빈 줄 자동 필터링
- Few-shot learning을 위한 예시 제공

```python
# data/repositories/file_writing_style_examples_repository.py
class FileSystemWritingStyleExamplesRepository(WritingStyleExamplesRepositoryInterface):
    def get_examples(self, style: WritingStyle) -> list[str]:
        """예시 문장 로드 (파일이 없으면 빈 리스트)"""
        file_path = self.examples_dir / f"{style.value}.txt"

        if not file_path.exists():
            return []

        with open(file_path, "r", encoding="utf-8") as f:
            return [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.strip().startswith("#")
            ]
```

**FileSystemChatRepository** ⭐ NEW
- 채팅 세션을 JSON 파일로 저장 (`data/chats/{session-id}.json`)
- 활성 세션 추적 (`data/chats/active_session.json`)
- 세션 목록 조회, 삭제 기능

**MongoDBChatRepository** ⭐ NEW
- 채팅 세션을 MongoDB에 저장
- `chat_sessions` 컬렉션 사용
- 인덱스 자동 생성 (성능 최적화)
- Context Manager 지원

**OpenAIClient** ⭐ NEW
- OpenAI GPT 모델 API 클라이언트 (기본: gpt-4o-mini)
- `AIClientInterface` 구현

**AnthropicClient** ⭐ NEW
- Anthropic Claude 모델 API 클라이언트 (기본: claude-3-5-haiku)
- `AIClientInterface` 구현

**GoogleAIClient** ⭐ NEW
- Google Gemini 모델 API 클라이언트 (기본: gemini-1.5-flash)
- `AIClientInterface` 구현

#### 3.2 확장 전략

**같은 인터페이스, 다른 구현체**:
```
초기:
- FileSystemCredentialRepository (JSON)
- FileSystemUserPreferencesRepository (JSON)
- FileSystemWritingStyleExamplesRepository (TXT)
- FileSystemChatRepository (JSON)
- FileSystemDiaryRepository (JSON) ← 구현 예정

확장 후 (MongoDB):
- MongoDBChatRepository (MongoDB) ✅ 구현됨
- MongoDBDiaryRepository (MongoDB) ← 구현 예정

확장 후 (PostgreSQL):
- DatabaseCredentialRepository (PostgreSQL)
- DatabaseUserPreferencesRepository (PostgreSQL)
- RemoteWritingStyleExamplesRepository (API)

→ Domain/Presentation 코드는 변경 없이 Data Layer만 교체!
→ MongoDB와 파일 시스템을 혼용 가능 (서로 다른 Repository 사용)
```

---

## 특별 기능

### 1. Few-shot Learning 시스템

**목적**: 사용자가 좋아하는 작가의 문체를 AI에게 학습시키기

### 아키텍처

```
User edits text file
        ↓
data/writing_examples/emotional_literary.txt
        ↓
FileSystemWritingStyleExamplesRepository (Data Layer)
        ↓
UserPreferencesService (Domain Layer)
        ↓
WritingStyle.get_prompt_instruction(examples)
        ↓
Enhanced AI Prompt with Few-shot examples
```

### 사용 방법

1. **예시 문장 추가** (코드 수정 불필요!):
```txt
# data/writing_examples/emotional_literary.txt
긴 회의들 사이로 피로가 밀려왔다.
석양이 창문을 물들일 때쯤, 나는 하루의 무게를 느꼈다.
시간은 천천히, 매우 천천히 흘러갔다.
```

2. **자동으로 AI 프롬프트에 포함**:
```
일기를 감성적이고 문학적인 스타일로 작성해주세요.

다음은 참고할 수 있는 문학적 표현 예시입니다:
- 긴 회의들 사이로 피로가 밀려왔다.
- 석양이 창문을 물들일 때쯤, 나는 하루의 무게를 느꼈다.
- 시간은 천천히, 매우 천천히 흘러갔다.

이러한 스타일을 참고하여 깊이 있고 감성적인 일기를 작성해주세요.
```

#### 아키텍처 장점
- ✅ **사용자 친화적**: 텍스트 파일만 편집
- ✅ **레이어 분리**: Domain은 파일 시스템 모름
- ✅ **선택적 기능**: 예시 파일 없어도 기본 동작
- ✅ **확장 가능**: 다른 스타일에도 동일하게 적용

---

### 2. Cursor 기반 페이지네이션 ⭐ NEW

**목적**: 효율적인 일기 목록 조회 (대량 데이터 처리)

#### 왜 Cursor 기반인가?

**전통적 Offset 기반의 문제점**:
```python
# Offset 방식 (비효율적)
page1 = get_diaries(offset=0, limit=10)   # 1-10번 일기
page2 = get_diaries(offset=10, limit=10)  # 11-20번 일기
page3 = get_diaries(offset=20, limit=10)  # 21-30번 일기

# 문제:
# - offset=1000이면 1000개를 건너뛰어야 함 (느림)
# - 새 데이터 추가 시 중복/누락 가능
```

**Cursor 방식의 장점**:
```python
# Cursor 방식 (효율적)
diaries, cursor = get_diaries(limit=10)              # 최근 10개
more, cursor = get_diaries(cursor=cursor, limit=10)  # 다음 10개

# 장점:
# - 항상 O(1) 시작 (마지막 위치에서 시작)
# - 데이터 추가되어도 중복/누락 없음
# - 무한 스크롤에 최적화
```

#### 구현 예시

```python
# domain/interfaces/diary_repository.py
class DiaryRepositoryInterface(ABC):
    @abstractmethod
    def list_diaries(
        self,
        cursor: Optional[str] = None,
        limit: int = 30,
    ) -> Tuple[List[Diary], Optional[str]]:
        """
        Returns:
            (일기 리스트, 다음 커서)
            - 일기 리스트: 최신순 정렬
            - 다음 커서: None이면 마지막 페이지
        """
        pass

# 사용 예시
# 첫 페이지
diaries, next_cursor = diary_service.list_diaries(limit=10)
for diary in diaries:
    print(diary.get_formatted_date(), diary.content[:50])

# 다음 페이지
if next_cursor:
    more_diaries, next_cursor = diary_service.list_diaries(
        cursor=next_cursor,
        limit=10
    )
```

#### 장점
- ✅ **성능**: 대량 데이터에서도 일정한 속도
- ✅ **안정성**: 새 데이터 추가 시에도 중복/누락 없음
- ✅ **확장성**: MongoDB, PostgreSQL 모두 지원 가능
- ✅ **무한 스크롤**: 모바일/웹 UI에 최적화

---

## 의존성 주입 (실제 구현)

`main.py`에서 모든 의존성을 조립:

```python
# main.py - 애플리케이션 진입점
from diary.data.repositories import (
    FileSystemCredentialRepository,
    FileSystemUserPreferencesRepository,
    FileSystemWritingStyleExamplesRepository,
    FileSystemChatRepository,
    # FileSystemDiaryRepository,  # ← 구현 예정
    OpenAIClient,
    AnthropicClient,
    GoogleAIClient,
)
from diary.domain.services import (
    CredentialService,
    UserPreferencesService,
    ChatService,
    # DiaryService,  # ← 구현 예정
)
from diary.domain.entities import AIProvider
from diary.presentation.cli import DiaryApp

# Data Layer - Repository 구현체
credential_repo = FileSystemCredentialRepository()
preferences_repo = FileSystemUserPreferencesRepository()
examples_repo = FileSystemWritingStyleExamplesRepository()
# diary_repo = FileSystemDiaryRepository()  # ← 구현 예정

# Domain Layer - Business Logic (인터페이스에만 의존)
credential_service = CredentialService(credential_repo)
preferences_service = UserPreferencesService(
    preferences_repo,
    examples_repo  # 선택적 의존성
)

# AI Client 선택 (기본 AI 기준) ⭐ NEW
default_ai = credential_service.get_default_credential()
if default_ai:
    if default_ai.provider == AIProvider.OPENAI:
        ai_client = OpenAIClient(api_key=default_ai.api_key)
    elif default_ai.provider == AIProvider.ANTHROPIC:
        ai_client = AnthropicClient(api_key=default_ai.api_key)
    elif default_ai.provider == AIProvider.GOOGLE:
        ai_client = GoogleAIClient(api_key=default_ai.api_key)

    # Chat Repository 및 Chat Service 생성
    chat_repo = FileSystemChatRepository()
    chat_service = ChatService(
        chat_repo=chat_repo,
        ai_client=ai_client,
        preferences_service=preferences_service
    )
else:
    # AI 설정이 없으면 None (첫 실행 시)
    chat_service = None

# Presentation Layer - CLI (Domain에만 의존)
diary_app = DiaryApp(
    credential_service,
    preferences_service,
    chat_service  # 선택적 의존성 ⭐ NEW
)

# 실행
diary_app.run()
```

**핵심**:
- `main.py`만 모든 레이어를 알고 있음
- Domain/Presentation은 구현체를 모름
- 나중에 DB로 교체 시 `main.py`만 수정

---

## 실제 디렉토리 구조

```
daily-cli/
├── diary/
│   ├── presentation/                    # Presentation Layer
│   │   ├── __init__.py
│   │   ├── cli.py                       # 메인 CLI (오케스트레이터)
│   │   ├── api_key_ui.py                # API Key 관리 UI
│   │   ├── preferences_ui.py            # 사용자 설정 UI
│   │   └── chat_ui.py                   # AI 채팅 UI ⭐ NEW
│   ├── domain/                          # Domain Layer
│   │   ├── entities/                    # 도메인 엔티티
│   │   │   ├── __init__.py
│   │   │   ├── ai_credential.py         # AI 인증 정보
│   │   │   ├── user_preferences.py      # 사용자 설정
│   │   │   ├── writing_style.py         # 일기 작성 스타일
│   │   │   ├── chat_message.py          # 채팅 메시지 ⭐ NEW
│   │   │   ├── chat_session.py          # 채팅 세션 ⭐ NEW
│   │   │   └── diary.py                 # 일기 ⭐ NEW
│   │   ├── services/                    # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── credential_service.py
│   │   │   ├── user_preferences_service.py
│   │   │   ├── chat_service.py          # 채팅 로직 ⭐ NEW
│   │   │   └── diary_service.py         # 일기 CRUD 로직 ⭐ NEW
│   │   └── interfaces/                  # Repository 인터페이스
│   │       ├── __init__.py
│   │       ├── credential_repository.py
│   │       ├── user_preferences_repository.py
│   │       ├── writing_style_examples_repository.py
│   │       ├── ai_client.py             # AI API 인터페이스 ⭐ NEW
│   │       ├── chat_repository.py       # 채팅 저장소 인터페이스 ⭐ NEW
│   │       └── diary_repository.py      # 일기 저장소 인터페이스 ⭐ NEW
│   └── data/                            # Data Layer
│       └── repositories/                # Repository 구현체
│           ├── __init__.py
│           ├── file_credential_repository.py
│           ├── file_user_preferences_repository.py
│           ├── file_writing_style_examples_repository.py
│           ├── file_chat_repository.py  # 채팅 JSON 저장 ⭐ NEW
│           ├── openai_client.py         # OpenAI API 클라이언트 ⭐ NEW
│           ├── anthropic_client.py      # Anthropic API 클라이언트 ⭐ NEW
│           └── google_ai_client.py      # Google AI API 클라이언트 ⭐ NEW
├── data/                                # 실제 데이터 저장
│   ├── credentials.json                 # AI API Keys
│   ├── user_preferences.json            # 사용자 설정
│   ├── writing_examples/                # 예시 문장
│   │   ├── README.md                    # 사용 가이드
│   │   └── emotional_literary.txt       # 감성적 스타일 예시
│   ├── chats/                           # 채팅 데이터 ⭐ NEW
│   │   ├── {session-id}.json            # 각 세션 대화 기록
│   │   └── active_session.json          # 현재 활성 세션
│   └── diaries/                         # 일기 데이터 ⭐ NEW
│       └── {diary-id}.json              # 각 일기 파일
├── main.py                              # 애플리케이션 진입점 (DI 조립)
├── CLAUDE.md                            # 아키텍처 가이드
├── pyproject.toml                       # 의존성 관리 (uv 사용)
├── Dockerfile                           # Docker 설정
├── Makefile                             # Docker 명령어
└── README.md
```

---

## 확장 시나리오

### Phase 1: CLI 로컬 앱 (현재)
```
Presentation: CLI (Typer + Rich) + UI 컴포넌트 분리
Domain: API Key 관리, 사용자 설정, 일기 관리, AI 채팅
Data: 로컬 파일 시스템 (JSON + TXT) + MongoDB (선택)
```

### Phase 2: 서버 + DB 추가
```
Presentation: CLI (동일)
Domain: API Key 관리, 사용자 설정, 일기 관리, AI 채팅 (동일)
Data: PostgreSQL/MongoDB + API Server
```
**변경사항**: `main.py`에서 Repository 구현체만 교체
```python
# Before
credential_repo = FileSystemCredentialRepository()

# After
credential_repo = DatabaseCredentialRepository(db_connection)
```

### Phase 3: 웹/모바일 앱 추가
```
Presentation: CLI + Web(React) + Mobile(Swift)
Domain: 동일 (API로 제공)
Data: PostgreSQL + API Server (동일)
```
**변경사항**: Presentation Layer만 추가, Domain/Data 재사용

---

## 디자인 패턴 및 베스트 프랙티스

### 1. 단일 책임 원칙 (SRP)
- `DiaryApp`: 메인 플로우 오케스트레이션만
- `ApiKeyUI`: API Key 관리 UI만
- `PreferencesUI`: 사용자 설정 UI만
- `ChatUI`: AI 채팅 UI만 ⭐ NEW

### 2. 의존성 역전 원칙 (DIP)
- Domain이 인터페이스 정의
- Data Layer가 인터페이스 구현
- 의존 방향: Data → Domain (역전!)

### 3. 선택적 의존성 (Optional Dependencies)
```python
def __init__(
    self,
    required_repo: RequiredInterface,
    optional_repo: Optional[OptionalInterface] = None
):
    # 필수 기능: required_repo 사용
    # 추가 기능: optional_repo가 있으면 사용
```

### 4. 콜백 패턴 (느슨한 결합)
```python
# UI 컴포넌트가 메인 메뉴로 돌아가기
self.preferences_ui.show_menu(on_back_callback=self._show_menu)
```

### 5. 엔티티에 비즈니스 로직 포함
```python
class UserPreferences:
    def change_writing_style(self, new_style):
        """엔티티 자체가 변경 로직 보유"""
        if not isinstance(new_style, WritingStyle):
            raise ValueError("유효한 스타일이 아님")
        self.writing_style = new_style
        self.updated_at = datetime.now()
```

---

## 핵심 원칙 요약

1. **Domain은 아무것도 의존하지 않음**: 가장 안쪽, 순수 비즈니스 로직
2. **인터페이스는 Domain이 정의**: Data Layer가 이를 구현 (의존성 역전)
3. **Presentation은 Domain에만 의존**: UI는 비즈니스 로직 호출
4. **Data Layer는 교체 가능**: 파일 → DB → API로 쉽게 전환 (같은 인터페이스)
5. **확장 시 기존 코드는 최소 변경**: 새로운 구현체 추가로 확장
6. **UI 컴포넌트 분리**: 단일 책임 원칙으로 유지보수성 향상
7. **선택적 기능**: 필수 기능 + 선택적 기능으로 점진적 확장

**의존성 흐름**:
```
Presentation → Domain ← Data
                ↑
            (인터페이스 정의)
```

이 구조를 따르면, CLI → 웹 → 모바일로 확장해도 핵심 로직은 재사용 가능합니다.
