"""AI Scorer - Groq Vision API."""
import requests
import base64
import json
import os
import streamlit as st


def get_groq_key():
    """Ambil API key Groq dari credentials.json."""
    if os.path.exists("credentials.json"):
        with open("credentials.json") as f:
            config = json.load(f)
            return config.get("groq_api_key", "")
    return ""


def prediksi_skor_dari_foto(image_bytes):
    try:
        api_key = get_groq_key()

        if not api_key:
            st.error("GROQ key tidak ada di credentials.json")
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

        url = "https://api.groq.com/openai/v1/chat/completions"

        payload = {
            "model": "qwen/qwen3.6-27b",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_b64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 0.1
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

        st.info("Mengirim foto ke Groq...")

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        st.info("HTTP Status = " + str(response.status_code))

        if response.status_code != 200:
            st.error("Error: " + str(response.status_code))
            st.error("Detail: " + response.text[:500])
            return None

        data = response.json()
        text = data["choices"][0]["message"]["content"]
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
