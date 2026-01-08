from app.settings.config import settings


def load_messages(name: str) -> str:
    """
    Reads message text from:
    <project_root>/src/resources/messages/{name}.txt
    """
    path = settings.messages_dir / f"{name}.txt"
    return path.read_text(encoding="utf-8")
