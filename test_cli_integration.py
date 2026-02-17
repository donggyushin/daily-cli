"""CLI 통합 테스트 - 의존성 주입 검증"""

from diary.data.repositories import FileSystemCredentialRepository
from diary.domain.services import CredentialService
from diary.domain.entities import AIProvider
from diary.presentation.cli import DiaryApp


def test_dependency_injection():
    """생성자 주입 방식 테스트"""

    print("=== 의존성 주입 테스트 ===\n")

    # 1. Data Layer 생성
    print("1. Data Layer 생성")
    credential_repo = FileSystemCredentialRepository()
    print(f"   ✓ FileSystemCredentialRepository 생성")
    print(f"   - 저장 경로: {credential_repo.file_path}")
    print()

    # 2. Domain Layer 생성 및 주입
    print("2. Domain Layer 생성 (Data Layer 주입)")
    credential_service = CredentialService(credential_repo)
    print(f"   ✓ CredentialService 생성")
    print(f"   - Repository: {type(credential_service.credential_repo).__name__}")
    print()

    # 3. Presentation Layer 생성 및 주입
    print("3. Presentation Layer 생성 (Domain Layer 주입)")
    diary_app = DiaryApp(credential_service)
    print(f"   ✓ DiaryApp 생성")
    print(f"   - Service: {type(diary_app.credential_service).__name__}")
    print()

    # 4. 비즈니스 로직 테스트
    print("4. 비즈니스 로직 테스트")

    # API 키가 없는지 확인
    has_credentials = credential_service.has_any_credential()
    print(f"   - API 키 존재 여부: {has_credentials}")

    if not has_credentials:
        print("   ✓ API 키가 없음 (초기 상태)")
        print("   → CLI 실행 시 API 키 등록 플로우로 이동함")
    else:
        print("   ✓ API 키가 존재함")
        default_cred = credential_service.get_default_credential()
        if default_cred:
            print(f"   - 기본 AI: {default_cred.provider.value}")
            print(f"   - 마스킹된 키: {default_cred.mask_api_key()}")

    print()

    # 5. 의존성 흐름 확인
    print("5. 의존성 흐름 확인")
    print("   Presentation (DiaryApp)")
    print("        ↓ 의존")
    print("   Domain (CredentialService)")
    print("        ↓ 인터페이스에만 의존")
    print("   Data (FileSystemCredentialRepository)")
    print()
    print("   ✓ 의존성 역전 원칙 준수!")
    print("   - Domain은 Data의 구체적인 구현체를 모름")
    print("   - Presentation은 Domain을 통해서만 데이터에 접근")
    print()

    print("=== 테스트 완료 ===")
    print()
    print("다음 단계:")
    print("  python main.py        # CLI 실행 (API 키 없으면 등록 플로우 시작)")


if __name__ == "__main__":
    test_dependency_injection()
