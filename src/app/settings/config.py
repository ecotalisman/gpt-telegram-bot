import logging
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator, computed_field

logger = logging.getLogger(__name__)


def _get_project_root() -> Path:
    """Get project root directory (3 levels up from this file)"""
    return Path(__file__).resolve().parents[3]


PROJECT_ROOT = _get_project_root()
ENV_FILE_PATH = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings with automatic validation from .env file"""

    # Required API keys
    openai_api_key: str = Field(..., description="OpenAI API key")
    tg_bot_api_key: str = Field(..., description="Telegram Bot API key")

    # Optional settings with defaults
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model name")

    # OpenAI Assistant IDs (optional) - use validation_alias to map from .env names
    assistant_random_facts_id: str = Field(default="", validation_alias="AI_ASSISTANT_RANDOM_FACTS_ID")
    assistant_fact_spark_id: str = Field(default="", validation_alias="AI_ASSISTANT_FACT_SPARK_ID")
    assistant_talk_id: str = Field(default="", validation_alias="AI_ASSISTANT_TALK_ID")
    assistant_quiz_master_id: str = Field(default="", validation_alias="AI_ASSISTANT_QUIZ_MASTER_ID")

    @field_validator("openai_api_key", "tg_bot_api_key")
    @classmethod
    def validate_required(cls, v: str, info) -> str:
        """
        Validate that required API keys are not empty or whitespace-only.

        Args:
            v: The value to validate
            info: Field information (contains field_name)

        Returns:
            Stripped value if valid

        Raises:
            ValueError: If the value is empty or whitespace-only
        """
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} is required and cannot be empty")
        return v.strip()

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
        populate_by_name=True,
    )

    @computed_field
    @property
    def project_root(self) -> Path:
        return _get_project_root()

    @computed_field
    @property
    def resources_dir(self) -> Path:
        return self.project_root / "src" / "resources"

    @computed_field
    @property
    def messages_dir(self) -> Path:
        return self.resources_dir / "messages"

    @computed_field
    @property
    def prompts_dir(self) -> Path:
        return self.resources_dir / "prompts"

    @computed_field
    @property
    def images_dir(self) -> Path:
        return self.resources_dir / "images"


# Create settings instance (pydantic automatically loads from .env)
settings = Settings()
