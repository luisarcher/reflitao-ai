import json
from collections import Counter
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.config import DEFAULT_SESSION

# type: ignore[override]


def _load_state(state_file: Path) -> dict:
    if state_file.exists():
        return json.loads(state_file.read_text(encoding="utf-8"))
    return {}


def _save_state(state_file: Path, state: dict) -> None:
    state_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def get_current_session(
    context: ContextTypes.DEFAULT_TYPE, user_id: int
) -> tuple[str, Path]:
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
    assert update.message is not None
    assert update.effective_user is not None
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


async def ls_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/ls — list files in the current session (like Linux ls)."""
    assert update.message is not None
    assert update.effective_user is not None
    user_id = update.effective_user.id
    session_name, session_path = get_current_session(context, user_id)

    files = sorted(f.name for f in session_path.iterdir() if f.is_file())
    if not files:
        await update.message.reply_text(f"📂 {session_name}/ (empty)")
        return

    lines = [f"📂 {session_name}/"]
    for fname in files:
        lines.append(f"  {fname}")

    await update.message.reply_text("\n".join(lines))


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/status — list all sessions with file-type counts, mark current."""
    assert update.message is not None
    assert update.effective_user is not None
    cfg = context.bot_data["config"]
    cfg.sessions_dir.mkdir(parents=True, exist_ok=True)

    sessions = sorted(d.name for d in cfg.sessions_dir.iterdir() if d.is_dir())
    if not sessions:
        await update.message.reply_text("No sessions yet.")
        return

    user_id = update.effective_user.id
    current_name, _ = get_current_session(context, user_id)

    lines = []
    for s in sessions:
        marker = " ← current" if s == current_name else ""
        session_path = cfg.sessions_dir / s
        files = [f for f in session_path.iterdir() if f.is_file()]

        if files:
            ext_counts = Counter(f.suffix.lower() for f in files)
            counts_str = ", ".join(
                f"{count} {ext}" for ext, count in sorted(ext_counts.items())
            )
            lines.append(f"• {s}{marker} [{counts_str}]")
        else:
            lines.append(f"• {s}{marker} (empty)")

    await update.message.reply_text("Sessions:\n" + "\n".join(lines))
