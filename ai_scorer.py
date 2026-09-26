"""AI Scorer - Gemini 2.0 Flash via REST API."""
import requests
from io import BytesIO
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
            st.error("❌ GEMINI key tidak ada di credentials.json")
            return None
        
        img_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
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
            "alasan": "<penjelasan>"
        }
        """
        
       url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": api_key
}
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": img_b64
                        }
                    }
                ]
            }]
        }
        
        headers = {"Content-Type": "application/json"}
        
        st.info("🔍 Debug: Mengirim foto ke Gemini 2.0 Flash...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        st.info(f"🔍 Debug: HTTP Status = {response.status_code}")
        
        if response.status_code != 200:
            st.error(f"❌ Error dari Google: {response.status_code}")
            st.error(f"Detail: {response.text[:500]}")
            return None
        
        data = response.json()
        
        text = data['candidates'][0]['content']['parts'][0]['text']
        text = text.strip()
        
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        
        result = json.loads(text)
        st.success(f"✅ Saran AI: {result}")
        return result
        
    except Exception as e:
        st.error(f"❌ Error: {type(e).__name__}: {e}")
        return None
