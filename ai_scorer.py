"""AI Scorer - Groq Vision API dengan retry."""
import requests
import base64
import json
import os
import time
from PIL import Image
from io import BytesIO


def get_groq_key():
    """Ambil API key Groq dari config.json."""
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)
            return config.get("groq_api_key", "")
    return ""


def compress_image(image_bytes, max_size=1024):
    """Compress gambar biar tidak terlalu besar."""
    try:
        img = Image.open(BytesIO(image_bytes))
        # Resize kalau lebih besar dari max_size
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.LANCZOS)
        # Convert ke RGB kalau RGBA
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        # Save ke bytes
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return buffer.getvalue()
    except Exception:
        return image_bytes


def prediksi_skor_dari_foto(image_bytes):
    """Prediksi skor Comstock dari foto dengan retry."""
    try:
        api_key = get_groq_key()
        if not api_key:
            return None

        # Compress dulu
        image_bytes = compress_image(image_bytes)
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        Kompartemen: kiri atas SAYUR, kiri bawah LAUK, kanan atas NASI, bawah BUAH.
        Fokus NASI, SAYUR, LAUK.
        Tentukan skor Comstock 0-5:
        0 = Habis total, 1 = Tersisa 1/4, 2 = Tersisa 1/2,
        3 = Tersisa 3/4, 4 = Hampir utuh, 5 = Utuh.
        Jawab HANYA JSON:
        {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        url = "https://api.groq.com/openai/v1/chat/completions"

        # Coba 2 model
        models = [
            "qwen/qwen3.8-27b",
            "meta-llama/llama-4-scout-17b-16e-instruct"
        ]

        payload_base = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/jpeg;base64," + img_b64
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }

        # Retry 3 kali, coba tiap model
        for attempt in range(3):
            for model in models:
                try:
                    payload = dict(payload_base)
                    payload["model"] = model

                    response = requests.post(url, json=payload, headers=headers, timeout=30)

                    if response.status_code == 200:
                        data = response.json()
                        text = data["choices"][0]["message"]["content"]
                        text = text.strip()

                        if "```" in text:
                            text = text.split("```")[1]
                            if text.startswith("json"):
                                text = text[4:]
                        text = text.strip()

                        result = json.loads(text)
                        return result

                    elif response.status_code == 429:
                        # Rate limit, tunggu
                        time.sleep(2)
                        continue

                except Exception:
                    continue

            # Jeda antar attempt
            time.sleep(1)

        return None

    except Exception:
        return None
