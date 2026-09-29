"""AI Scorer - Groq Vision API dengan rotasi API key."""
import requests
import base64
import json
import os
import time
from PIL import Image
from io import BytesIO
import streamlit as st

from gsheet_helper import ambil_api_keys


# Cache API keys per session
def get_api_keys():
    """Ambil list API key Groq dari sheet APIKey."""
    if "api_keys_cache" not in st.session_state:
        st.session_state.api_keys_cache = ambil_api_keys()
        st.session_state.api_key_index = 0
    return st.session_state.api_keys_cache


def get_current_key():
    """Ambil API key saat ini."""
    keys = get_api_keys()
    if not keys:
        return None
    idx = st.session_state.get("api_key_index", 0) % len(keys)
    return keys[idx]


def rotate_key():
    """Pindah ke API key berikutnya."""
    keys = get_api_keys()
    if not keys:
        return False
    st.session_state.api_key_index = (st.session_state.get("api_key_index", 0) + 1) % len(keys)
    print(f"[AI] Rotasi ke key index {st.session_state.api_key_index}")
    return True


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
    """Coba dengan rotasi API key otomatis."""
    try:
        keys = get_api_keys()
        if not keys:
            print("[AI] Tidak ada API key di sheet APIKey")
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

        # Coba semua API key, semua model
        total_keys = len(keys)
        for key_attempt in range(total_keys):
            api_key = get_current_key()
            if not api_key:
                break

            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + api_key
            }

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
                        print(f"[AI] Sukses dengan key index {st.session_state.api_key_index}, model {model}")
                        return json.loads(text)

                    elif response.status_code == 429:
                        # Rate limit - coba model lain dulu, baru rotasi key
                        print(f"[AI] 429 rate limit di key {st.session_state.api_key_index}")
                        time.sleep(2)
                        continue

                    elif response.status_code == 401:
                        # API key invalid - langsung rotasi
                        print(f"[AI] 401 invalid key di index {st.session_state.api_key_index}")
                        break  # keluar dari loop model, rotasi key

                    else:
                        time.sleep(1)
                        continue

                except Exception as e:
                    print(f"[AI] Error: {e}")
                    continue

            # Setelah coba semua model dengan key ini, rotasi
            rotate_key()
            time.sleep(1)

        print("[AI] Semua API key dan model gagal")
        return None

    except Exception as e:
        print(f"[AI] Exception utama: {e}")
        return None
