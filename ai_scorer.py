"""AI Scorer - Gemini via google-genai SDK (paling stabil)."""
import os
import json
import streamlit as st
from google import genai
from PIL import Image
from io import BytesIO


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

        client = genai.Client(api_key=api_key)
        img = Image.open(BytesIO(image_bytes))

        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        Tentukan skor Comstock 0-5 untuk NASI, SAYUR, LAUK:
        0 = Habis total, 1 = Tersisa 1/4, 2 = Tersisa 1/2,
        3 = Tersisa 3/4, 4 = Hampir utuh, 5 = Utuh.
        Jawab HANYA JSON:
        {"nasi": 0, "sayur": 0, "lauk": 0, "confidence": 0.0, "alasan": "..."}
        """

        st.info("Mengirim foto ke Gemini...")

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, img]
        )

        text = response.text.strip()
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
