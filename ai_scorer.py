"""AI Scorer - Groq Vision API (dengan debug)."""
import requests
import base64
import json
import streamlit as st


def get_groq_key():
    """Ambil API key Groq dari Streamlit Secrets (digabung dari 2 bagian)."""
    try:
        p1 = st.secrets.get("groq_p1", "")
        p2 = st.secrets.get("groq_p2", "")
        return p1 + p2
    except Exception:
        return ""


def prediksi_skor_dari_foto(image_bytes):
    """Prediksi skor Comstock dari foto. Return dict atau None."""
    try:
        api_key = get_groq_key()

        # DEBUG: cek panjang key
        st.info(f"🔍 Debug: API key panjang = {len(api_key)} karakter")

        if not api_key:
            st.error("❌ Debug: API key kosong")
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

        st.info("🔍 Debug: Mengirim request ke Groq...")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        st.info(f"🔍 Debug: HTTP Status = {response.status_code}")

        if response.status_code == 401:
            st.error("❌ Debug: API key SALAH (401 Unauthorized)")
            st.error(f"Detail: {response.text[:300]}")
            return None

        if response.status_code == 429:
            st.warning("⚠️ Debug: QUOTA HABIS (429 Rate Limit)")
            st.warning(f"Detail: {response.text[:300]}")
            return None

        if response.status_code == 404:
            st.error("❌ Debug: Model TIDAK DITEMUKAN (404)")
            st.error(f"Detail: {response.text[:300]}")
            return None

        if response.status_code != 200:
            st.error(f"❌ Debug: Error {response.status_code}")
            st.error(f"Detail: {response.text[:500]}")
            return None

        data = response.json()
        text = data["choices"][0]["message"]["content"]
        text = text.strip()

        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        st.success(f"✅ Debug: Response OK")
        result = json.loads(text)
        return result

    except Exception as e:
        st.error(f"❌ Debug Exception: {type(e).__name__}: {e}")
        return None
