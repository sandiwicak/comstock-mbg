"""AI Scorer - OpenRouter Vision API."""
import requests
import base64
import json
import os
import time
from PIL import Image
from io import BytesIO


def get_openrouter_key():
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)
            return config.get("openrouter_api_key", "")
    return ""


def compress_image(image_bytes, max_size=640, quality=70):
    try:
        img = Image.open(BytesIO(image_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.LANCZOS)
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        return buffer.getvalue()
    except Exception:
        return image_bytes


def prediksi_skor_dari_foto(image_bytes):
    try:
        api_key = get_openrouter_key()
        if not api_key:
            return None

        image_bytes = compress_image(image_bytes)
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        Kompartemen: kiri atas SAYUR, kiri bawah LAUK, kanan atas NASI.
        Fokus NASI, SAYUR, LAUK.
        Skor Comstock 0-5: 0=Habis, 1=Tersisa 1/4, 2=Tersisa 1/2,
        3=Tersisa 3/4, 4=Hampir utuh, 5=Utuh.
        Jawab HANYA JSON: {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        url = "https://openrouter.ai/api/v1/chat/completions"

        # Model gratis yang bisa lihat gambar
        models = [
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "qwen/qwen2.5-vl-72b-instruct:free",
            "meta-llama/llama-4-scout-17b-16e-instruct:free"
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key,
            "HTTP-Referer": "https://comstock-mbg.streamlit.app",
            "X-Title": "Comstock Digital MBG"
        }

        for attempt in range(3):
            for model in models:
                try:
                    payload = {
                        "model": model,
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + img_b64}}
                            ]
                        }],
                        "temperature": 0.1,
                        "max_tokens": 400
                    }

                    response = requests.post(url, json=payload, headers=headers, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        text = data["choices"][0]["message"]["content"].strip()
                        if "```" in text:
                            text = text.split("```")[1]
                            if text.startswith("json"):
                                text = text[4:]
                        text = text.strip()
                        return json.loads(text)

                    elif response.status_code == 429:
                        time.sleep(5)
                        continue

                    else:
                        continue

                except Exception:
                    continue

            time.sleep(3)

        return None

    except Exception:
        return None
