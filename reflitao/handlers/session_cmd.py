import json
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.config import DEFAULT_SESSION


def _load_state(state_file: Path) -> dict:
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {}


def _save_state(state_file: Path, state: dict) -> None:
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_current_session(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> tuple[str, Path]:
    """Return (session_name, session_path) for the given user."""
    cfg = context.bot_data["config"]
    state = _load_state(cfg.state_file)
    uid = str(user_id)
    session_name = state.get(uid, DEFAULT_SESSION)

    session_path = cfg.sessions_dir / session_name
    session_path.mkdir(parents=True, exist_ok=True)

    if uid not in state:
        state[uid] = session_name
        _save_state(cfg.state_file, state)

    return session_name, session_path


async def session_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/session <name> — create or switch to a named session."""
    if not context.args:
        await update.message.reply_text("Usage: /session <name>")
        return

    cfg = context.bot_data["config"]
    name = context.args[0].strip()
    user_id = update.effective_user.id

    session_path = cfg.sessions_dir / name
    session_path.mkdir(parents=True, exist_ok=True)

    state = _load_state(cfg.state_file)
    state[str(user_id)] = name
    _save_state(cfg.state_file, state)

    await update.message.reply_text(f"Switched to session: {name}")


async def listsessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/listsessions — list all sessions."""
    cfg = context.bot_data["config"]
    cfg.sessions_dir.mkdir(parents=True, exist_ok=True)
    sessions = sorted(
        d.name for d in cfg.sessions_dir.iterdir() if d.is_dir()
    )
    if not sessions:
        await update.message.reply_text("No sessions yet.")
        return

    user_id = update.effective_user.id
    current_name, _ = get_current_session(context, user_id)
    lines = []
    for s in sessions:
        marker = " ← current" if s == current_name else ""
        lines.append(f"• {s}{marker}")

    await update.message.reply_text("Sessions:\n" + "\n".join(lines))


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status — show current session name and file list."""
    user_id = update.effective_user.id
    session_name, session_path = get_current_session(context, user_id)

    files = sorted(f.name for f in session_path.iterdir() if f.is_file())
    if not files:
        file_list = "(empty)"
    else:
        lines = []
        for fname in files:
            ext = Path(fname).suffix.lower()
            type_label = {
                ".md": "text",
                ".jpg": "image",
                ".jpeg": "image",
                ".png": "image",
                ".ogg": "audio",
                ".mp3": "audio",
                ".wav": "audio",
                ".m4a": "audio",
            }.get(ext, "file")
            lines.append(f"  • {fname} [{type_label}]")
        file_list = "\n".join(lines)

    await update.message.reply_text(
        f"Session: {session_name}\nFiles:\n{file_list}"
    )
