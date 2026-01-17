from app.settings.config import settings


def load_message(name: str) -> str:
    path = settings.messages_dir / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def load_prompt(name: str) -> str:
    path = settings.prompts_dir / f"{name}.txt"
    return path.read_text(encoding="utf-8")


def image_path(name: str) -> str:
    return str(settings.resources_dir / "images" / f"{name}.png")
