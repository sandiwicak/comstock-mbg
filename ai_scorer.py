"""AI Scorer - Groq Vision API dengan auto-retry."""
import requests
import base64
import json
import os
import time
from PIL import Image
from io import BytesIO


def get_groq_key():
    if os.path.exists("config.json"):
        with open("config.json") as f:
            config = json.load(f)
            return config.get("groq_api_key", "")
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
    """Coba 5x dengan 3 model berbeda. Return dict atau None."""
    try:
        api_key = get_groq_key()
        if not api_key:
            return None

        image_bytes = compress_image(image_bytes)
        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        Analisa foto tray makanan MBG Indonesia.
        Kompartemen: kiri atas SAYUR, kiri bawah LAUK, kanan atas NASI.
        Skor Comstock 0-5: 0=Habis, 1=Tersisa 1/4, 2=Tersisa 1/2,
        3=Tersisa 3/4, 4=Hampir utuh, 5=Utuh.
        Jawab HANYA JSON: {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        url = "https://api.groq.com/openai/v1/chat/completions"

        models = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "qwen/qwen3.8-27b",
            "meta-llama/llama-4-maverick-17b-128e-instruct"
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }

        # RETRY 5x dengan 3 model
        for attempt in range(5):
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
                        result = json.loads(text)
                        print(f"[AI] ✅ Sukses dengan {model} (attempt {attempt+1})")
                        return result

                    elif response.status_code == 429:
                        # Rate limit, tunggu lebih lama
                        time.sleep(8)
                        continue

                    elif response.status_code == 404:
                        # Model tidak ada, langsung coba model berikutnya
                        continue

                    else:
                        # Error lain, tunggu sebentar
                        time.sleep(3)
                        continue

                except requests.exceptions.Timeout:
                    time.sleep(3)
                    continue
                except json.JSONDecodeError:
                    time.sleep(2)
                    continue
                except Exception:
                    continue

            # Jeda antar attempt
            time.sleep(3)

        print("[AI] ❌ Gagal semua attempt")
        return None

    except Exception:
        return None
