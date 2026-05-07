import logging
from pathlib import Path

from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from reflitao.config import load_config
from reflitao.handlers.get_cmd import get_command
from reflitao.handlers.image_cmd import image_command
from reflitao.handlers.media import document_handler, photo_handler, voice_audio_handler
from reflitao.handlers.prompt_cmd import prompt_command, promptsession_command
from reflitao.handlers.session_cmd import ls_command, session_command, status_command
from reflitao.handlers.text_msg import text_message_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand("session", "Create or switch session"),
    BotCommand("s", "Create or switch session (short)"),
    BotCommand("ls", "List files in current session"),
    BotCommand("status", "List all sessions with file counts"),
    BotCommand("ps", "Prompt LLM with session context"),
    BotCommand("promptsession", "Prompt LLM with session context"),
    BotCommand("p", "Prompt LLM without context"),
    BotCommand("prompt", "Prompt LLM without context"),
    BotCommand("get", "Download a file from session"),
    BotCommand("image", "Generate an image"),
]


async def post_init(application) -> None:
    """Set bot commands so they appear in the Telegram keyboard."""
    await application.bot.set_my_commands(BOT_COMMANDS)


def run_bot(data_dir: Path) -> None:
    cfg = load_config(data_dir)

    # Ensure sessions dir exists
    cfg.sessions_dir.mkdir(parents=True, exist_ok=True)

    app = ApplicationBuilder().token(cfg.telegram_token).post_init(post_init).build()

    # Store config in bot_data so handlers can access it
    app.bot_data["config"] = cfg

    # Session commands
    app.add_handler(CommandHandler(["session", "s"], session_command))
    app.add_handler(CommandHandler("ls", ls_command))
    app.add_handler(CommandHandler("status", status_command))

    # Prompt commands
    app.add_handler(CommandHandler(["promptsession", "ps"], promptsession_command))
    app.add_handler(CommandHandler(["prompt", "p"], prompt_command))

    # File retrieval
    app.add_handler(CommandHandler("get", get_command))

    # Image generation
    app.add_handler(CommandHandler("image", image_command))

    # Message handlers
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler)
    )
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_audio_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    logger.info("Bot starting (data dir: %s)...", data_dir)
    app.run_polling()
