"""Domain interfaces (Repository contracts)"""

from diary.domain.interfaces.credential_repository import CredentialRepositoryInterface
from diary.domain.interfaces.user_preferences_repository import UserPreferencesRepositoryInterface
from diary.domain.interfaces.writing_style_examples_repository import WritingStyleExamplesRepositoryInterface

__all__ = [
    "CredentialRepositoryInterface",
    "UserPreferencesRepositoryInterface",
    "WritingStyleExamplesRepositoryInterface",
]
