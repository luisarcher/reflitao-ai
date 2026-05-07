# Plan: AI Thinking Support Telegram Bot

TL;DR: A Python Telegram bot where users collect mixed-media artifacts (text, audio, images) into named sessions, then query a multimodal LLM with all session content as context. Audio is auto-transcribed via Whisper. State is persisted per-user in flat-file session folders.

App name is reflitao

## Project Structure

```
├── pyproject.toml          # uv-managed dependencies (astral toolchain)
├── .env                    # TELEGRAM_TOKEN, OPENAI_API_KEY, ANTHROPIC_API_KEY (gitignored)
├── .env.example
├── state.json              # persists current session per user_id (gitignored)
├── sessions/               # auto-created at runtime
│   ├── session0/           # default first session
│   └── .../
├── bot.py                  # entry point, registers all handlers
├── config.py               # settings, env var loading
├── handlers/
│   ├── __init__.py
│   ├── session_cmd.py      # /session, /listsessions (/ls), /status
│   ├── text_msg.py         # plain text message handler
│   ├── media.py            # photo / audio / voice handler
│   ├── prompt_cmd.py       # /promptsession (/ps), /prompt (/p)
│   ├── get_cmd.py          # /get <filename>
│   └── image_cmd.py        # /image <description>
└── services/
    ├── __init__.py
    ├── whisper.py          # Whisper API transcription
    ├── llm.py              # Claude Sonnet via Anthropic API
    └── image.py            # Image generation via OpenAI gpt-image-1
```

---

## Phase 1 — Project Scaffold
1. Add dependencies to `pyproject.toml` using `uv add`: `python-telegram-bot>=20`, `openai>=1.0`, `anthropic>=0.25`, `python-dotenv`
2. Create `.env.example` with placeholders: `TELEGRAM_TOKEN`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
3. Create `config.py`: loads env vars via `python-dotenv`, defines `SESSIONS_DIR`, `STATE_FILE`, `DEFAULT_SESSION = "session0"`, `DEFAULT_LLM_MODEL = "claude-sonnet-4-6"`
4. Create `state.json` schema: `{ "<user_id>": "<current_session_name>" }` — keyed by user so it's multi-user ready
5. Ensure `sessions/session0/` exists on first run
6. Run bot with `uv run python bot.py`

## Phase 2 — Session Management (`handlers/session_cmd.py`)
7. `/session <name>` — create or switch to named session; creates `sessions/<name>/`; updates `state.json`; replies with confirmation
8. `/listsessions` (alias `/ls`) — lists all folders under `sessions/`
9. `/status` — replies with current session name + file list inside with types
10. Helper `get_current_session(user_id)` — reads `state.json`, returns name + path; auto-initializes `session0` if missing

## Phase 3 — Artifact Collection
11. **Text messages** (`handlers/text_msg.py`): any non-command message → saved as `sessions/<name>/YYYYMMDDHHMMSS.md`
12. **Voice/audio** (`handlers/media.py`): file downloaded as `YYYYMMDDHHMMSS.ogg`; passed to `services/whisper.py`; transcript saved as `YYYYMMDDHHMMSS.md` (same base timestamp); bot replies "Transcribed and saved."
13. **Photos**: saved as `YYYYMMDDHHMMSS.jpg`; any caption saved as a paired `YYYYMMDDHHMMSS.md`
14. Timestamp: `datetime.now().strftime("%Y%m%d%H%M%S")`

## Phase 4 — Whisper Service (`services/whisper.py`)
15. `transcribe(file_path: str) -> str` — calls `openai.audio.transcriptions.create(model="whisper-1", file=...)`, returns text string
16. Called inline during audio handling before saving the `.md`

## Phase 5 — LLM Service (`services/llm.py`)
17. Uses Anthropic Python SDK; default model `claude-sonnet-4-6`
18. `call_llm(prompt: str, session_path: str | None = None) -> str`:
    - If `session_path` provided: loads session context, builds a user message with context + prompt, calls `anthropic.messages.create`
    - If `session_path` is `None`: sends prompt directly with no context (used by `/prompt`)
19. Context assembly:
    - Sort all session files by filename (timestamp order = chronological)
    - `.md` files → text blocks labeled with filename
    - `.jpg`/`.png` → base64 image blocks (Anthropic vision format)
    - Raw audio files (`.ogg`) → skipped if a paired `.md` transcript exists
