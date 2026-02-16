# uv 공식 이미지 사용 (Python 3.13)
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# 작업 디렉토리 설정
WORKDIR /app

# uv 환경 변수 설정
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 의존성 파일 먼저 복사 (캐싱 활용)
COPY pyproject.toml uv.lock ./

# 의존성 설치 (소스 없이)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 소스 코드 복사
COPY . .

# 프로젝트 설치
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 런타임 이미지
FROM python:3.13-slim-bookworm

# 작업 디렉토리 설정
WORKDIR /app

# builder에서 가상환경 복사
COPY --from=builder /app/.venv /app/.venv

# 소스 코드 복사
COPY --from=builder /app/diary /app/diary

# PATH에 가상환경 추가
ENV PATH="/app/.venv/bin:$PATH"

# 기본 명령어
ENTRYPOINT ["diary"]
CMD ["--help"]
