"""Domain interfaces (Repository contracts)"""

from diary.domain.interfaces.credential_repository import CredentialRepositoryInterface
from diary.domain.interfaces.user_preferences_repository import UserPreferencesRepositoryInterface
from diary.domain.interfaces.writing_style_examples_repository import WritingStyleExamplesRepositoryInterface
from diary.domain.interfaces.ai_client import AIClientInterface
from diary.domain.interfaces.chat_repository import ChatRepositoryInterface

__all__ = [
    "CredentialRepositoryInterface",
    "UserPreferencesRepositoryInterface",
    "WritingStyleExamplesRepositoryInterface",
    "AIClientInterface",
    "ChatRepositoryInterface",
]
