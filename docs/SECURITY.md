# 보안 가이드

## 🔐 중요한 보안 원칙

### 1. 환경 변수 파일 (.env) 관리

**절대 하지 말아야 할 것:**
- ❌ `.env` 파일을 Git에 커밋
- ❌ 기본 비밀번호 (`admin123`) 그대로 사용
- ❌ 환경 변수를 소스 코드에 하드코딩
- ❌ `.env` 파일을 공개 저장소에 업로드

**반드시 해야 할 것:**
- ✅ `.env.example`을 복사해서 `.env` 생성
- ✅ `.env` 파일의 비밀번호 변경
- ✅ `.env`는 로컬에만 보관
- ✅ `.gitignore`에 `.env` 포함 확인

---

## 📝 초기 설정 (처음 한 번만)

### Step 1: 환경 변수 파일 생성

```bash
# .env.example 복사
cp .env.example .env
```

### Step 2: 비밀번호 변경

`.env` 파일을 열어서 다음 항목을 **강력한 비밀번호**로 변경:

```bash
# ❌ 절대 이대로 사용하지 마세요!
MONGODB_PASSWORD=CHANGE_THIS_PASSWORD

# ✅ 강력한 비밀번호로 변경 (예시)
MONGODB_PASSWORD=MyStr0ng!P@ssw0rd#2024

# Mongo Express 비밀번호도 변경
ME_CONFIG_BASICAUTH_PASSWORD=An0th3r$tr0ngP@ss
```

### Step 3: 권한 설정 (선택사항, 권장)

```bash
# .env 파일을 본인만 읽을 수 있도록 설정 (macOS/Linux)
chmod 600 .env
```

---

## 🚨 .gitignore 확인

`.env` 파일이 Git에 추적되지 않는지 확인:

```bash
# .gitignore 확인
cat .gitignore | grep ".env"

# 출력 예시 (이미 포함되어 있어야 함):
# .env
# .env.local
```

만약 `.env`가 `.gitignore`에 없다면 추가:

```bash
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

---

## 🔒 프로덕션 환경 보안

### 1. 환경 변수 관리 도구 사용

프로덕션에서는 `.env` 파일 대신 **안전한 비밀 관리 서비스** 사용:

**AWS 환경:**
```bash
# AWS Secrets Manager
aws secretsmanager get-secret-value --secret-id daily-cli/mongodb

# AWS Systems Manager Parameter Store
aws ssm get-parameter --name /daily-cli/mongodb-password --with-decryption
```

**Docker Swarm/Kubernetes:**
```bash
# Docker Secrets
docker secret create mongodb_password /path/to/secret

# Kubernetes Secrets
kubectl create secret generic mongodb-creds \
  --from-literal=username=admin \
  --from-literal=password=YourStrongPassword
```

### 2. Docker Compose Secrets (Docker Swarm)

```yaml
# docker-compose.prod.yml
services:
  mongodb:
    environment:
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/mongodb_password
    secrets:
      - mongodb_password

secrets:
  mongodb_password:
    external: true
```

### 3. 환경별 설정 분리

```
.env.development   # 개발 환경 (약한 비밀번호 허용)
.env.staging       # 스테이징 (프로덕션과 유사)
.env.production    # 프로덕션 (강력한 비밀번호 필수)
```

---

## 🛡️ MongoDB 보안 강화

### 1. 네트워크 제한

```yaml
# docker-compose.yml
services:
  mongodb:
    # 외부 접근 차단 (포트 노출 제거)
    # ports:
    #   - "27017:27017"  # 주석 처리
    networks:
      - daily-network  # 내부 네트워크만 사용
```

### 2. 읽기 전용 사용자 생성

```javascript
// MongoDB 쉘에서 실행
use daily_diary

db.createUser({
  user: "readonly_user",
  pwd: "ReadOnlyPassword123!",
  roles: [{ role: "read", db: "daily_diary" }]
})

db.createUser({
  user: "app_user",
  pwd: "AppUserPassword456!",
  roles: [{ role: "readWrite", db: "daily_diary" }]
})
```

### 3. IP 화이트리스트 (MongoDB Atlas 사용 시)

```
허용 IP:
- 개발 환경: 127.0.0.1/32
- 프로덕션 서버: [서버 IP]/32
```

---

## 🔍 보안 체크리스트

배포 전에 확인:

- [ ] `.env` 파일이 `.gitignore`에 포함됨
- [ ] 기본 비밀번호(`admin123`)를 변경함
- [ ] MongoDB 관리자 계정을 변경함
- [ ] Mongo Express 인증 정보를 변경함
- [ ] 프로덕션에서는 외부 포트 노출 최소화
- [ ] HTTPS 사용 (프로덕션 환경)
- [ ] 정기적인 백업 설정
- [ ] 로그에 민감한 정보가 남지 않도록 설정

---

## 🚨 비밀번호가 노출되었다면?

### 즉시 조치:

1. **비밀번호 즉시 변경**
```bash
# .env 파일 수정
vi .env

# Docker 컨테이너 재시작
make down-db
make up-db
```

2. **Git 히스토리에서 제거** (커밋한 경우)
```bash
# Git 히스토리에서 완전 제거
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 강제 푸시 (주의!)
git push origin --force --all
```

3. **GitHub Secrets 사용** (공개 저장소인 경우)
```bash
# GitHub Actions Secrets에 등록
Settings > Secrets and variables > Actions > New repository secret
```

---

## 📚 참고 자료

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [Docker Secrets Documentation](https://docs.docker.com/engine/swarm/secrets/)
- [12 Factor App - Config](https://12factor.net/config)

---

## 💡 추가 보안 팁

### 비밀번호 생성 도구

```bash
# 강력한 랜덤 비밀번호 생성 (macOS/Linux)
openssl rand -base64 32

# Python으로 생성
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 환경 변수 검증 스크립트

```bash
# scripts/check_env.sh
#!/bin/bash

if [ ! -f .env ]; then
  echo "❌ .env 파일이 없습니다. .env.example을 복사하세요."
  exit 1
fi

if grep -q "CHANGE_THIS_PASSWORD" .env; then
  echo "⚠️  기본 비밀번호를 사용 중입니다. 보안을 위해 변경하세요!"
  exit 1
fi

echo "✅ 환경 변수 검증 완료"
```

---

**핵심 원칙: 비밀은 코드에 넣지 말고, 환경 변수로 관리하라!**
