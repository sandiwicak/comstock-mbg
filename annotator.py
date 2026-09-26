"""Tools Anotasi Comstock - Manual Cepat untuk Banyak Foto."""
import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="Anotasi Comstock",
    page_icon="🏷️",
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Poppins', sans-serif !important; color: #1a1a1a; }
    .stApp { background: #f6e3b4 !important; }
    .main-header { background: linear-gradient(135deg, #efd48a 0%, #f6e3b4 100%); border: 2px solid #c99a3a; border-radius: 20px; padding: 1.5rem; text-align: center; margin-bottom: 1.5rem; }
    .main-header h1 { color: #1a1a1a !important; font-size: 1.6rem; font-weight: 800; margin: 0; }
    .main-header p { color: #5c3a1a !important; font-size: 0.85rem; margin: 0.5rem 0 0 0; }
    .card { background: #ffffff; border: 2px solid #c99a3a; border-radius: 16px; padding: 1.5rem; margin-bottom: 1rem; }
    .section-title { color: #1a1a1a !important; font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 3px solid #c99a3a; display: inline-block; }
    .stButton > button { background: #c99a3a !important; color: white !important; border: none !important; border-radius: 22px !important; padding: 0.8rem 1.5rem !important; font-weight: 600 !important; width: 100% !important; }
    .stButton > button:hover { background: #8a5a2b !important; }
    .stButton > button p, .stButton > button span { color: white !important; }
    .stSelectbox [data-baseweb="select"] > div { background-color: #1a1a1a !important; color: white !important; border-radius: 10px !important; }
    .stSelectbox [data-baseweb="select"] span { color: white !important; -webkit-text-fill-color: white !important; }
    .stSelectbox [data-baseweb="select"] svg { fill: white !important; }
    [role="listbox"] { background-color: #1a1a1a !important; }
    [role="option"] { background-color: #1a1a1a !important; color: white !important; }
    [role="option"]:hover { background-color: #c99a3a !important; color: #1a1a1a !important; }
    [aria-selected="true"] { background-color: #c99a3a !important; color: #1a1a1a !important; }
    .stTextInput input, .stNumberInput input, .stDateInput input { background-color: #1a1a1a !important; color: white !important; -webkit-text-fill-color: white !important; border-radius: 10px !important; border: 2px solid #1a1a1a !important; }
    .stTextInput input::placeholder { color: #888888 !important; -webkit-text-fill-color: #888888 !important; }
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label, .stFileUploader label { color: #1a1a1a !important; font-weight: 600 !important; }
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #5c3a1a !important; }
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1a1a1a; }
    .stFileUploader > div > div { border: 2px dashed #c99a3a !important; border-radius: 12px !important; background: #f6e3b4 !important; }
    .stFileUploader > div > div > div { color: #1a1a1a !important; }
    .stFileUploader button { background-color: #c99a3a !important; color: white !important; border-radius: 10px !important; }
    [data-testid="stFileUploaderFile"] { background-color: #1a1a1a !important; }
    [data-testid="stFileUploaderFile"] * { color: white !important; -webkit-text-fill-color: white !important; }
    .stAlert { border-radius: 12px !important; }
    .stAlert p { color: #1a1a1a !important; }
    .stProgress > div > div > div > div { background: #c99a3a !important; }
    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>🏷️ ANOTASI COMSTOCK</h1>
    <p>Input Skor Manual Cepat</p>
</div>
""", unsafe_allow_html=True)

# Session state
if "hasil_anotasi" not in st.session_state:
    st.session_state.hasil_anotasi = []
if "foto_processed" not in st.session_state:
    st.session_state.foto_processed = set()
if "uploader_key_version" not in st.session_state:
    st.session_state.uploader_key_version = 0

# Setup
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">⚙️ Setup</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    tanggal = st.date_input("Tanggal", datetime.now(), key="an_tanggal")
    kode_sekolah = st.text_input("Kode Sekolah", value="SDN01-LB", key="an_sekolah")
with col2:
    ba_nasi = st.number_input("Berat Awal Nasi (g)", 0.0, 500.0, 136.0, key="an_ba_nasi")
    ba_sayur = st.number_input("Berat Awal Sayur (g)", 0.0, 500.0, 24.0, key="an_ba_sayur")
    ba_lauk = st.number_input("Berat Awal Lauk (g)", 0.0, 500.0, 64.0, key="an_ba_lauk")

st.markdown('</div>', unsafe_allow_html=True)

# Upload
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📷 Upload Foto (bisa banyak)</div>', unsafe_allow_html=True)

uploader_key = f"an_uploader_{st.session_state.uploader_key_version}"

foto_list = st.file_uploader(
    "Pilih foto",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True,
    key=uploader_key,
    label_visibility="collapsed"
)

if foto_list:
    st.success(f"✅ {len(foto_list)} foto terpilih")
    st.caption(f"Total sudah diinput: {len(st.session_state.hasil_anotasi)}")

    # Tampilkan progress
    total = len(foto_list) + len(st.session_state.hasil_anotasi)
    st.progress(len(st.session_state.hasil_anotasi) / total if total > 0 else 0)

    for i, foto in enumerate(foto_list):
        if foto.name in st.session_state.foto_processed:
            continue

        st.markdown(f"---")
        st.markdown(f"**📷 Foto {i+1} dari {len(foto_list)}: `{foto.name}`**")

        col1, col2 = st.columns([1, 2])

        with col1:
            st.image(foto, use_container_width=True)

        with col2:
            c1, c2, c3 = st.columns(3)
            with c1:
                sn = st.selectbox("🍚 Nasi", [0,1,2,3,4,5], key=f"sn_{i}_{foto.name}")
            with c2:
                ss = st.selectbox("🥬 Sayur", [0,1,2,3,4,5], key=f"ss_{i}_{foto.name}")
            with c3:
                sl = st.selectbox("🍗 Lauk", [0,1,2,3,4,5], key=f"sl_{i}_{foto.name}")

            ket = st.text_input("Keterangan (opsional)", key=f"ket_{i}_{foto.name}")

            if st.button(f"💾 Simpan Foto Ini", key=f"save_{i}_{foto.name}"):
                # Hitung
                total_awal = ba_nasi + ba_sayur + ba_lauk
                pn_map = {0:0, 1:0.25, 2:0.5, 3:0.75, 4:0.95, 5:1.0}
                pn = pn_map[sn]
                ps = pn_map[ss]
                pl = pn_map[sl]
                bsn = ba_nasi * pn
                bss = ba_sayur * ps
                bsl = ba_lauk * pl
                total_sisa = bsn + bss + bsl
                el = (total_sisa / total_awal * 15000) if total_awal > 0 else 0

                st.session_state.hasil_anotasi.append({
                    "Tanggal": str(tanggal),
                    "Kode Sekolah": kode_sekolah,
                    "ID Foto": foto.name,
                    "Skor Nasi": sn,
                    "Skor Sayur": ss,
                    "Skor Lauk": sl,
                    "Berat Awal Nasi": ba_nasi,
                    "Berat Sisa Nasi": round(bsn, 1),
                    "% Sisa Nasi": round(pn, 2),
                    "Berat Awal Sayur": ba_sayur,
                    "Berat Sisa Sayur": round(bss, 1),
                    "% Sisa Sayur": round(ps, 2),
                    "Berat Awal Lauk": ba_lauk,
                    "Berat Sisa Lauk": round(bsl, 1),
                    "% Sisa Lauk": round(pl, 2),
                    "Total Awal": total_awal,
                    "Total Sisa": round(total_sisa, 1),
                    "Economic Loss": round(el, 0),
                    "Keterangan": ket,
                })
                st.session_state.foto_processed.add(foto.name)
                st.success(f"✅ {foto.name} tersimpan! Lanjut foto berikutnya...")
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Hasil
if st.session_state.hasil_anotasi:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📋 Hasil ({len(st.session_state.hasil_anotasi)} foto)</div>', unsafe_allow_html=True)

    df = pd.DataFrame(st.session_state.hasil_anotasi)
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV (paste ke Google Sheets)",
        csv,
        f"anotasi_{kode_sekolah}_{tanggal}.csv",
        "text/csv",
        key="download_csv"
    )

    if st.button("🗑️ Reset Semua"):
        st.session_state.hasil_anotasi = []
        st.session_state.foto_processed = set()
        st.session_state.uploader_key_version += 1
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
