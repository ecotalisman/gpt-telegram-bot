import argparse
from tabulate import tabulate
from openai import OpenAI, OpenAIError
from src.app.settings.config import settings

CLI_VERSION = "0.1.0"


def load_prompt(prompt_name: str) -> str:
    path = settings.prompts_dir / f"{prompt_name}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="assistant-manager",
        description=(
            "Manage your OpenAI Assistants\n\n"
            "Examples:\n"
            "  python -m app.services.assistant_manager_cli --list\n"
            "  python -m app.services.assistant_manager_cli --list 20\n"
            "  python -m app.services.assistant_manager_cli --create -n \"History Expert\" -p history\n"
            "  python -m app.services.assistant_manager_cli --delete asst_abc123\n"
            "  python -m app.services.assistant_manager_cli --update asst_abc123 -p updated_prompt\n"
            "  python -m app.services.assistant_manager_cli --show asst_abc123\n"
            "  python -m app.services.assistant_manager_cli --show asst_abc123 --instructions\n"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"assistant-manager {CLI_VERSION}",
        help="Show CLI version",
    )

    parser.add_argument(
        "-l", "--list",
        nargs="?",
        const=10,
        type=int,
        help="List up to N assistants (default: 10)",
    )

    parser.add_argument(
        "-s", "--show",
        type=str,
        help="Show assistant by ID",
    )

    parser.add_argument(
        "--instructions",
        action="store_true",
        help="Show full instructions with --show",
    )

    parser.add_argument(
        "-c", "--create",
        action="store_true",
        help="Create a new assistant",
    )

    parser.add_argument(
        "-u", "--update",
        type=str,
        help="Update assistant instructions by ID",
    )

    parser.add_argument(
        "-d", "--delete",
        type=str,
        help="Delete assistant by ID",
    )

    parser.add_argument(
        "-n", "--name",
        type=str,
        help="Assistant name (required with --create)",
    )

    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Prompt filename from resources/prompts (no .txt)",
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        default=None,
        help="Model name used ONLY with --create (default: gpt-4o-mini). --update changes instructions only)",
    )

    return parser


def create_client() -> OpenAI:
    """Create an OpenAI client using the configured API key"""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is missing in .env")
    return OpenAI(api_key=settings.openai_api_key)


def handle_list(client: OpenAI, limit: int) -> None:
    """List assistants with a configurable limit (pretty table)"""
    try:
        assistants = client.beta.assistants.list(limit=limit)
    except OpenAIError as exc:
        raise SystemExit(f"Failed to list assistants: {exc}") from exc

    if not assistants.data:
        print("No assistants found")
        return

    rows = [(a.id, a.name or "-", a.model) for a in assistants.data]
    print(tabulate(rows, headers=["ID", "Name", "Model"], tablefmt="github"))


def handle_show(client: OpenAI, assistant_id: str, show_instructions: bool) -> None:
    """Show details for a single assistant by ID"""
    try:
        assistant = client.beta.assistants.retrieve(assistant_id)
    except OpenAIError as exc:
        raise SystemExit(f"Failed to retrieve assistant: {exc}") from exc

    print(f"ID: {assistant.id}")
    print(f"Name: {assistant.name or '-'}")
    print(f"Model: {assistant.model}")
    if show_instructions:
        print("\n--- instructions ---")
        print(assistant.instructions or "")


def handle_delete(client: OpenAI, assistant_id: str) -> None:
    """Delete an assistant by ID"""
    try:
        client.beta.assistants.delete(assistant_id)
    except OpenAIError as exc:
        raise SystemExit(f"Failed to delete assistant: {exc}") from exc

    print(f"Deleted: {assistant_id}")


def handle_create(client: OpenAI, name: str, prompt_name: str, model: str) -> None:
    """Create a new assistant using the prompt file and chosen model"""
    if not name or not prompt_name:
        raise SystemExit("Need: --create -n NAME -p PROMPT_NAME")

    try:
        instructions = load_prompt(prompt_name)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            model=model,
        )
    except OpenAIError as exc:
        raise SystemExit(f"Failed to create assistant: {exc}") from exc

    print(f"Assistant created: {assistant.id} ({assistant.name})")


def handle_update(client: OpenAI, assistant_id: str, prompt_name: str) -> None:
    """Update assistant instructions using a prompt file"""
    if not prompt_name:
        raise SystemExit("Need: --update ASSISTANT_ID -p PROMPT_NAME")

    try:
        instructions = load_prompt(prompt_name)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc

    try:
        assistant = client.beta.assistants.update(
            assistant_id=assistant_id,
            instructions=instructions,
        )
    except OpenAIError as exc:
        raise SystemExit(f"Failed to update assistant: {exc}") from exc

    print(f"Updated: {assistant.id} ({assistant.name})")


def main() -> None:
    """CLI entry point. Parses args and performs exactly one action"""
    parser = build_parser()
    args = parser.parse_args()

    if args.instructions and not args.show:
        raise SystemExit("--instructions requires --show ASSISTANT_ID")

    actions = sum([
        args.list is not None,
        bool(args.show),
        bool(args.delete),
        bool(args.create),
        bool(args.update),
    ])

    if actions != 1:
        raise SystemExit(
            "Choose exactly one action: --list/--show/--create/--update/--delete"
        )

    if args.model is not None and not args.create:
        raise SystemExit("--model can be used only with --create")

    if args.create and args.model is None:
        args.model = "gpt-4o-mini"

    client = create_client()

    if args.list is not None:
        handle_list(client, args.list)
        return

    if args.show:
        handle_show(client, args.show, args.instructions)
        return

    if args.delete:
        handle_delete(client, args.delete)
        return

    if args.create:
        handle_create(client, args.name, args.prompt, args.model)
        return

    if args.update:
        handle_update(client, args.update, args.prompt)
        return

    print("Nothing to do. Use -h for help.")


if __name__ == "__main__":
    main()
