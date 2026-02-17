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

#### 2.2 Services (비즈니스 로직)
- `CredentialService` - API Key 관리, 검증, 기본 AI 설정
- `UserPreferencesService` - 사용자 설정 관리, 강화된 프롬프트 생성

#### 2.3 Interfaces (Repository 인터페이스)
Domain이 정의하고, Data Layer가 구현:
- `CredentialRepositoryInterface`
- `UserPreferencesRepositoryInterface`
- `WritingStyleExamplesRepositoryInterface`

**핵심 원칙**:
- **Domain은 아무것도 의존하지 않음** - 가장 안쪽 레이어
- **인터페이스(추상)는 Domain이 정의**하고, Data Layer가 구현함 (의존성 역전)

**실제 예시**:
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

---

### 3. Data Layer
**책임**: 데이터 영속성, 외부 시스템 연동, **Domain 인터페이스 구현**

#### 3.1 현재 구현된 Repository

**FileSystemCredentialRepository**
- AI API Key를 JSON 파일로 저장 (`data/credentials.json`)
- 중복 방지, 기본 AI 설정 관리

**FileSystemUserPreferencesRepository**
- 사용자 설정을 JSON 파일로 저장 (`data/user_preferences.json`)

**FileSystemWritingStyleExamplesRepository** ⭐ 새로운 패턴
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

#### 3.2 확장 전략

**같은 인터페이스, 다른 구현체**:
```
초기:
- FileSystemCredentialRepository (JSON)
- FileSystemUserPreferencesRepository (JSON)
- FileSystemWritingStyleExamplesRepository (TXT)

확장 후:
- DatabaseCredentialRepository (PostgreSQL)
- DatabaseUserPreferencesRepository (PostgreSQL)
- RemoteWritingStyleExamplesRepository (API)

→ Domain/Presentation 코드는 변경 없이 Data Layer만 교체!
```

---

## 특별 기능: Few-shot Learning 시스템

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

### 아키텍처 장점
- ✅ **사용자 친화적**: 텍스트 파일만 편집
- ✅ **레이어 분리**: Domain은 파일 시스템 모름
- ✅ **선택적 기능**: 예시 파일 없어도 기본 동작
- ✅ **확장 가능**: 다른 스타일에도 동일하게 적용

---

## 의존성 주입 (실제 구현)

`main.py`에서 모든 의존성을 조립:

```python
# main.py - 애플리케이션 진입점
from diary.data.repositories import (
    FileSystemCredentialRepository,
    FileSystemUserPreferencesRepository,
    FileSystemWritingStyleExamplesRepository,
)
from diary.domain.services import CredentialService, UserPreferencesService
from diary.presentation.cli import DiaryApp

# Data Layer - Repository 구현체
credential_repo = FileSystemCredentialRepository()
preferences_repo = FileSystemUserPreferencesRepository()
examples_repo = FileSystemWritingStyleExamplesRepository()

# Domain Layer - Business Logic (인터페이스에만 의존)
credential_service = CredentialService(credential_repo)
preferences_service = UserPreferencesService(
    preferences_repo,
    examples_repo  # 선택적 의존성
)

# Presentation Layer - CLI (Domain에만 의존)
diary_app = DiaryApp(credential_service, preferences_service)

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
│   │   ├── cli.py                       # 메인 CLI (110줄, 간결함)
│   │   ├── api_key_ui.py                # API Key 관리 UI
│   │   └── preferences_ui.py            # 사용자 설정 UI
│   ├── domain/                          # Domain Layer
│   │   ├── entities/                    # 도메인 엔티티
│   │   │   ├── __init__.py
│   │   │   ├── ai_credential.py         # AI 인증 정보
│   │   │   ├── user_preferences.py      # 사용자 설정
│   │   │   └── writing_style.py         # 일기 작성 스타일
│   │   ├── services/                    # 비즈니스 로직
│   │   │   ├── __init__.py
│   │   │   ├── credential_service.py
│   │   │   └── user_preferences_service.py
│   │   └── interfaces/                  # Repository 인터페이스
│   │       ├── __init__.py
│   │       ├── credential_repository.py
│   │       ├── user_preferences_repository.py
│   │       └── writing_style_examples_repository.py
│   └── data/                            # Data Layer
│       └── repositories/                # Repository 구현체
│           ├── __init__.py
│           ├── file_credential_repository.py
│           ├── file_user_preferences_repository.py
│           └── file_writing_style_examples_repository.py
├── data/                                # 실제 데이터 저장
│   ├── credentials.json                 # AI API Keys
│   ├── user_preferences.json            # 사용자 설정
│   └── writing_examples/                # 예시 문장
│       ├── README.md                    # 사용 가이드
│       └── emotional_literary.txt       # 감성적 스타일 예시
├── main.py                              # 애플리케이션 진입점 (DI 조립)
├── CLAUDE.md                            # 아키텍처 가이드
├── requirements.txt
└── README.md
```

---

## 확장 시나리오

### Phase 1: CLI 로컬 앱 (현재)
```
Presentation: CLI (Typer + Rich) + UI 컴포넌트 분리
Domain: API Key 관리, 사용자 설정, 일기 스타일
Data: 로컬 파일 시스템 (JSON + TXT)
```

### Phase 2: 서버 + DB 추가
```
Presentation: CLI (동일)
Domain: API Key 관리, 사용자 설정, 일기 스타일 (동일)
Data: PostgreSQL + API Server
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
