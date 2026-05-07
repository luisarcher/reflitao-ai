import base64

import openai


def generate_image(api_key: str, description: str) -> bytes:
    client = openai.OpenAI(api_key=api_key)
    response = client.images.generate(
        model="gpt-image-2",
        prompt=description,
    )
    # gpt-image-2 returns base64-encoded image data
    image_data = base64.b64decode(response.data[0].b64_json)
    return image_data
