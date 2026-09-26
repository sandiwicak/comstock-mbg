"""AI Scorer - Groq Vision API."""
import requests
import base64
import json
import streamlit as st


def get_groq_key():
    """Ambil API key Groq dari Streamlit Secrets."""
    try:
        return st.secrets.get("groq_api_key", "")
    except Exception:
        return ""


def prediksi_skor_dari_foto(image_bytes):
    """Prediksi skor Comstock dari foto. Return dict atau None."""
    try:
        api_key = get_groq_key()

        if not api_key:
            return None

        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.

        Tray kompartemen:
        - Kiri atas: SAYUR
        - Kiri bawah: LAUK
        - Kanan atas: NASI
        - Bawah: BUAH

        Fokus pada NASI, SAYUR, dan LAUK.

        Tentukan skor Comstock 0-5:
        0 = Habis total (0% sisa)
        1 = Tersisa 1/4 porsi (25% sisa)
        2 = Tersisa 1/2 porsi (50% sisa)
        3 = Tersisa 3/4 porsi (75% sisa)
        4 = Hampir utuh (95% sisa)
        5 = Utuh (100% sisa)

        Jawab HANYA JSON:
        {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        url = "https://api.groq.com/openai/v1/chat/completions"

        payload = {
            "model": "qwen/qwen3.8-27b",
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

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        if response.status_code != 200:
            return None

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

    except Exception:
        return None
