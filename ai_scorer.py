"""AI Scorer - Gemini Vision."""
import streamlit as st
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import json


def get_gemini_key():
    """Ambil API key Gemini, gabung dari 2 bagian."""
    try:
        part1 = st.secrets.get("GEMINI_KEY_PART1", "")
        part2 = st.secrets.get("GEMINI_KEY_PART2", "")
        return part1 + part2
    except Exception:
        return ""


def prediksi_skor_dari_foto(image_bytes):
    try:
        api_key = get_gemini_key()
        
        if not api_key:
            st.warning("⚠️ GEMINI_KEY tidak tersedia di Secrets.")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        img = Image.open(BytesIO(image_bytes))
        
        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        
        Tray kompartemen:
        - Kiri atas: SAYUR
        - Kiri bawah: LAUK
        - Kanan atas: NASI
        - Bawah: BUAH
        
        Tentukan skor Comstock 0-5 untuk NASI, SAYUR, LAUK:
        - 0 = Habis total (0% sisa)
        - 1 = Tersisa 1/4 porsi (25% sisa)
        - 2 = Tersisa 1/2 porsi (50% sisa)
        - 3 = Tersisa 3/4 porsi (75% sisa)
        - 4 = Hampir utuh (95% sisa)
        - 5 = Utuh (100% sisa)
        
        Jawab HANYA dalam format JSON:
        {
            "nasi": <skor 0-5>,
            "sayur": <skor 0-5>,
            "lauk": <skor 0-5>,
            "confidence": <0.0-1.0>,
            "alasan": "<penjelasan>"
        }
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        result = json.loads(text)
        return result
        
    except Exception as e:
        st.error(f"❌ Error Gemini: {e}")
        return None
