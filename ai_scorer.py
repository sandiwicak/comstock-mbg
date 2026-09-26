"""AI Scorer - Gemini via Service Account."""
import requests
from PIL import Image
from io import BytesIO
import base64
import json
import os
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import google.auth.transport.requests


def get_credentials_dict():
    """Ambil credentials dari credentials.json."""
    if os.path.exists("credentials.json"):
        with open("credentials.json") as f:
            return json.load(f)
    return None


def get_access_token():
    """Dapatkan access token dari Service Account."""
    creds_dict = get_credentials_dict()
    if not creds_dict:
        return None
    
    scope = ["https://www.googleapis.com/auth/generative-language"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    
    # Refresh untuk dapat access token
    import google.auth.transport.requests
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    
    return creds.token


def prediksi_skor_dari_foto(image_bytes):
    try:
        # Dapatkan access token dari service account
        access_token = get_access_token()
        
        if not access_token:
            st.error("❌ Gagal dapat access token dari service account")
            return None
        
        # Convert image ke base64
        img_b64 = base64.b64encode(image_bytes).decode('utf-8')
        
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
        
        # REST API call dengan access token
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        
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
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        st.info("🔍 Debug: Mengirim foto ke Gemini via Service Account...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        st.info(f"🔍 Debug: HTTP Status = {response.status_code}")
        
        if response.status_code != 200:
            st.error(f"❌ Error: {response.status_code}")
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
