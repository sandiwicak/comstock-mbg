"""Comstock Digital MBG - Auto Upload + AI + Simpan (1 per 1)."""
import streamlit as st
import pandas as pd
import time
from datetime import datetime

from comstock_utils import (
    skor_ke_persentase_sisa, hitung_economic_loss,
    COMSTOCK_MAPPING, KETERANGAN_SKOR, SEKOLAH_LIST
)
from gsheet_helper import simpan_data, ambil_semua_data
from ai_scorer import prediksi_skor_dari_foto


st.set_page_config(
    page_title="Comstock Digital MBG",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif !important; 
        color: #1a1a1a;
    }
    
    .stApp { background: #f6e3b4 !important; }
    
    .main-header {
        background: linear-gradient(135deg, #efd48a 0%, #f6e3b4 100%);
        border: 2px solid #c99a3a;
        border-radius: 20px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(138, 90, 43, 0.15);
    }
    .main-header h1 { color: #1a1a1a !important; font-size: 1.8rem; font-weight: 800; margin: 0; letter-spacing: 1px; }
    .main-header p { color: #5c3a1a !important; font-size: 0.85rem; margin: 0.5rem 0 0 0; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; }
    
    .card { 
        background: #ffffff; 
        border: 2px solid #c99a3a; 
        border-radius: 16px; 
        padding: 1.5rem; 
        margin-bottom: 1rem; 
        box-shadow: 0 4px 12px rgba(138, 90, 43, 0.08); 
    }
    .section-title { color: #1a1a1a !important; font-size: 1.1rem; font-weight: 700; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 3px solid #c99a3a; display: inline-block; }
    
    .metric-card { background: linear-gradient(135deg, #c99a3a 0%, #8a5a2b 100%); border-radius: 14px; padding: 1.1rem; color: white; text-align: center; margin: 0.3rem 0; }
    .metric-value { font-size: 1.6rem; font-weight: 800; color: white; }
    .metric-label { font-size: 0.72rem; opacity: 0.95; letter-spacing: 1px; text-transform: uppercase; margin-top: 0.3rem; color: white; }
    .metric-card-red { background: linear-gradient(135deg, #c0392b 0%, #8a1a10 100%); border-radius: 14px; padding: 1.1rem; color: white; text-align: center; margin: 0.3rem 0; }
    
    .stButton > button { background: #c99a3a !important; color: white !important; border: none !important; border-radius: 22px !important; padding: 0.8rem 1.5rem !important; font-weight: 600 !important; width: 100% !important; }
    .stButton > button:hover { background: #8a5a2b !important; }
    .stButton > button p, .stButton > button span { color: #ffffff !important; }
    
    /* TEXT INPUT */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #1a1a1a !important; 
        border-radius: 10px !important; 
    }
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder { 
        color: #888888 !important; 
        -webkit-text-fill-color: #888888 !important; 
    }
    
    /* NUMBER INPUT */
    .stNumberInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 600 !important;
        border: 2px solid #1a1a1a !important;
        border-radius: 10px !important;
    }
    .stNumberInput > div > div > input::placeholder {
        color: #888888 !important;
        -webkit-text-fill-color: #888888 !important;
    }
    .stNumberInput button {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        border: 1px solid #333333 !important;
    }
    .stNumberInput button:hover {
        background-color: #c99a3a !important;
    }
    .stNumberInput button svg,
    .stNumberInput button p {
        fill: #ffffff !important;
        color: #ffffff !important;
    }
    
    /* DATE INPUT */
    .stDateInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #1a1a1a !important;
        border-radius: 10px !important;
    }
    
    /* SELECTBOX */
    .stSelectbox > div > div { background-color: #1a1a1a !important; border: 2px solid #1a1a1a !important; border-radius: 10px !important; color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] > div { background-color: #1a1a1a !important; color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] span { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] svg { fill: #ffffff !important; }
    [role="listbox"] { background-color: #1a1a1a !important; }
    [role="option"] { background-color: #1a1a1a !important; color: #ffffff !important; }
    [role="option"]:hover { background-color: #c99a3a !important; color: #1a1a1a !important; }
    [aria-selected="true"] { background-color: #c99a3a !important; color: #1a1a1a !important; }
    
    /* LABELS */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label, .stFileUploader label, .stDateInput label { color: #1a1a1a !important; font-weight: 600 !important; }
    
    /* CAPTION */
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #5c3a1a !important; font-weight: 500 !important; }
    
    /* MARKDOWN */
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1a1a1a; }
    
    /* EXPANDER HITAM */
    [data-testid="stExpander"] {
        border: 2px solid #1a1a1a !important;
        border-radius: 12px !important;
        background: #1a1a1a !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary *,
    [data-testid="stExpander"] summary p,
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary svg {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        fill: #ffffff !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] details *,
    [data-testid="stExpander"] details p,
    [data-testid="stExpander"] details span,
    [data-testid="stExpander"] details label,
    [data-testid="stExpander"] details div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stExpander"] .stNumberInput > div > div > input,
    [data-testid="stExpander"] .stTextInput > div > div > input {
        border: 2px solid #ffffff !important;
        border-radius: 10px !important;
    }
    [data-testid="stExpander"] .stNumberInput button {
        border: 2px solid #ffffff !important;
        border-radius: 6px !important;
    }
    
    /* FILE UPLOADER */
    .stFileUploader > div > div { border: 2px dashed #c99a3a !important; border-radius: 12px !important; background: #f6e3b4 !important; }
    .stFileUploader > div > div > div { color: #1a1a1a !important; }
    .stFileUploader button { background-color: #c99a3a !important; color: white !important; border-radius: 10px !important; border: none !important; }
    [data-testid="stFileUploaderFile"], [data-testid="stUploadedFile"], [data-testid="stFileUploaderFileName"] { background-color: #1a1a1a !important; }
    [data-testid="stFileUploaderFile"] *, [data-testid="stUploadedFile"] *, [data-testid="stFileUploaderFileName"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    [data-testid="stFileUploaderDeleteBtn"] svg { fill: #ffffff !important; }
    
    /* ALERT */
    .stAlert { border-radius: 12px !important; }
    .stAlert p { color: #1a1a1a !important; }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { background: #efd48a; border-right: 2px solid #c99a3a; }
    section[data-testid="stSidebar"] * { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] .stButton > button { background: white !important; color: #1a1a1a !important; border: 2px solid #8a5a2b !important; border-radius: 12px; margin-bottom: 0.5rem; }
    section[data-testid="stSidebar"] .stButton > button p { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] .stButton > button:hover { background: #8a5a2b !important; }
    section[data-testid="stSidebar"] .stButton > button:hover p { color: white !important; }
    
    /* PROGRESS */
    .stProgress > div > div > div > div { background: #c99a3a !important; }
    
    /* METRIC NATIVE */
    [data-testid="stMetricValue"] { color: #1a1a1a !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #5c3a1a !important; font-weight: 600 !important; }
    
    /* DATAFRAME */
    .stDataFrame, .stDataFrame * { color: #1a1a1a; }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    @media (max-width: 768px) { 
        .main-header h1 { font-size: 1.3rem; } 
        .card { padding: 1rem; } 
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "halaman" not in st.session_state: st.session_state.halaman = "upload"
if "kode_sekolah" not in st.session_state: st.session_state.kode_sekolah = "SDN01-LB"
if "nama_enum" not in st.session_state: st.session_state.nama_enum = "Enumerator"
if "uploader_version" not in st.session_state: st.session_state.uploader_version = 0
if "processed_files" not in st.session_state: st.session_state.processed_files = set()

user = {
    "nama": st.session_state.nama_enum,
    "kode_sekolah": st.session_state.kode_sekolah,
    "email": "-"
}

# Sidebar
with st.sidebar:
    st.markdown("### 🏫 Pilih Sekolah")
    sekolah_options = list(SEKOLAH_LIST.keys())
    pilihan = st.selectbox(
        "Sekolah", 
        options=sekolah_options,
        format_func=lambda x: SEKOLAH_LIST[x],
        key="sekolah_selector",
        label_visibility="collapsed"
    )
    st.session_state.kode_sekolah = pilihan
    user["kode_sekolah"] = pilihan
    
    st.markdown("---")
    nama_input = st.text_input("Nama Anda (opsional)", value=st.session_state.nama_enum, key="nama_enum_input")
    st.session_state.nama_enum = nama_input if nama_input else "Enumerator"
    user["nama"] = st.session_state.nama_enum
    
    st.markdown("---")
    if st.button("📸 Upload Foto", key="btn_upload"): 
        st.session_state.halaman = "upload"
        st.rerun()
    if st.button("📊 Dashboard", key="btn_dashboard"): 
        st.session_state.halaman = "dashboard"
        st.rerun()

# Header
st.markdown(f"""
<div class="main-header">
    <h1>🌿 COMSTOCK DIGITAL</h1>
    <p>{SEKOLAH_LIST.get(user['kode_sekolah'], user['kode_sekolah'])} — {user['nama']}</p>
</div>
""", unsafe_allow_html=True)

# ==================== HALAMAN UPLOAD ====================
if st.session_state.halaman == "upload":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📸 Upload Foto Sisa</div>', unsafe_allow_html=True)
    st.caption("Upload foto → AI cek 1 per 1 → langsung simpan. Kalau gagal, tahu foto ke berapa.")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        tanggal_upload = st.date_input("Tanggal", datetime.now(), key="tanggal_input")
    with col2:
        harga_upload = st.number_input("Harga Porsi (Rp)", 0.0, 100000.0, 15000.0, key="harga_input")
    with col3:
        hari_ke = st.number_input("Hari Ke-", 1, 30, 1, key="hari_input")
    
    with st.expander("⚖️ Berat Awal Referensi (klik untuk ubah)"):
        col1, col2, col3 = st.columns(3)
        with col1: ba_nasi = st.number_input("Nasi (g)", 0.0, 500.0, 136.0, key="ba_nasi_input")
        with col2: ba_sayur = st.number_input("Sayur (g)", 0.0, 500.0, 24.0, key="ba_sayur_input")
        with col3: ba_lauk = st.number_input("Lauk (g)", 0.0, 500.0, 64.0, key="ba_lauk_input")
    
    st.markdown("---")
    st.markdown("**📷 Upload Foto Sisa (bisa banyak sekaligus)**")
    
    uploader_key = f"file_uploader_v{st.session_state.uploader_version}"
    
    foto_list = st.file_uploader(
        "Pilih foto sisa makanan",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key=uploader_key,
        label_visibility="collapsed"
    )
    
    if foto_list:
        foto_baru = [f for f in foto_list if f.name not in st.session_state.processed_files]
        
        if foto_baru:
            st.info(f"🔄 Memproses {len(foto_baru)} foto (1 per 1)...")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_area = st.empty()
            
            sukses = 0
            gagal = 0
            gagal_ai = 0
            error_detail = []
            gagal_di = None
            
            timestamp_id = datetime.now().strftime("%H%M%S")
            
            for i, foto in enumerate(foto_baru):
                status_text.info(f"⏳ Foto {i+1}/{len(foto_baru)}: {foto.name}")
                
                nasi_val = 0
                sayur_val = 0
                lauk_val = 0
                ket_val = ""
                
                # 1. AI cek
                try:
                    skor_ai = prediksi_skor_dari_foto(foto.getvalue())
                    if skor_ai:
                        nasi_val = int(skor_ai.get("nasi", 0))
                        sayur_val = int(skor_ai.get("sayur", 0))
                        lauk_val = int(skor_ai.get("lauk", 0))
                        ket_val = skor_ai.get("alasan", "")
                    else:
                        gagal_ai += 1
                except Exception as e:
                    gagal_ai += 1
                    print(f"[ERROR AI] Foto {i+1}: {e}")
                
                # 2. Hitung
                total_awal = ba_nasi + ba_sayur + ba_lauk
                pn = skor_ke_persentase_sisa(nasi_val)
                ps = skor_ke_persentase_sisa(sayur_val)
                pl = skor_ke_persentase_sisa(lauk_val)
                bsn = ba_nasi * pn
                bss = ba_sayur * ps
                bsl = ba_lauk * pl
                total_sisa = bsn + bss + bsl
                el = hitung_economic_loss(total_awal, total_sisa, harga_upload)
                
                id_siswa_unik = f"{timestamp_id}-{i+1:02d}"
                link_foto = ""
                
                row = {
                    "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Tanggal": str(tanggal_upload),
                    "Hari Ke-": hari_ke,
                    "Kode Sekolah": user['kode_sekolah'],
                    "Nama Sekolah": SEKOLAH_LIST[user['kode_sekolah']],
                    "Nama Enumerator": user['nama'],
                    "Email Enumerator": user.get('email', '-'),
                    "ID Siswa": id_siswa_unik,
                    "Nama Foto": foto.name,
                    "Kelas": "-",
                    "Skor Visual Nasi": nasi_val, "Berat Awal Nasi (g)": ba_nasi,
                    "Berat Sisa Nasi (g)": round(bsn,1), "% Sisa Nasi": round(pn,4),
                    "Skor Visual Sayur": sayur_val, "Berat Awal Sayur (g)": ba_sayur,
                    "Berat Sisa Sayur (g)": round(bss,1), "% Sisa Sayur": round(ps,4),
                    "Skor Visual Lauk": lauk_val, "Berat Awal Lauk (g)": ba_lauk,
                    "Berat Sisa Lauk (g)": round(bsl,1), "% Sisa Lauk": round(pl,4),
                    "Total Awal (g)": total_awal, "Total Sisa (g)": round(total_sisa,1),
                    "Harga Satuan (Rp)": harga_upload,
                    "Economic Loss (Rp)": round(el,0),
                    "Keterangan": ket_val,
                    "Link Foto Sebelum": "",
                    "Link Foto Sesudah": link_foto,
                }
                
                # 3. Simpan ke Sheets
                try:
                    simpan_data(row)
                    sukses += 1
                    st.session_state.processed_files.add(foto.name)
                    log_area.success(f"✅ Foto {i+1} ({foto.name}) — tersimpan!")
                except Exception as e:
                    gagal += 1
                    error_detail.append(f"Foto {i+1} ({foto.name}): {type(e).__name__}: {str(e)[:100]}")
                    gagal_di = i + 1
                    log_area.error(f"❌ Foto {i+1} ({foto.name}) GAGAL: {str(e)[:80]}")
                    st.error(f"🛑 Proses berhenti di foto ke-{i+1}. Perbaiki masalah, lalu upload ulang dari foto ini.")
                    break
                
                progress_bar.progress((i + 1) / len(foto_baru))
                
                if i < len(foto_baru) - 1:
                    time.sleep(1)
            
            # Ringkasan
            if gagal_di is None:
                status_text.success(f"✅ Semua selesai! {sukses} sukses, {gagal_ai} AI tidak tersedia")
            else:
                status_text.warning(f"⚠️ Berhenti di foto ke-{gagal_di}. {sukses} tersimpan sebelum gagal.")
            
            if error_detail:
                with st.expander(f"❌ Detail Error ({len(error_detail)})", expanded=True):
                    for err in error_detail:
                        st.error(err)
            
            if gagal_ai > 0:
                st.warning(f"⚠️ **{gagal_ai} foto gagal dianalisa AI** (skor 0, tapi tetap tersimpan).")
            
            # Clear kalau semua sukses
            if gagal == 0:
                st.session_state.uploader_version += 1
                st.session_state.processed_files = set()
                time.sleep(3)
                st.rerun()
            else:
                if st.button("🔄 Coba Lagi dari Foto yang Gagal", key="btn_retry"):
                    st.session_state.uploader_version += 1
                    time.sleep(1)
                    st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== HALAMAN DASHBOARD ====================
elif st.session_state.halaman == "dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Dashboard Rekap</div>', unsafe_allow_html=True)
    try:
        data = ambil_semua_data()
        if not data:
            st.info("Belum ada data.")
        else:
            df = pd.DataFrame(data)
            df = df[df["Kode Sekolah"] == user['kode_sekolah']]
            
            if len(df) == 0:
                st.info("Belum ada data untuk sekolah Anda.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    tgl_list = ["Semua"] + sorted(df["Tanggal"].astype(str).unique(), reverse=True)
                    filter_tgl = st.selectbox("Filter Tanggal", tgl_list, key="filter_tanggal")
                if filter_tgl != "Semua":
                    df = df[df["Tanggal"].astype(str) == filter_tgl]
                
                total = len(df)
                avg_n = df["% Sisa Nasi"].astype(float).mean() * 100 if total > 0 else 0
                avg_s = df["% Sisa Sayur"].astype(float).mean() * 100 if total > 0 else 0
                avg_l = df["% Sisa Lauk"].astype(float).mean() * 100 if total > 0 else 0
                loss = df["Economic Loss (Rp)"].astype(float).sum() if total > 0 else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Foto</div></div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="metric-card-red"><div class="metric-value">Rp {loss:,.0f}</div><div class="metric-label">Economic Loss</div></div>', unsafe_allow_html=True)
                
                st.markdown("**Rata-rata % Sisa per Komponen**")
                c1, c2, c3 = st.columns(3)
                c1.metric("🍚 Nasi", f"{avg_n:.1f}%")
                c2.metric("🥬 Sayur", f"{avg_s:.1f}%")
                c3.metric("🍗 Lauk", f"{avg_l:.1f}%")
                
                st.markdown("**Distribusi Skor Comstock**")
                chart = pd.DataFrame({
                    "Nasi": df["Skor Visual Nasi"].astype(int).value_counts().sort_index(),
                    "Sayur": df["Skor Visual Sayur"].astype(int).value_counts().sort_index(),
                    "Lauk": df["Skor Visual Lauk"].astype(int).value_counts().sort_index(),
                }).fillna(0)
                st.bar_chart(chart)
                
                st.markdown("**Data Detail**")
                st.dataframe(df, use_container_width=True)
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", csv, f"comstock_{user['kode_sekolah']}_{filter_tgl}.csv", "text/csv")
    except Exception as e:
        st.error(f"Error: {e}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    if st.button("⬅️ Kembali ke Upload", key="btn_kembali"):
        st.session_state.halaman = "upload"
        st.rerun()