20. Returns the text content string

## Phase 6 — Image Generation Service (`services/image.py`)
21. `generate_image(description: str) -> bytes` — calls `openai.images.generate(model="gpt-image-1", prompt=description)`, returns image bytes
22. Used by `/image` handler; bot sends the result back as a photo reply

## Phase 7 — Prompt Commands (`handlers/prompt_cmd.py`)
23. `/promptsession <prompt>` (alias `/ps`) — collects all files in current session, calls `call_llm(prompt, session_path)`, replies with result
24. `/prompt <prompt>` (alias `/p`) — calls `call_llm(prompt, session_path=None)` with no session context, replies with result
25. Both split and send the reply respecting Telegram's 4096-char message limit

## Phase 8 — File Retrieval (`handlers/get_cmd.py`)
26. `/get <filename>` — looks up `<filename>` inside the user's current session folder; sends the file as a document via `context.bot.send_document`; replies with an error if the file is not found

## Phase 9 — Image Generation Command (`handlers/image_cmd.py`)
27. `/image <description>` — calls `services/image.generate_image(description)`, sends the result back as a photo; replies with an error on failure

## Phase 10 — Entry Point (`bot.py`)
28. Register all handlers:
    - `CommandHandler` for `session`, `listsessions`/`ls`, `status`
    - `CommandHandler` for `promptsession`/`ps`, `prompt`/`p`
    - `CommandHandler` for `get`
    - `CommandHandler` for `image`
    - `MessageHandler(filters.TEXT & ~filters.COMMAND)` → text handler
    - `MessageHandler(filters.VOICE | filters.AUDIO)` → audio handler
    - `MessageHandler(filters.PHOTO)` → photo handler
29. Call `application.run_polling()`

---

## Relevant Files (all to create)
- `bot.py`, `config.py`, `.env.example`
- `handlers/__init__.py`, `handlers/session_cmd.py`, `handlers/text_msg.py`, `handlers/media.py`
- `handlers/prompt_cmd.py`, `handlers/get_cmd.py`, `handlers/image_cmd.py`
- `services/__init__.py`, `services/whisper.py`, `services/llm.py`, `services/image.py`
- Dependencies managed via `pyproject.toml` + `uv add` (no `requirements.txt`)

---

## Verification
1. Send a plain text message → confirm `.md` appears in `sessions/session0/` with correct timestamp
2. `/session work` → `sessions/work/` created; `/status` reflects the switch
3. Send a voice message → `.ogg` + `.md` transcript both appear in session folder
4. Send a photo with a caption → `.jpg` + paired `.md` saved
5. `/ps "Summarize everything"` → Claude Sonnet receives all session content and returns a coherent summary
6. `/p "What is the capital of France?"` → Claude Sonnet replies with no session context loaded
7. `/get 20260506120000.md` → bot sends the file as a document
8. `/image "a red fox in a snowy forest"` → bot replies with a generated image
9. `/ls` → lists all sessions; `/status` → shows file list for current session
10. Restart bot → `state.json` correctly restores current session

---

## Decisions
- **State keyed by user_id**: multi-user ready from day one, no refactor later
- **No database**: flat files + `state.json` — simple, inspectable, portable
- **Audio → transcript replaces audio in context**: Whisper first, LLM never receives raw audio
- **LLM model**: Claude Sonnet (`claude-sonnet-4-6`) via Anthropic API for `/ps` and `/p`; Whisper-1 for audio transcription; `gpt-image-2` for `/image`
- **`/prompt` vs `/promptsession`**: `/p` is a quick raw prompt with no session context; `/ps` includes full session context
- **Toolchain**: `uv` (astral) for dependency management; no `requirements.txt`; all dependencies declared in `pyproject.toml`
- **Out of scope**: ACL/auth, web UI, session deletion, LLM conversation history across `/ps` calls

If I upload any file, it is immediately uploaded to the current session folder

create an .env.example on the project root

start the readme with the centered image in .docs/img1.jpeg like this:
<p align="center">
  <img src=" ... ./docs/im1.jpeg AI to edit this" width="180" />
</p>

<h1 align="center">reflitão</h1>

---

And then continue the rest of the readme