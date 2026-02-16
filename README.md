# Daily CLI

AI와 대화하며 작성하는 일기 앱

## 설치

```bash
# uv로 의존성 설치
uv sync
```

## 실행

```bash
# uv run으로 실행
uv run diary
```

또는 가상환경 활성화 후:

```bash
source .venv/bin/activate
diary
```

## 아키텍처

레이어드 아키텍처 + 의존성 역전 원칙 (DIP)

- **Presentation Layer**: CLI 인터페이스 (Typer + Rich)
- **Domain Layer**: 비즈니스 로직 (순수, 의존성 없음)
- **Data Layer**: 데이터 저장 및 외부 API

자세한 내용은 [CLAUDE.md](./CLAUDE.md) 참조
