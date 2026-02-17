# Daily CLI

AI와 대화하며 작성하는 일기 앱

## 주요 기능

- ✅ **AI API 키 관리**: OpenAI, Anthropic, Google AI 지원
- ✅ **생성자 주입 방식**: 명시적 의존성 주입 (Constructor Injection)
- ✅ **레이어드 아키텍처**: Domain, Data, Presentation 분리
- 🚧 **AI 대화형 일기 작성**: 구현 예정

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

### API 키 관리

```bash
# CLI 실행
python main.py

# 메뉴에서 선택
1. Write Diary          # 일기 작성 (구현 예정)
2. Manage API Keys      # API 키 관리
3. Exit
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
