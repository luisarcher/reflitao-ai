import base64
from typing import Any, cast

import openai

# type: ignore[override]


def generate_image(api_key: str, description: str) -> bytes:
    client = openai.OpenAI(api_key=api_key)
    response = client.images.generate(
        model="gpt-image-2",
        prompt=description,
    )
    # gpt-image-2 returns base64-encoded image data
    b64_str = cast(Any, response.data)[0].b64_json
    image_data = base64.b64decode(b64_str)
    return image_data
