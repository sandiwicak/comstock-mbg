"""AI Scorer - Gemini Vision (dengan debug error)."""
from google import genai
from PIL import Image
from io import BytesIO
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
            st.error("❌ Debug: GEMINI key tidak ada di credentials.json")
            return None
        
        st.info(f"🔍 Debug: API key ditemukan (panjang {len(api_key)})")
        
        client = genai.Client(api_key=api_key)
        
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
        
        st.info("🔍 Debug: Mengirim foto ke Gemini...")
        
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[prompt, img]
        )
        
        st.info(f"🔍 Debug: Response diterima!")
        
        text = response.text.strip()
        
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        result = json.loads(text)
        st.success(f"✅ Debug: Berhasil parse JSON: {result}")
        return result
        
    except Exception as e:
        st.error(f"❌ Error Gemini: {type(e).__name__}: {e}")
        return None
