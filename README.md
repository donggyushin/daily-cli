# Daily CLI

AI와 대화하며 작성하는 일기 앱

## 실행 방법

### 1. Docker 사용 (권장)

```bash
# 빌드
make build

# 실행
make run

# 개발 모드 (소스 코드 수정 가능)
make dev
```

<details>
<summary>Docker Compose 직접 사용</summary>

```bash
# 빌드
docker compose build

# 실행
docker compose run --rm daily-cli

# 개발 컨테이너
docker compose run --rm dev
```
</details>

### 2. 로컬 실행 (uv)

```bash
# 의존성 설치
uv sync

# 실행
uv run diary

# 또는 가상환경 활성화 후
source .venv/bin/activate
diary
```

## 아키텍처

레이어드 아키텍처 + 의존성 역전 원칙 (DIP)

- **Presentation Layer**: CLI 인터페이스 (Typer + Rich)
- **Domain Layer**: 비즈니스 로직 (순수, 의존성 없음)
- **Data Layer**: 데이터 저장 및 외부 API

자세한 내용은 [CLAUDE.md](./CLAUDE.md) 참조
