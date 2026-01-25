# GPT Telegram Bot

A multi-mode Telegram bot powered by OpenAI's Responses API. Chat with GPT, take quizzes, talk to historical personas, and get random facts.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Schema](#database-schema)

---

## Features

- **GPT Mode** — Have a conversation with GPT. Context is preserved across messages using OpenAI's Responses API.

- **Quiz Mode** — Test your knowledge with AI-generated quizzes on Python, JavaScript, Docker, and Web topics. Get instant feedback on each answer.

- **Talk Mode** — Chat with historical personas:
  - Ada Lovelace — poetic visionary of computing
  - Albert Einstein — thoughtful, curious explainer
  - Elon Musk — bold and pragmatic

- **Random Facts** — Get interesting random facts on any topic you provide.

- **Persistent Sessions** — Each mode maintains its own conversation history per user.

- **Reset Command** — Clear your conversation history and start fresh.

---

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python 3.12 |
| Bot Framework | [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) v22 |
| AI | [OpenAI Responses API](https://platform.openai.com/docs/api-reference) |
| Database | SQLite via [aiosqlite](https://github.com/omnilib/aiosqlite) |
| Configuration | [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) v2 |
| Package Manager | [Poetry](https://python-poetry.org/) |

---

## Project Structure

```
gpt-telegram-bot/
├── src/
│   ├── app/
│   │   ├── bot/
│   │   │   ├── handlers/
│   │   │   │   ├── gpt_handler.py      # GPT mode message handler
│   │   │   │   ├── quiz_handler.py     # Quiz mode logic
│   │   │   │   ├── talk_handler.py     # Persona chat handler
│   │   │   │   ├── random_handler.py   # Random facts handler
│   │   │   │   └── message_router.py   # Routes messages to handlers
│   │   │   ├── utils/
│   │   │   │   ├── quiz.py             # Quiz utilities
│   │   │   │   └── openai_quiz.py      # Quiz generation with OpenAI
│   │   │   ├── bot.py                  # Bot initialization
│   │   │   ├── commands.py             # Command handlers (/start, /gpt, etc.)
│   │   │   ├── keyboards.py            # Reply keyboard definitions
│   │   │   ├── message_sender.py       # Message sending utilities
│   │   │   └── resource_loader.py      # Load prompts and messages
│   │   ├── db/
│   │   │   ├── database.py             # Database initialization
│   │   │   ├── repository.py           # Data access layer
│   │   │   └── enums.py                # Session modes enum
│   │   ├── services/
│   │   │   └── openai_client.py        # OpenAI API wrapper
│   │   ├── settings/
│   │   │   ├── config.py               # Pydantic settings
│   │   │   └── logging_config.py       # Logging configuration
│   │   ├── main.py                     # Application entry point
│   │   └── utils.py                    # General utilities
│   └── resources/
│       ├── images/                     # Mode images (gpt.png, quiz.png, etc.)
│       ├── menus/
│       │   └── keyboards.json          # Keyboard button configuration
│       ├── messages/                   # Text message templates
│       └── prompts/                    # System prompts for OpenAI
├── storage/
│   └── bot.db                          # SQLite database (auto-created)
├── logs/                               # Application logs
├── .env                                # Environment variables (create from .env.sample)
├── .env.sample                         # Environment template
├── pyproject.toml                      # Poetry dependencies
└── README.md
```

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ecotalisman/gpt-telegram-bot.git
cd gpt-telegram-bot
```

### 2. Install Poetry (if not installed)

<details>
<summary>Windows (PowerShell)</summary>

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```
</details>

<details>
<summary>macOS / Linux</summary>

```bash
curl -sSL https://install.python-poetry.org | python3 -
```
</details>

### 3. Install dependencies

```bash
poetry install
```

### 4. Configure environment

```bash
cp .env.sample .env
```

Edit `.env` with your API keys (see [Configuration](#configuration)).

### 5. Run the bot

```bash
poetry run python -m src.app.main
```

---

## Configuration

Create a `.env` file based on `.env.sample`:

```dotenv
# Required
OPENAI_API_KEY=sk-...
TG_BOT_API_KEY=123456:ABC-DEF...

# Optional (defaults shown)
OPENAI_MODEL=gpt-4o-mini

# Optional OpenAI Assistant IDs (for advanced features)
AI_ASSISTANT_FACT_SPARK_ID=
AI_ASSISTANT_RANDOM_FACTS_ID=
AI_ASSISTANT_TALK_ID=
AI_ASSISTANT_QUIZ_MASTER_ID=
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `TG_BOT_API_KEY` | Yes | Telegram Bot API token from [@BotFather](https://t.me/BotFather) |
| `OPENAI_MODEL` | No | OpenAI model to use (default: `gpt-4o-mini`) |
| `AI_ASSISTANT_*_ID` | No | OpenAI Assistant IDs for specific modes |

---

## Usage

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and main menu |
| `/gpt` | Switch to GPT chat mode |
| `/quiz` | Start a quiz (choose topic: Python, JavaScript, Docker, Web) |
| `/talk` | Chat with a persona (Ada Lovelace, Einstein, Elon Musk) |
| `/random` | Get a random fact (optionally specify a topic) |
| `/reset` | Clear all your conversation history |

### Workflow

1. **Start the bot** — Send `/start` to see the main menu
2. **Choose a mode** — Tap a button or send a command
3. **Interact** — Send messages, answer quiz questions, or chat with personas
4. **Switch modes** — Use commands or tap "Finish" to return to main menu

---

## Database Schema

The bot uses SQLite to store conversation sessions and message history.

### Tables

#### `user_threads`

Stores one session per user per mode.

| Column | Type | Description |
|--------|------|-------------|
| `tg_user_id` | INTEGER | Telegram user ID |
| `mode` | TEXT | Session mode (gpt, quiz, talk, random) |
| `conversation_id` | TEXT | Unique conversation identifier |
| `last_response_id` | TEXT | OpenAI response ID for context continuation |

Primary Key: `(tg_user_id, mode)`

#### `thread_messages`

Stores all messages in conversations.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `conversation_id` | TEXT | Links to user_threads |
| `role` | TEXT | Message role (user/assistant) |
| `content` | TEXT | Message content |
| `created_at` | DATETIME | Timestamp |

Index: `idx_thread_messages_conversation` on `conversation_id`

---

## License

MIT
