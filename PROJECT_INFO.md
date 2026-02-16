# AI 대화형 일기 앱 (CLI)

## 프로젝트 개요
AI와 대화하며 일기를 작성하는 터미널 기반 일기 앱

## 프로젝트명
**현재 상태**: 미정 (추후 결정)

**후보 목록**:
- `dlog` - diary log 약어, 짧고 타이핑 편함
- `logmate` - 일기 친구, 친근한 느낌
- `jot` - 영어로 "휘갈겨 쓰다", 세련됨
- `daylog`, `talklog`, `diario` 등

**참고**: GitHub Repository 이름은 언제든지 변경 가능

---

## 아키텍처 패턴

**레이어드 아키텍처 (Layered Architecture)** 적용

- **Presentation Layer**: CLI UI, 사용자 인터랙션
- **Domain Layer**: 비즈니스 로직, 엔티티 (프레임워크 독립적)
- **Data Layer**: 데이터 저장, 외부 API 연동 (교체 가능)

### 확장 계획
1. **Phase 1 (초기)**: CLI + 로컬 파일 저장
2. **Phase 2**: 서버 + 데이터베이스 (Data Layer만 교체)
3. **Phase 3**: 웹/모바일 앱 (Presentation Layer 추가, Domain 재사용)

**상세 내용**: `CLAUDE.md` 참조

---

## 핵심 기능

### 1. 대화형 일기 작성
- **방식**: AI가 사용자의 답변에 따라 자연스럽게 질문을 이어가는 자유 대화 형식
- **길이**: 5-10개 질문 정도 (약 10분)
- **종료 조건**: AI가 일기 작성에 충분한 정보를 얻었다고 판단하면 일기 작성 버튼 활성화
- **데이터 저장**: 대화 내용 및 생성된 일기 저장

### 2. AI 일기 자동 생성
대화 내용을 기반으로 AI가 일기 작성. 사용자는 3가지 스타일 중 선택 가능:
- **스타일 1**: 객관적 3인칭 ("그는 오늘 피곤한 하루를 보냈다")
- **스타일 2**: 1인칭 자서전 ("오늘은 피곤한 하루였다")
- **스타일 3**: 감성적/문학적 ("긴 회의들 사이로 피로가 밀려왔다")

### 3. 저장 & 조회 기능
```bash
$ diary              # 오늘 일기 쓰기 (대화 시작)
$ diary show         # 오늘 일기 보기
$ diary show -d 3    # 3일 전 일기 보기
$ diary list         # 모든 일기 목록
$ diary search "회의" # 키워드로 일기 검색
```

### 4. 특별 기능
- **일주일/한 달 요약**: AI가 일정 기간의 일기를 분석하여 요약 제공
- **기분 트래킹**: 매일 기분 기록 및 추이 확인
- **사진/링크 첨부**: 일기에 관련 사진이나 링크 첨부 가능

---

## 기술 스택

### 언어
- Python 3.x

### 주요 라이브러리 (예상)
- **CLI UI**: Rich (터미널 스타일링), Typer (명령어 프레임워크)
- **대화형 입력**: Prompt Toolkit
- **AI**: OpenAI API, Anthropic Claude API 등
- **데이터 저장**: JSON, SQLite 또는 로컬 파일 시스템

### API
- **API Key**: 사용자가 직접 입력 및 관리
- 비용은 사용자 부담

---

## 사용자 요구사항

### 개발자 배경
- iOS 개발자 (Swift 주력)
- 파이썬 경험: FastAPI, crewAI 사용 경험 있음
- 터미널 환경 선호 (nvim 사용자)
- 키보드 중심 워크플로우

### 프로젝트 목표
- **우선순위**: 재미 > 실용성
- **투자 시간**: 주 2-3시간
- **기간**: 장기 프로젝트
- **AI 활용**: 적극 활용 (비용 부담 가능)

---

## 프로젝트 구조 (레이어드 아키텍처)

```
diary-cli/
├── diary/
│   ├── presentation/           # Presentation Layer
│   │   ├── cli.py              # CLI 명령어 (Typer)
│   │   └── ui.py               # UI 컴포넌트 (Rich)
│   ├── domain/                 # Domain Layer
│   │   ├── entities/           # 도메인 엔티티
│   │   │   ├── diary.py
│   │   │   ├── conversation.py
│   │   │   └── mood.py
│   │   ├── services/           # 비즈니스 로직
│   │   │   ├── conversation_service.py
│   │   │   ├── diary_writer_service.py
│   │   │   └── mood_tracker_service.py
│   │   └── interfaces/         # Repository 인터페이스
│   │       └── diary_repository.py
│   └── data/                   # Data Layer
│       ├── repositories/       # Repository 구현체
│       │   ├── file_diary_repository.py      # Phase 1
│       │   └── db_diary_repository.py        # Phase 2+
│       ├── api/                # 외부 API
│       │   └── ai_client.py
│       └── config/             # 설정 관리
│           └── config_manager.py
├── data/                       # 실제 데이터 저장 (로컬 파일)
├── tests/
├── requirements.txt
├── README.md
├── PROJECT_INFO.md             # 이 파일
└── CLAUDE.md                   # 아키텍처 상세 가이드
```

**핵심 원칙**:
- Domain Layer는 Data Layer를 **인터페이스로만** 의존
- Data Layer 교체 시 Domain/Presentation 코드는 변경 없음
- 상세 내용은 `CLAUDE.md` 참조

---

## 개발 단계

### Phase 1: MVP (CLI + 로컬 파일)
- 레이어드 아키텍처 기반 프로젝트 구조 세팅
- 기본 CLI 명령어 (write, show, list)
- AI 자유 대화 기반 일기 작성
- 3가지 스타일 선택
- 로컬 파일 시스템 저장 (JSON)
- 기분 트래킹 기본 기능

### Phase 2: 고급 기능
- 검색 기능
- 일주일/한 달 요약
- 사진/링크 첨부
- UI 개선 (Rich 활용)

### Phase 3: 서버 + DB
- API 서버 구축 (FastAPI)
- Data Layer 교체 (파일 → PostgreSQL)
- 사용자 계정 기능

### Phase 4: 멀티 플랫폼
- 웹 프론트엔드 (React)
- iOS 앱 (Swift)
- Domain Layer 재사용

---

## 참고사항
- 터미널 감성 중시
- 키보드만으로 모든 조작 가능해야 함
- ASCII 아트나 시각적 요소 활용 가능
- 사용자가 하루에 한 번이라도 실행하면 성공
- GitHub Repository 이름은 추후 언제든지 변경 가능
- 코드 작업 시 레이어드 아키텍처 원칙 준수 (상세: `CLAUDE.md`)
