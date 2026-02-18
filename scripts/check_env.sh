#!/bin/bash
# 환경 변수 검증 스크립트

set -e

echo "🔍 환경 변수 보안 검사 시작..."
echo ""

# .env 파일 존재 확인
if [ ! -f .env ]; then
  echo "❌ .env 파일이 없습니다."
  echo ""
  echo "다음 명령어로 생성하세요:"
  echo "  cp .env.example .env"
  echo ""
  echo "생성 후 .env 파일의 비밀번호를 반드시 변경하세요!"
  exit 1
fi

echo "✅ .env 파일이 존재합니다."

# 기본 비밀번호 사용 확인
if grep -q "CHANGE_THIS_PASSWORD" .env; then
  echo ""
  echo "⚠️  경고: 기본 비밀번호를 사용 중입니다!"
  echo ""
  echo "보안을 위해 .env 파일의 다음 항목을 변경하세요:"
  echo "  - MONGODB_PASSWORD"
  echo "  - ME_CONFIG_BASICAUTH_PASSWORD"
  echo ""
  echo "강력한 비밀번호 생성 방법:"
  echo "  openssl rand -base64 32"
  echo ""
  exit 1
fi

echo "✅ 기본 비밀번호를 변경했습니다."

# .gitignore에 .env 포함 확인
if ! grep -q "^\.env$" .gitignore 2>/dev/null; then
  echo ""
  echo "⚠️  경고: .env가 .gitignore에 없습니다!"
  echo ""
  echo "다음 명령어로 추가하세요:"
  echo "  echo '.env' >> .gitignore"
  echo ""
  exit 1
fi

echo "✅ .env가 .gitignore에 포함되어 있습니다."

# Git에 .env가 추가되지 않았는지 확인
if git ls-files --error-unmatch .env 2>/dev/null; then
  echo ""
  echo "❌ 위험: .env 파일이 Git에 추적되고 있습니다!"
  echo ""
  echo "즉시 제거하세요:"
  echo "  git rm --cached .env"
  echo "  git commit -m 'Remove .env from Git tracking'"
  echo ""
  exit 1
fi

echo "✅ .env가 Git에 추적되지 않습니다."
echo ""
echo "🎉 환경 변수 보안 검사 통과!"
