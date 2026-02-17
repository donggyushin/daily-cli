.PHONY: help build run dev shell clean

help: ## 도움말 표시
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

build: ## Docker 이미지 빌드
	docker compose build

run: ## CLI 실행 (hello world)
	docker compose run --rm daily-cli

dev: ## 개발 컨테이너 실행
	docker compose run --rm dev

shell: ## 프로덕션 컨테이너 쉘 접속
	docker compose run --rm daily-cli bash

clean: ## Docker 이미지 삭제
	docker compose down
	docker rmi daily-cli:latest daily-cli:dev 2>/dev/null || true

rebuild: clean build ## 완전 재빌드

# 로컬 실행 (비교용)
local: ## 로컬에서 uv run 실행
	uv run main.py
