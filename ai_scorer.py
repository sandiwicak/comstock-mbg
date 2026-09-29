"""AI Scorer - Groq Vision API dengan API key dinamis."""
import requests
import base64
import json
import os
import time
from PIL import Image
from io import BytesIO
import streamlit as st


def get_groq_key():
    """Ambil API key dari session state (input user) atau config.json."""
    # Prioritas 1: session state (input user)
    if "groq_api_key_input" in st.session_state and st.session_state.groq_api_key_input:
        return st.session_state.groq_api_key_input.strip()
    
    # Prioritas 2: config.json
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
    """Coba 5x dengan 3 model. Return dict atau None."""
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
                        return json.loads(text)

                    elif response.status_code == 429:
                        # Rate limit / quota habis
                        print(f"[AI] 429 rate limit, tunggu 8s...")
                        time.sleep(8)
                        continue

                    elif response.status_code == 401:
                        # API key invalid
                        print(f"[AI] 401 invalid API key!")
                        return None

                    else:
                        time.sleep(3)
                        continue

                except Exception:
                    continue

            time.sleep(3)

        return None

    except Exception:
        return None
