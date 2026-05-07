<p align="center">
  <img src="./docs/img1.jpeg" width="180" />
</p>

<h1 align="center">reflitão</h1>

---

A Telegram bot for AI-assisted thinking. Collect mixed-media artifacts (text, audio, images) into named sessions, then query a multimodal LLM with all session content as context. Audio is auto-transcribed via Whisper.

## Features

- **Session management** — organize thoughts into named sessions
- **Text capture** — any message is saved as a timestamped artifact
- **Voice/audio transcription** — automatic Whisper transcription on upload
- **Photo collection** — images with optional captions stored in sessions
- **File uploads** — any document uploaded goes straight to the current session
- **LLM prompting with context** — query Claude Sonnet with your full session as context (`/ps`)
- **Raw LLM prompting** — quick questions without session context (`/p`)
- **Image generation** — generate images via OpenAI's gpt-image-1 (`/image`)
- **File retrieval** — download any session artifact via `/get`
- **Multi-user** — state is persisted per user, sessions are isolated
- **Flat-file storage** — no database, everything is inspectable on disk

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A Telegram bot token
- OpenAI API key (Whisper + image generation)
- Anthropic API key (Claude Sonnet)

## Installation

```bash
pip install reflitao
```

Or from source:

```bash
git clone https://github.com/luisarcher/reflitao-ai.git
cd reflitao-ai
uv sync
```

## Configuration

First-time setup (interactive):

```bash
reflitao init
```

This creates `~/.config/reflitao/config.toml`:

```toml
[keys]
telegram_token = "your-telegram-bot-token"
openai_api_key = "your-openai-api-key"
anthropic_api_key = "your-anthropic-api-key"
```

Alternatively, set environment variables (useful for Docker/CI):

```bash
export REFLITAO_TELEGRAM_TOKEN="..."
export REFLITAO_OPENAI_API_KEY="..."
export REFLITAO_ANTHROPIC_API_KEY="..."
```

Environment variables take priority over the config file.

## Usage

```bash
# Run the bot (sessions stored in current directory)
reflitao

# Or specify a workspace directory
reflitao ~/my-thinking-sessions

# Or via python -m
python -m reflitao [dir]
```

## Bot Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `/session <name>` | | Create or switch to a named session |
| `/listsessions` | `/ls` | List all sessions |
| `/status` | | Show current session and its files |
| `/promptsession <prompt>` | `/ps` | Query LLM with full session context |
| `/prompt <prompt>` | `/p` | Query LLM without session context |
| `/get <filename>` | | Download a file from the current session |
| `/image <description>` | | Generate an image from a text description |

## How It Works

1. **Collect** — send text, voice, photos, or files to the bot. Everything is saved to your current session folder.
2. **Organize** — use `/session` to create and switch between named sessions.
3. **Query** — use `/ps` to send a prompt to Claude Sonnet with all session artifacts as context.

## Use cases

Most applications of AI vendors already support access to the camera, realtime audio and text. Hows does this benefits me?

You create multiple sessions for any variety of topic and you actually OWN both input and output data.
You can actually brainstorm into .md files and you can run reflitao next to your personal knowledge manager like Obsidian.
In my case this is how I use reflitao, brainstorm on ideas and link it to my existing Obsidian notes.

## Development

```bash
uv sync --group dev
uv run pytest
```

## License

[MIT](LICENSE)

## Linting & Formatting

```bash
uv run ruff check .
uv run ruff format .
```

## Type Checking

```bash
uv run ty check reflitao/
```

## Commit Convention

This project uses [Conventional Commits](https://www.conventionalcommits.org/) to drive automated versioning:

| Prefix | Effect |
|--------|--------|
| `fix:` | Patch release |
| `feat:` | Minor release |
| `feat!:` / `BREAKING CHANGE` | Major release |

## License

[MIT](LICENSE)
