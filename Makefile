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

# MongoDB 관련
check-env: ## 환경 변수 보안 검사
	@bash scripts/check_env.sh

setup-env: ## .env 파일 생성 (처음 한 번만)
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "✅ .env 파일이 생성되었습니다."; \
		echo "⚠️  반드시 .env 파일의 비밀번호를 변경하세요!"; \
		echo ""; \
		echo "편집: vi .env"; \
	else \
		echo "ℹ️  .env 파일이 이미 존재합니다."; \
	fi

status-db: ## MongoDB 상태 확인
	@bash scripts/check_mongodb_status.sh

up-db: setup-env check-env ## MongoDB 서비스 시작 (환경 변수 검증 포함)
	docker compose up -d mongodb mongo-express

restart-db: ## MongoDB 재시작 (환경 변수 다시 로드)
	docker compose down mongodb mongo-express
	docker compose up -d mongodb mongo-express
	@echo "✅ MongoDB 재시작 완료"

recreate-db: ## MongoDB 완전 재생성 (⚠️ 데이터 유지, 컨테이너만 재생성)
	docker compose up -d --force-recreate --no-deps mongodb mongo-express
	@echo "✅ MongoDB 컨테이너 재생성 완료"

reset-db: ## MongoDB 완전 초기화 (⚠️ 모든 데이터 삭제!)
	@echo "⚠️  경고: 모든 MongoDB 데이터가 삭제됩니다!"
	@read -p "계속하시겠습니까? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		docker compose down mongodb mongo-express; \
		docker volume rm daily-cli_mongodb_data daily-cli_mongodb_config 2>/dev/null || true; \
		echo "✅ MongoDB 데이터 삭제 완료"; \
		echo "다시 시작: make up-db"; \
	else \
		echo "❌ 취소되었습니다."; \
	fi

down-db: ## MongoDB 서비스 중지
	docker compose down mongodb mongo-express

logs-db: ## MongoDB 로그 확인
	docker compose logs -f mongodb

mongo-shell: ## MongoDB 쉘 접속
	@docker compose exec mongodb mongosh -u $$(grep MONGODB_USERNAME .env | cut -d '=' -f2) -p $$(grep MONGODB_PASSWORD .env | cut -d '=' -f2)

# 로컬 실행 (비교용)
local: ## 로컬에서 uv run 실행
	uv run main.py
