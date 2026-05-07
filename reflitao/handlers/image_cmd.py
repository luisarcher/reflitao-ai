import io

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.services.image import generate_image

# type: ignore[override]


async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/image <description> — generate an image and send it back."""
    assert update.message is not None
    if not context.args:
        await update.message.reply_text("Usage: /image <description>")
        return

    description = " ".join(context.args)
    cfg = context.bot_data["config"]

    await update.message.reply_text("Generating image...")

    try:
        image_bytes = generate_image(cfg.openai_api_key, description)
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")
        return

    await update.message.reply_photo(photo=io.BytesIO(image_bytes))
