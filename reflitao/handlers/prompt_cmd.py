from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.handlers.session_cmd import get_current_session
from reflitao.services.llm import call_llm, split_message


def _save_response(session_path, prompt: str, result: str) -> None:
    """Persist LLM response as a timestamped markdown file."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    md_path = session_path / f"{timestamp}_response.md"
    content = f"# Prompt\n\n{prompt}\n\n# Response\n\n{result}\n"
    md_path.write_text(content, encoding="utf-8")


async def promptsession_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/promptsession <prompt> — query LLM with full session context."""
    if not context.args:
        await update.message.reply_text("Usage: /promptsession <prompt>")
        return

    prompt = " ".join(context.args)
    user_id = update.effective_user.id
    cfg = context.bot_data["config"]
    _, session_path = get_current_session(context, user_id)

    await update.message.reply_text("Thinking...")

    try:
        result = call_llm(cfg.anthropic_api_key, prompt, session_path=str(session_path))
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    _save_response(session_path, prompt, result)

    for chunk in split_message(result):
        await update.message.reply_text(chunk)


async def prompt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/prompt <prompt> — query LLM with no session context."""
    if not context.args:
        await update.message.reply_text("Usage: /prompt <prompt>")
        return

    prompt = " ".join(context.args)
    user_id = update.effective_user.id
    cfg = context.bot_data["config"]
    _, session_path = get_current_session(context, user_id)

    await update.message.reply_text("Thinking...")

    try:
        result = call_llm(cfg.anthropic_api_key, prompt, session_path=None)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    _save_response(session_path, prompt, result)

    for chunk in split_message(result):
        await update.message.reply_text(chunk)
