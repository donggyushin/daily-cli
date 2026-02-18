# MongoDB 환경 변수 업데이트 가이드

이미 MongoDB를 실행한 후, `.env` 파일을 변경했을 때 적용하는 방법입니다.

## 📌 중요: MongoDB 초기화 메커니즘

MongoDB는 **처음 실행될 때만** 환경 변수로 계정을 생성합니다:

```
첫 실행 → 환경 변수 읽기 → 데이터 볼륨에 계정 생성 ✅
두 번째 실행 → 데이터 볼륨 존재 → 환경 변수 무시 ❌
```

즉, **이미 데이터가 있으면** 환경 변수를 바꿔도 비밀번호가 안 바뀝니다!

---

## 🔍 Step 1: 현재 상태 확인

```bash
make status-db
```

출력 예시:
```
✅ MongoDB 컨테이너가 실행 중입니다.
📦 MongoDB 데이터 볼륨이 존재합니다.
⚠️  이미 초기화된 데이터베이스가 있습니다.
```

---

## 📋 상황별 해결 방법

### 상황 1: 환경 변수만 변경 (포트, 데이터베이스명 등)

**비밀번호가 아닌** 다른 환경 변수를 변경한 경우:

```bash
# 방법 A: 재시작 (권장)
make restart-db

# 방법 B: 컨테이너만 재생성 (데이터 유지)
make recreate-db
```

---

### 상황 2: 비밀번호 변경 (데이터 유지)

**이미 데이터가 있는데 비밀번호를 바꾸고 싶은 경우**:

#### 옵션 A: MongoDB 쉘에서 비밀번호 변경 (데이터 유지) ✅

```bash
# 1. MongoDB 쉘 접속 (현재 비밀번호로)
make mongo-shell

# 2. 관리자 데이터베이스로 전환
use admin

# 3. 비밀번호 변경
db.changeUserPassword("admin", "새로운강력한비밀번호!")

# 4. 종료
exit

# 5. .env 파일도 동일한 비밀번호로 업데이트
vi .env
# MONGODB_PASSWORD=새로운강력한비밀번호!

# 6. 컨테이너 재시작 (새 환경 변수 적용)
make restart-db
```

#### 옵션 B: 컨테이너 내부에서 직접 변경

```bash
# 1. MongoDB 컨테이너 내부 진입
docker compose exec mongodb bash

# 2. MongoDB 관리자로 접속
mongosh -u admin -p 현재비밀번호

# 3. 비밀번호 변경
use admin
db.changeUserPassword("admin", "새로운강력한비밀번호!")
exit

# 4. 컨테이너 나가기
exit

# 5. .env 파일 업데이트
vi .env

# 6. 재시작
make restart-db
```

---

### 상황 3: 완전 초기화 (⚠️ 모든 데이터 삭제)

**데이터를 버려도 괜찮고, 처음부터 다시 시작하고 싶은 경우**:

```bash
# 1. .env 파일 수정
vi .env
# MONGODB_PASSWORD=새로운강력한비밀번호!

# 2. 완전 초기화 (⚠️ 모든 데이터 삭제!)
make reset-db
# 확인 메시지: yes 입력

# 3. 다시 시작 (새 비밀번호로 초기화됨)
make up-db
```

---

## 🛠️ 명령어 요약

| 명령어 | 용도 | 데이터 손실 |
|--------|------|------------|
| `make status-db` | 현재 상태 확인 | ❌ 없음 |
| `make restart-db` | 재시작 (환경 변수 다시 로드) | ❌ 없음 |
| `make recreate-db` | 컨테이너 재생성 | ❌ 없음 |
| `make reset-db` | 완전 초기화 | ⚠️ **모든 데이터 삭제!** |

---

## 💡 추천 워크플로우

### 처음 MongoDB 사용 시

```bash
# 1. 환경 변수 설정
make setup-env
vi .env  # 비밀번호 변경

# 2. 보안 검증
make check-env

# 3. 시작
make up-db
```

### 비밀번호 변경 시 (데이터 유지)

```bash
# 1. MongoDB 쉘에서 변경
make mongo-shell
# use admin
# db.changeUserPassword("admin", "새비밀번호")
# exit

# 2. .env 파일 동기화
vi .env

# 3. 재시작
make restart-db
```

### 비밀번호 변경 시 (데이터 삭제해도 됨)

```bash
# 1. .env 파일 수정
vi .env

# 2. 완전 초기화
make reset-db  # yes 입력

# 3. 다시 시작
make up-db
```

---

## 🔍 트러블슈팅

### 문제: 환경 변수를 바꿨는데 적용이 안 됨

**원인**: 컨테이너가 이전 환경 변수를 캐싱

**해결**:
```bash
make restart-db
# 또는
make recreate-db
```

### 문제: 비밀번호를 바꿨는데 로그인이 안 됨

**원인**: MongoDB는 데이터 볼륨에 저장된 비밀번호를 사용

**해결**:
```bash
# 방법 1: MongoDB 쉘에서 비밀번호 변경 (위 참조)
# 방법 2: 데이터 삭제 후 재초기화
make reset-db
make up-db
```

### 문제: 이전 비밀번호를 잊어버림

**해결**:
```bash
# 데이터를 포기하고 완전 초기화
make reset-db
make up-db
```

---

## 🎯 핵심 정리

1. **환경 변수 변경 후**: `make restart-db`로 재시작
2. **비밀번호 변경**: MongoDB 쉘에서 변경 + `.env` 동기화
3. **완전 초기화**: `make reset-db` (모든 데이터 삭제)
4. **MongoDB는 첫 실행 시만** 환경 변수로 계정 생성

---

**관련 문서**:
- [docs/SECURITY.md](SECURITY.md) - 보안 가이드
- [docs/MONGODB_SETUP.md](MONGODB_SETUP.md) - 초기 설정
