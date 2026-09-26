"""AI Scorer - Gemini Vision untuk deteksi skor Comstock."""
import streamlit as st
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import json

def prediksi_skor_dari_foto(image_bytes):
    """
    Analisa foto sisa makanan dengan Gemini Vision.
    Return: dict {nasi, sayur, lauk, confidence, alasan} atau None
    """
    try:
        # Ambil API key dari secrets
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key:
            st.warning("⚠️ GEMINI_API_KEY belum di-set di Secrets.")
            return None
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        img = Image.open(BytesIO(image_bytes))
        
        prompt = """
        Anda ahli gizi menganalisa foto tray makanan MBG Indonesia.
        
        Tray kompartemen:
        - Kiri atas: SAYUR
        - Kiri bawah: LAUK
        - Kanan atas: NASI (biasanya kosong karena dipindah)
        - Bawah: BUAH
        
        Fokus pada NASI, SAYUR, dan LAUK.
        
        Tentukan skor Comstock 0-5 untuk setiap komponen:
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
            "alasan": "<penjelasan singkat>"
        }
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        
        # Bersihkan markdown code block
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
