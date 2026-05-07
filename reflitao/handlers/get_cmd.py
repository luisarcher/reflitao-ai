from telegram import Update
from telegram.ext import ContextTypes

from reflitao.handlers.session_cmd import get_current_session


async def get_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/get <filename> — send a file from the current session."""
    if not context.args:
        await update.message.reply_text("Usage: /get <filename>")
        return

    filename = context.args[0].strip()
    user_id = update.effective_user.id
    _, session_path = get_current_session(context, user_id)

    file_path = session_path / filename

    if not file_path.is_file():
        await update.message.reply_text(f"File not found: {filename}")
        return

    # Prevent path traversal
    try:
        file_path.resolve().relative_to(session_path.resolve())
    except ValueError:
        await update.message.reply_text("Invalid filename.")
        return

    await update.message.reply_document(document=open(file_path, "rb"), filename=filename)
