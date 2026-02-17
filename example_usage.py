"""AI 인증 정보 관리 사용 예제

레이어드 아키텍처 + 의존성 역전 원칙 적용 예시:
- Domain Layer: 비즈니스 로직 (CredentialService)
- Data Layer: 구현체 (FileSystemCredentialRepository)
"""

from diary.domain.entities import AIProvider
from diary.domain.services import CredentialService
from diary.data.repositories import FileSystemCredentialRepository


def main():
    print("=== AI 인증 정보 관리 시스템 예제 ===\n")

    # 1. 의존성 주입 (Dependency Injection)
    # Data Layer 구현체를 생성 (Domain은 이것을 모름!)
    credential_repo = FileSystemCredentialRepository()

    # Domain Layer 서비스에 주입
    credential_service = CredentialService(credential_repo)

    print("1. API 키 저장")
    print("-" * 50)

    # 2. OpenAI API 키 저장 (첫 번째는 자동으로 기본 AI가 됨)
    try:
        openai_cred = credential_service.save_credential(
            provider=AIProvider.OPENAI,
            api_key="sk-proj-test1234567890abcdef",
            name="내 OpenAI 계정"
        )
        print(f"✅ {openai_cred.provider.value} 저장 완료")
        print(f"   - 마스킹된 키: {openai_cred.mask_api_key()}")
        print(f"   - 기본 AI: {openai_cred.is_default}")
        print(f"   - 이름: {openai_cred.name}")
    except ValueError as e:
        print(f"❌ 오류: {e}")

    print()

    # 3. Anthropic API 키 저장
    try:
        anthropic_cred = credential_service.save_credential(
            provider=AIProvider.ANTHROPIC,
            api_key="sk-ant-test1234567890abcdef",
            name="내 Claude 계정"
        )
        print(f"✅ {anthropic_cred.provider.value} 저장 완료")
        print(f"   - 마스킹된 키: {anthropic_cred.mask_api_key()}")
        print(f"   - 기본 AI: {anthropic_cred.is_default}")
    except ValueError as e:
        print(f"❌ 오류: {e}")

    print("\n2. 전체 AI 목록 조회")
    print("-" * 50)

    all_credentials = credential_service.list_all_credentials()
    for cred in all_credentials:
        default_mark = "⭐" if cred.is_default else "  "
        print(f"{default_mark} {cred.provider.value:12s} | {cred.mask_api_key():30s} | {cred.name or 'N/A'}")

    print("\n3. 기본 AI 변경")
    print("-" * 50)

    try:
        new_default = credential_service.set_default_provider(AIProvider.ANTHROPIC)
        print(f"✅ 기본 AI를 {new_default.provider.value}로 변경")
    except ValueError as e:
        print(f"❌ 오류: {e}")

    print("\n4. 변경 후 전체 AI 목록")
    print("-" * 50)

    all_credentials = credential_service.list_all_credentials()
    for cred in all_credentials:
        default_mark = "⭐" if cred.is_default else "  "
        print(f"{default_mark} {cred.provider.value:12s} | {cred.mask_api_key():30s}")

    print("\n5. 기본 AI 조회")
    print("-" * 50)

    default_cred = credential_service.get_default_credential()
    if default_cred:
        print(f"⭐ 기본 AI: {default_cred.provider.value}")
        print(f"   - API 키: {default_cred.mask_api_key()}")
        print(f"   - 이름: {default_cred.name}")
    else:
        print("❌ 기본 AI가 설정되지 않았습니다")

    print("\n6. 특정 AI 삭제")
    print("-" * 50)

    try:
        credential_service.delete_credential(AIProvider.OPENAI)
        print(f"✅ {AIProvider.OPENAI.value} 삭제 완료")
    except ValueError as e:
        print(f"❌ 오류: {e}")

    print("\n7. 삭제 후 전체 AI 목록")
    print("-" * 50)

    all_credentials = credential_service.list_all_credentials()
    for cred in all_credentials:
        default_mark = "⭐" if cred.is_default else "  "
        print(f"{default_mark} {cred.provider.value:12s} | {cred.mask_api_key():30s}")

    print("\n8. 저장 위치 확인")
    print("-" * 50)
    print(f"📁 파일 위치: {credential_repo.file_path}")

    print("\n=== 완료 ===")


if __name__ == "__main__":
    main()
