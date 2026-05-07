from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.handlers.session_cmd import get_current_session

# type: ignore[override]


async def text_message_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Save any non-command text message as a .md file in the current session."""
    assert update.message is not None
    assert update.effective_user is not None
    assert update.message.text is not None
    user_id = update.effective_user.id
    _, session_path = get_current_session(context, user_id)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filepath = session_path / f"{timestamp}.md"
    filepath.write_text(update.message.text, encoding="utf-8")

    await update.message.reply_text("Text saved.")
