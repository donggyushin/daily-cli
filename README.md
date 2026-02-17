# Daily CLI

AI와 대화하며 작성하는 일기 앱

## 주요 기능

- ✅ **AI API 키 관리**: OpenAI, Anthropic, Google AI 지원
- ✅ **생성자 주입 방식**: 명시적 의존성 주입 (Constructor Injection)
- ✅ **레이어드 아키텍처**: Domain, Data, Presentation 분리
- ✅ **AI 대화형 채팅**: AI와 자연스럽게 대화하며 하루 기록

## 빠른 시작

### 1. 로컬 실행 (권장)

```bash
# 의존성 설치
uv sync

# 실행
python main.py
```

최초 실행 시 API 키 등록이 필요합니다:
1. 사용할 AI 서비스 선택 (OpenAI/Anthropic/Google)
2. API 키 입력
3. 메인 메뉴 진입

### 2. Docker 사용

```bash
# 빌드
make build

# 실행
make run

# 개발 모드
make dev
```

## 사용 예제

### 메인 기능

```bash
# CLI 실행
uv run python main.py

# 메뉴에서 선택
1. Write Diary          # AI와 대화하며 하루 기록 ⭐
2. Manage API Keys      # API 키 관리
3. Manage Preferences   # 사용자 설정 (일기 스타일 선택)
4. Exit
```

### AI 채팅 기능

```bash
# Write Diary 선택 후
AI: 안녕하세요! 오늘 하루는 어떠셨나요?
You: 오늘은 프로젝트 마감이라 정신없었어요.

AI: 프로젝트 마감이라 정말 바쁘셨겠네요. 어떤 프로젝트였나요?
You: 새로운 기능 개발이었는데, 버그가 좀 많이 나와서...

# 대화가 충분히 쌓이면 AI가 일기 작성 제안
AI: 오늘 대화를 바탕으로 일기를 작성해드릴까요?

# 종료: 'quit', 'exit', '그만'
# → 대화 내용이 data/chats/ 폴더에 저장됨
```

### 프로그래밍 방식 사용

```python
from diary.data.repositories import FileSystemCredentialRepository
from diary.domain.services import CredentialService
from diary.domain.entities import AIProvider

# 의존성 조립 (Dependency Injection)
repo = FileSystemCredentialRepository()
service = CredentialService(repo)

# API 키 저장
service.save_credential(
    provider=AIProvider.OPENAI,
    api_key="sk-proj-xxx"
)

# 기본 AI 조회
default = service.get_default_credential()
print(f"사용 중인 AI: {default.provider.value}")
```

## 아키텍처

레이어드 아키텍처 + 의존성 역전 원칙 (DIP)

- **Presentation Layer**: CLI 인터페이스 (Typer + Rich)
- **Domain Layer**: 비즈니스 로직 (순수, 의존성 없음)
- **Data Layer**: 데이터 저장 및 외부 API

자세한 내용은 [CLAUDE.md](./CLAUDE.md) 참조
