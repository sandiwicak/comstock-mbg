"""AI Scorer - Groq Vision API dengan retry super agresif."""
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


def compress_image(image_bytes, max_size=800, quality=80):
    """Compress gambar lebih agresif biar cepat diproses."""
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
    """Prediksi skor Comstock dengan 7 model, 10x retry."""
    try:
        api_key = get_groq_key()
        if not api_key:
            print("[AI] API key kosong")
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

        url = "https://api.groq.com/openai/v1/chat/completions"

        # 7 MODEL FALLBACK
        models = [
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "qwen/qwen3.8-27b",
            "qwen/qwen2.5-vl-72b-instruct",
            "qwen/qwen2.5-vl-32b-instruct",
            "llava-v1.5-7b-4096-preview",
            "gemma2-9b-it"
        ]

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + api_key
        }

        # 10x RETRY, tiap kali coba semua 7 model
        for attempt in range(10):
            for model in models:
                try:
                    payload = {
                        "model": model,
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

                    print(f"[AI] Attempt {attempt+1}, model: {model}")
                    response = requests.post(url, json=payload, headers=headers, timeout=90)

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
                        print(f"[AI] SUKSES dengan {model}")
                        return result

                    elif response.status_code == 429:
                        print(f"[AI] Rate limit 429, tunggu 8 detik...")
                        time.sleep(8)
                        continue

                    elif response.status_code == 404:
                        # Model tidak ada, langsung coba model berikutnya
                        print(f"[AI] Model {model} tidak ada (404)")
                        continue

                    elif response.status_code >= 500:
                        print(f"[AI] Server error {response.status_code}, tunggu 5 detik...")
                        time.sleep(5)
                        continue

                    else:
                        print(f"[AI] Error {response.status_code}: {response.text[:200]}")
                        time.sleep(3)
                        continue

                except requests.exceptions.Timeout:
                    print(f"[AI] Timeout dengan {model}")
                    time.sleep(3)
                    continue
                except json.JSONDecodeError as e:
                    print(f"[AI] JSON error: {e}")
                    time.sleep(2)
                    continue
                except Exception as e:
                    print(f"[AI] Error: {e}")
                    continue

            # Jeda antar attempt besar
            print(f"[AI] Attempt {attempt+1} selesai, jeda 5 detik...")
            time.sleep(5)

        print("[AI] SEMUA ATTEMPT GAGAL")
        return None

    except Exception as e:
        print(f"[AI] Exception utama: {e}")
        return None
