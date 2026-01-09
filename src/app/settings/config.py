from pathlib import Path
import os
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    tg_bot_api_key: str

    # Assistant IDs (from .env)
    assistant_random_facts_id: str
    assistant_fact_spark_id: str
    assistant_talk_id: str
    assistant_quiz_master_id: str

    # Project paths
    project_root: Path
    resources_dir: Path
    messages_dir: Path
    prompts_dir: Path


def _get_project_root() -> Path:
    # file: src/app/settings/config.py
    # parents: settings -> app -> src -> project_root
    return Path(__file__).resolve().parents[3]


def _load_env(project_root: Path) -> None:
    env_path = project_root / ".env"
    load_dotenv(env_path)


project_root = _get_project_root()
_load_env(project_root)

resources_dir = project_root / "src" / "resources"
messages_dir = resources_dir / "messages"
prompts_dir = resources_dir / "prompts"

settings = Settings(
    openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
    tg_bot_api_key=os.getenv("TG_BOT_API_KEY", "").strip(),

    assistant_random_facts_id=os.getenv("AI_ASSISTANT_RANDOM_FACTS_ID", "").strip(),
    assistant_fact_spark_id=os.getenv("AI_ASSISTANT_FACT_SPARK_ID", "").strip(),
    assistant_talk_id=os.getenv("AI_ASSISTANT_TALK_ID", "").strip(),
    assistant_quiz_master_id=os.getenv("AI_ASSISTANT_QUIZ_MASTER_ID", "").strip(),

    project_root=project_root,
    resources_dir=resources_dir,
    messages_dir=messages_dir,
    prompts_dir=prompts_dir,
)


if not settings.tg_bot_api_key:
    raise RuntimeError("TG_BOT_API_KEY is missing in .env")

if not settings.openai_api_key:
    raise RuntimeError("OPENAI_API_KEY is missing in .env")
