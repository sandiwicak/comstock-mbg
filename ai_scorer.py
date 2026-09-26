"""AI Scorer - Gemini via REST API (versi paling simpel)."""
import requests
import base64
import json
import os
import streamlit as st


def get_gemini_key():
    """Ambil API key Gemini dari credentials.json."""
    if os.path.exists("credentials.json"):
        with open("credentials.json") as f:
            config = json.load(f)
            return config.get("gemini_api_key", "")
    return ""


def prediksi_skor_dari_foto(image_bytes):
    try:
        api_key = get_gemini_key()

        if not api_key:
            st.error("GEMINI key tidak ada di credentials.json")
            return None

        img_b64 = base64.b64encode(image_bytes).decode("utf-8")

        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        Tentukan skor Comstock 0-5 untuk NASI, SAYUR, LAUK:
        0 = Habis total, 1 = Tersisa 1/4, 2 = Tersisa 1/2,
        3 = Tersisa 3/4, 4 = Hampir utuh, 5 = Utuh.
        Jawab HANYA JSON:
        {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=" + api_key

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": img_b64
                            }
                        }
                    ]
                }
            ]
        }

        st.info("Mengirim foto ke Gemini...")

        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )

        st.info("HTTP Status = " + str(response.status_code))

        if response.status_code != 200:
            st.error("Error: " + str(response.status_code))
            st.error("Detail: " + response.text[:500])
            return None

        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip()

        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        result = json.loads(text)
        st.success("Saran AI: " + str(result))
        return result

    except Exception as e:
        st.error("Error: " + type(e).__name__ + ": " + str(e))
        return None
