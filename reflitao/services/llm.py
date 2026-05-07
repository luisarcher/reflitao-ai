import base64
from pathlib import Path

import anthropic

from reflitao.config import DEFAULT_LLM_MODEL

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
AUDIO_EXTENSIONS = {".ogg", ".mp3", ".wav", ".m4a"}


def _build_context_blocks(session_path: str) -> list[dict]:
    """Build Anthropic content blocks from all session files."""
    session = Path(session_path)
    files = sorted(session.iterdir())

    md_basenames = {f.stem for f in files if f.suffix == ".md"}

    blocks: list[dict] = []

    for f in files:
        if not f.is_file():
            continue

        if f.suffix == ".md":
            text = f.read_text(encoding="utf-8")
            blocks.append({
                "type": "text",
                "text": f"--- {f.name} ---\n{text}",
            })
        elif f.suffix.lower() in IMAGE_EXTENSIONS:
            data = base64.standard_b64encode(f.read_bytes()).decode("ascii")
            media_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
            }
            media_type = media_type_map.get(f.suffix.lower(), "image/jpeg")
            blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": data,
                },
            })
            blocks.append({
                "type": "text",
                "text": f"[Image: {f.name}]",
            })
        elif f.suffix.lower() in AUDIO_EXTENSIONS:
            if f.stem in md_basenames:
                continue
            blocks.append({
                "type": "text",
                "text": f"[Audio file: {f.name} — no transcript available]",
            })

    return blocks


def call_llm(api_key: str, prompt: str, session_path: str | None = None) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    content: list[dict] = []

    if session_path:
        context_blocks = _build_context_blocks(session_path)
        if context_blocks:
            content.extend(context_blocks)
            content.append({
                "type": "text",
                "text": f"\n--- User Prompt ---\n{prompt}",
            })
        else:
            content.append({"type": "text", "text": prompt})
    else:
        content.append({"type": "text", "text": prompt})

    response = client.messages.create(
        model=DEFAULT_LLM_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": content}],
    )

    # Extract text from response
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)


def split_message(text: str, limit: int = 4096) -> list[str]:
    """Split a message into chunks respecting Telegram's character limit."""
    if len(text) <= limit:
        return [text]

    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Try to split at a newline
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks
