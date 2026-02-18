# 보안 개선 변경 사항

## 🔐 문제점 및 해결책

### ❌ 이전 문제점

Docker Compose 파일에 MongoDB 계정 정보가 **하드코딩**되어 있었습니다:

```yaml
# docker-compose.yml (이전)
environment:
  - MONGO_INITDB_ROOT_USERNAME=admin      # ❌ 하드코딩
  - MONGO_INITDB_ROOT_PASSWORD=admin123   # ❌ 하드코딩 (약한 비밀번호)
```

**보안 위험:**
- Git에 커밋되면 비밀번호 노출
- 공개 저장소라면 누구나 접근 가능
- 기본 비밀번호로 운영 환경 침투 가능

---

### ✅ 해결책

**환경 변수 파일 분리 + Git 제외**

```yaml
# docker-compose.yml (현재)
env_file:
  - .env  # 환경 변수 파일에서 읽기
environment:
  - MONGO_INITDB_ROOT_USERNAME=${MONGODB_USERNAME}  # ✅ 환경 변수 참조
  - MONGO_INITDB_ROOT_PASSWORD=${MONGODB_PASSWORD}  # ✅ 환경 변수 참조
```

```bash
# .env (Git에 추가 안 됨 - .gitignore에 포함)
MONGODB_USERNAME=admin
MONGODB_PASSWORD=YourStrongPassword123!  # 강력한 비밀번호
```

```bash
# .env.example (Git에 추가됨 - 예시만 포함)
MONGODB_USERNAME=admin
MONGODB_PASSWORD=CHANGE_THIS_PASSWORD  # ⚠️ 기본값 (반드시 변경)
```

---

## 📋 변경 사항 상세

### 1. **docker-compose.yml**
- 하드코딩된 비밀번호 제거
- 환경 변수 참조로 변경 (`${VARIABLE}` 문법)
- `env_file: .env` 추가

### 2. **.env.example**
- 보안 경고 주석 추가
- 기본 비밀번호를 `CHANGE_THIS_PASSWORD`로 변경 (명시적 경고)

### 3. **.gitignore**
- `.env` 파일 제외 (이미 포함됨)
- `.env.local` 추가

### 4. **scripts/check_env.sh** (신규)
- `.env` 파일 존재 여부 확인
- 기본 비밀번호 사용 여부 확인
- `.gitignore`에 `.env` 포함 여부 확인
- Git 추적 여부 확인

### 5. **Makefile**
- `make setup-env`: `.env` 파일 자동 생성
- `make check-env`: 보안 검증 실행
- `make up-db`: MongoDB 시작 전 자동 보안 검증
- `make mongo-shell`: `.env` 파일에서 비밀번호 자동 읽기

### 6. **docs/SECURITY.md** (신규)
- 보안 가이드 문서
- 비밀번호 변경 방법
- 프로덕션 배포 체크리스트
- 비밀번호 노출 시 대응 방법

### 7. **README.md** 및 **docs/MONGODB_SETUP.md**
- 초기 설정 보안 가이드 추가
- 비밀번호 변경 필수 안내

---

## 🚀 사용 방법

### 초기 설정 (처음 한 번)

```bash
# 1. 환경 변수 파일 생성
make setup-env

# 2. 비밀번호 변경 (⚠️ 필수!)
vi .env
# MONGODB_PASSWORD=CHANGE_THIS_PASSWORD  →  강력한 비밀번호로 변경
# ME_CONFIG_BASICAUTH_PASSWORD=CHANGE_THIS_PASSWORD  →  변경

# 3. 보안 검증
make check-env
```

### MongoDB 시작

```bash
# MongoDB 시작 (자동으로 보안 검증 수행)
make up-db
```

---

## 🔒 보안 체크리스트

배포 전 확인:

- [ ] `.env` 파일 생성 (`make setup-env`)
- [ ] 기본 비밀번호 변경 (`.env` 파일 수정)
- [ ] 보안 검증 통과 (`make check-env`)
- [ ] `.env`가 `.gitignore`에 포함됨
- [ ] `.env` 파일이 Git에 추적 안 됨
- [ ] 프로덕션 환경에서는 강력한 비밀번호 사용
- [ ] MongoDB 외부 포트 노출 최소화 (필요시)

---

## 📚 관련 문서

- [docs/SECURITY.md](SECURITY.md) - 상세 보안 가이드
- [docs/MONGODB_SETUP.md](MONGODB_SETUP.md) - MongoDB 설정 가이드
- [README.md](../README.md) - 프로젝트 개요

---

## 💡 핵심 원칙

**"Secrets should never be in code, always in environment variables"**

- 🔒 비밀은 코드에 넣지 말고, 환경 변수로 관리
- 🚫 환경 변수 파일(`.env`)은 Git에 커밋 금지
- ✅ 예시 파일(`.env.example`)만 Git에 포함
- 🔐 프로덕션에서는 강력한 비밀번호 필수

---

**변경일**: 2024-02-18
**보안 수준**: 개선됨 (Low → Medium)
**다음 단계**: 프로덕션 배포 시 AWS Secrets Manager/Vault 도입 검토
