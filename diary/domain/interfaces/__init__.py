"""Domain interfaces (Repository contracts)"""

from diary.domain.interfaces.credential_repository import CredentialRepositoryInterface
from diary.domain.interfaces.user_preferences_repository import UserPreferencesRepositoryInterface

__all__ = [
    "CredentialRepositoryInterface",
    "UserPreferencesRepositoryInterface",
]
