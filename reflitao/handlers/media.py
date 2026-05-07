from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from reflitao.handlers.session_cmd import get_current_session
from reflitao.services.whisper import transcribe

# type: ignore[override]


async def voice_audio_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle voice and audio messages: download, transcribe, save both."""
    assert update.message is not None
    assert update.effective_user is not None
    user_id = update.effective_user.id
    _, session_path = get_current_session(context, user_id)
    cfg = context.bot_data["config"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    voice = update.message.voice
    audio = update.message.audio
    if voice:
        assert voice is not None
        file = await voice.get_file()
    elif audio:
        assert audio is not None
        file = await audio.get_file()
    else:
        return

    audio_path = session_path / f"{timestamp}.ogg"
    await file.download_to_drive(str(audio_path))

    transcript = transcribe(cfg.openai_api_key, str(audio_path))

    md_path = session_path / f"{timestamp}.md"
    md_path.write_text(transcript, encoding="utf-8")

    await update.message.reply_text("Transcribed and saved.")


async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages: save image and optional caption."""
    assert update.message is not None
    assert update.effective_user is not None
    user_id = update.effective_user.id
    _, session_path = get_current_session(context, user_id)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Get the largest photo
    photo = update.message.photo[-1]
    file = await photo.get_file()

    # Download image
    img_path = session_path / f"{timestamp}.jpg"
    await file.download_to_drive(str(img_path))

    # Save caption if present
    if update.message.caption:
        md_path = session_path / f"{timestamp}.md"
        md_path.write_text(update.message.caption, encoding="utf-8")

    await update.message.reply_text("Photo saved.")


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document/file uploads: save to current session folder."""
    assert update.message is not None
    assert update.effective_user is not None
    user_id = update.effective_user.id
    _, session_path = get_current_session(context, user_id)

    document = update.message.document
    assert document is not None
    file = await document.get_file()

    # Use original filename if available, otherwise timestamp-based
    if document.file_name:
        filename = document.file_name
    else:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.bin"

    file_path = session_path / filename
    await file.download_to_drive(str(file_path))

    # Save caption if present
    if update.message.caption:
        stem = file_path.stem
        md_path = session_path / f"{stem}.md"
        md_path.write_text(update.message.caption, encoding="utf-8")

    await update.message.reply_text(f"File saved: {filename}")
