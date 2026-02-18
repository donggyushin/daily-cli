"""Data Layer - Repository implementations"""

from diary.data.repositories.file_credential_repository import FileSystemCredentialRepository
from diary.data.repositories.file_user_preferences_repository import FileSystemUserPreferencesRepository
from diary.data.repositories.file_writing_style_examples_repository import FileSystemWritingStyleExamplesRepository
from diary.data.repositories.file_chat_repository import FileSystemChatRepository
from diary.data.repositories.openai_client import OpenAIClient
from diary.data.repositories.anthropic_client import AnthropicClient
from diary.data.repositories.google_ai_client import GoogleAIClient
from diary.data.repositories.mongodb_chat_repository import MongoDBChatRepository
from diary.data.repositories.mongodb_diary_repository import MongoDBDiaryRepository

__all__ = [
    "FileSystemCredentialRepository",
    "FileSystemUserPreferencesRepository",
    "FileSystemWritingStyleExamplesRepository",
    "FileSystemChatRepository",
    "MongoDBChatRepository",
    "MongoDBDiaryRepository",
    "OpenAIClient",
    "AnthropicClient",
    "GoogleAIClient",
]
