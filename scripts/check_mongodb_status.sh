#!/bin/bash
# MongoDB 상태 확인 스크립트

echo "🔍 MongoDB 상태 확인..."
echo ""

# 실행 중인 컨테이너 확인
if docker compose ps mongodb | grep -q "Up"; then
  echo "✅ MongoDB 컨테이너가 실행 중입니다."
  echo ""

  # 볼륨 확인
  if docker volume ls | grep -q "daily-cli_mongodb_data"; then
    echo "📦 MongoDB 데이터 볼륨이 존재합니다."
    echo ""
    echo "⚠️  주의: 이미 초기화된 데이터베이스가 있습니다."
    echo "비밀번호를 변경하려면 볼륨을 삭제하고 재생성해야 합니다."
  fi
else
  echo "❌ MongoDB 컨테이너가 실행 중이 아닙니다."
fi

echo ""
echo "현재 실행 중인 서비스:"
docker compose ps
