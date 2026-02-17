"""Data Layer - Repository implementations"""

from diary.data.repositories.file_credential_repository import FileSystemCredentialRepository
from diary.data.repositories.file_user_preferences_repository import FileSystemUserPreferencesRepository
from diary.data.repositories.file_writing_style_examples_repository import FileSystemWritingStyleExamplesRepository

__all__ = [
    "FileSystemCredentialRepository",
    "FileSystemUserPreferencesRepository",
    "FileSystemWritingStyleExamplesRepository",
]
