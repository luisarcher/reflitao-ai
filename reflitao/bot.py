import logging
from pathlib import Path

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from reflitao.config import load_config
from reflitao.handlers.session_cmd import session_command, listsessions_command, status_command
from reflitao.handlers.text_msg import text_message_handler
from reflitao.handlers.media import voice_audio_handler, photo_handler, document_handler
from reflitao.handlers.prompt_cmd import promptsession_command, prompt_command
from reflitao.handlers.get_cmd import get_command
from reflitao.handlers.image_cmd import image_command

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def run_bot(data_dir: Path) -> None:
    cfg = load_config(data_dir)

    # Ensure sessions dir exists
    cfg.sessions_dir.mkdir(parents=True, exist_ok=True)

    app = ApplicationBuilder().token(cfg.telegram_token).build()

    # Store config in bot_data so handlers can access it
    app.bot_data["config"] = cfg

    # Session commands
    app.add_handler(CommandHandler("session", session_command))
    app.add_handler(CommandHandler(["listsessions", "ls"], listsessions_command))
    app.add_handler(CommandHandler("status", status_command))

    # Prompt commands
    app.add_handler(CommandHandler(["promptsession", "ps"], promptsession_command))
    app.add_handler(CommandHandler(["prompt", "p"], prompt_command))

    # File retrieval
    app.add_handler(CommandHandler("get", get_command))

    # Image generation
    app.add_handler(CommandHandler("image", image_command))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_audio_handler))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.Document.ALL, document_handler))

    logger.info("Bot starting (data dir: %s)...", data_dir)
    app.run_polling()
