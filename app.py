"""Comstock Digital MBG - Aplikasi Utama."""
import streamlit as st
import pandas as pd
from datetime import datetime

from comstock_utils import (
    skor_ke_persentase_sisa, hitung_economic_loss,
    COMSTOCK_MAPPING, KETERANGAN_SKOR, SEKOLAH_LIST
)
from gsheet_helper import simpan_data, ambil_semua_data
from gdrive_helper import upload_foto
from ai_scorer import prediksi_skor_dari_foto
from auth import cek_login, login_google, logout


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
        font-family: 'Poppins', sans-serif; 
        color: #1a1a1a;
    }
    
    .stApp { 
        background: #f6e3b4; 
        color: #1a1a1a;
    }
    
    /* SEMUA TEXT HITAM */
    .stApp p, .stApp span, .stApp div, .stApp label,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
        color: #1a1a1a;
    }
    
    /* HEADER */
    .main-header {
        background: linear-gradient(135deg, #efd48a 0%, #f6e3b4 100%);
        border: 2px solid #c99a3a;
        border-radius: 20px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(138, 90, 43, 0.15);
    }
    .main-header h1 { 
        color: #1a1a1a !important; 
        font-size: 1.8rem; 
        font-weight: 800; 
        margin: 0; 
    }
    .main-header p { 
        color: #1a1a1a !important; 
        font-size: 0.85rem; 
        margin: 0.5rem 0 0 0; 
        letter-spacing: 2px; 
        text-transform: uppercase; 
        font-weight: 600; 
    }
    
    /* CARD */
    .card { 
        background: #ffffff; 
        border: 2px solid #c99a3a; 
        border-radius: 16px; 
        padding: 1.5rem; 
        margin-bottom: 1rem; 
        box-shadow: 0 4px 12px rgba(138, 90, 43, 0.08); 
    }
    .card * {
        color: #1a1a1a;
    }
    .section-title { 
        color: #1a1a1a !important; 
        font-size: 1.1rem; 
        font-weight: 700; 
        margin-bottom: 1rem; 
        padding-bottom: 0.5rem; 
        border-bottom: 3px solid #c99a3a; 
        display: inline-block; 
    }
    
    /* METRIC */
    .metric-card { 
        background: linear-gradient(135deg, #c99a3a 0%, #8a5a2b 100%); 
        border-radius: 14px; 
        padding: 1.1rem; 
        text-align: center; 
        margin: 0.3rem 0; 
    }
    .metric-value { 
        font-size: 1.6rem; 
        font-weight: 800; 
        color: #ffffff !important;
    }
    .metric-label { 
        font-size: 0.72rem; 
        letter-spacing: 1px; 
        text-transform: uppercase; 
        margin-top: 0.3rem; 
        color: #ffffff !important;
    }
    .metric-card-red { 
        background: linear-gradient(135deg, #c0392b 0%, #8a1a10 100%); 
        border-radius: 14px; 
        padding: 1.1rem; 
        text-align: center; 
        margin: 0.3rem 0; 
    }
    
    /* BUTTON */
    .stButton > button { 
        background: #c99a3a !important; 
        color: #ffffff !important; 
        border: none !important; 
        border-radius: 22px !important; 
        padding: 0.8rem 1.5rem !important; 
        font-weight: 600 !important; 
        width: 100% !important; 
    }
    .stButton > button:hover { 
        background: #8a5a2b !important; 
    }
    
    /* SEMUA INPUT - HITAM BG, PUTIH TEXT */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stDateInput > div > div > input { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
        border: 2px solid #1a1a1a !important; 
        border-radius: 10px !important; 
    }
    .stTextInput > div > div > input::placeholder,
    .stNumberInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #888888 !important;
    }
    
    /* SELECTBOX */
    .stSelectbox > div > div,
    .stSelectbox [data-baseweb="select"] > div { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
        border: 2px solid #1a1a1a !important; 
        border-radius: 10px !important; 
    }
    .stSelectbox [data-baseweb="select"] svg { 
        fill: #ffffff !important; 
    }
    [role="listbox"] { 
        background-color: #1a1a1a !important; 
    }
    [role="option"] { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
    }
    [role="option"]:hover { 
        background-color: #c99a3a !important; 
        color: #1a1a1a !important; 
    }
    [aria-selected="true"] { 
        background-color: #c99a3a !important; 
        color: #1a1a1a !important; 
    }
    
    /* LABELS HITAM */
    .stTextInput label, 
    .stNumberInput label, 
    .stSelectbox label, 
    .stTextArea label, 
    .stFileUploader label, 
    .stDateInput label { 
        color: #1a1a1a !important; 
        font-weight: 600 !important; 
    }
    
    /* CAPTION HITAM */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: #1a1a1a !important;
        font-weight: 500 !important;
    }
    
    /* MARKDOWN HITAM */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div {
        color: #1a1a1a !important;
    }
    
    /* FILE UPLOADER */
    .stFileUploader > div > div { 
        border: 2px dashed #c99a3a !important; 
        border-radius: 12px !important; 
        background: #f6e3b4 !important; 
    }
    .stFileUploader > div > div > div,
    .stFileUploader > div > div > div > div,
    .stFileUploader > div > div > small {
        color: #1a1a1a !important;
    }
    .stFileUploader button {
        background-color: #c99a3a !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* ALERT - teks hitam */
    .stAlert, .stAlert * {
        color: #1a1a1a !important;
    }
    .stAlert {
        border-radius: 12px !important;
    }
    
    /* EXPANDER */
    .streamlit-expanderHeader, 
    .streamlit-expanderHeader *,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary * {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] {
        border: 2px solid #c99a3a !important;
        border-radius: 12px !important;
        background: #ffffff !important;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] { 
        background: #efd48a; 
        border-right: 2px solid #c99a3a; 
    }
    section[data-testid="stSidebar"] * { 
        color: #1a1a1a !important; 
    }
    section[data-testid="stSidebar"] .stButton > button { 
        background: #ffffff !important; 
        color: #1a1a1a !important; 
        border: 2px solid #8a5a2b !important; 
        border-radius: 12px; 
        margin-bottom: 0.5rem; 
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #8a5a2b !important;
        color: #ffffff !important;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div { 
        background: #c99a3a !important; 
    }
    
    /* METRIC NATIVE */
    [data-testid="stMetricValue"] {
        color: #1a1a1a !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #1a1a1a !important;
        font-weight: 600 !important;
    }
    
    /* DATAFRAME */
    .stDataFrame, .stDataFrame * {
        color: #1a1a1a;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    @media (max-width: 768px) { 
        .main-header h1 { font-size: 1.3rem; } 
        .card { padding: 1rem; } 
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "halaman" not in st.session_state: st.session_state.halaman = "upload"
if "user" not in st.session_state: st.session_state.user = None

# Cek login
user = cek_login()
if not user:
    st.markdown("""
    <div class="main-header">
        <h1>🌿 COMSTOCK DIGITAL</h1>
        <p>Makanan Bergizi Gratis</p>
    </div>
    """, unsafe_allow_html=True)
    login_google()
    st.stop()

# Sidebar
with st.sidebar:
    st.markdown(f"### 👋 Halo, {user['nama']}")
    st.caption(f"🏫 {SEKOLAH_LIST.get(user['kode_sekolah'], user['kode_sekolah'])}")
    st.markdown("---")
    if st.button("📸 Upload Foto"): st.session_state.halaman = "upload"; st.rerun()
    if st.button("📊 Dashboard"): st.session_state.halaman = "dashboard"; st.rerun()
    st.markdown("---")
    if st.button("🚪 Logout"): logout()

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
    st.caption("Upload foto sisa makanan. AI akan menganalisa otomatis. Tinggal koreksi dan simpan.")
    
    # Setup minimal
    col1, col2 = st.columns(2)
    with col1:
        tanggal_upload = st.date_input("Tanggal", datetime.now(), key="upload_tanggal")
    with col2:
        harga_upload = st.number_input("Harga Porsi (Rp)", 0.0, 100000.0, 15000.0, key="upload_harga")
    
    # Berat awal default
    with st.expander("⚖️ Berat Awal Referensi (klik untuk ubah)"):
        col1, col2, col3 = st.columns(3)
        with col1: ba_nasi = st.number_input("Nasi (g)", 0.0, 500.0, 136.0, key="ba_nasi")
        with col2: ba_sayur = st.number_input("Sayur (g)", 0.0, 500.0, 29.0, key="ba_sayur")
        with col3: ba_lauk = st.number_input("Lauk (g)", 0.0, 500.0, 64.0, key="ba_lauk")
    
    st.markdown("---")
    st.markdown("**📷 Upload Foto Sisa (bisa banyak sekaligus)**")
    st.caption("Tips: Klik 'Browse files', lalu Ctrl + Klik beberapa foto, atau drag & drop dari File Explorer.")
    
    foto_list = st.file_uploader(
        "Pilih foto sisa makanan",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True,
        key="upload_fotos",
        label_visibility="collapsed"
    )
    
    if foto_list:
        st.success(f"✅ {len(foto_list)} foto terpilih")
        
        # Preview grid
        cols = st.columns(min(len(foto_list), 4))
        for i, f in enumerate(foto_list):
            with cols[i % 4]:
                st.image(f, caption=f.name[:12], use_container_width=True)
        
        st.markdown("---")
        
        # Tombol proses AI
        if st.button("🚀 Proses Semua Foto dengan AI"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            hasil = []
            
            for idx, foto in enumerate(foto_list):
                status_text.info(f"⏳ Menganalisa foto {idx+1}/{len(foto_list)}: {foto.name}")
                
                try:
                    skor_ai = prediksi_skor_dari_foto(foto.getvalue())
                    
                    if skor_ai:
                        hasil.append({
                            "idx": idx,
                            "file": foto,
                            "nama": foto.name,
                            "nasi": int(skor_ai.get("nasi", 0)),
                            "sayur": int(skor_ai.get("sayur", 0)),
                            "lauk": int(skor_ai.get("lauk", 0)),
                            "alasan": skor_ai.get("alasan", ""),
                            "error": None
                        })
                    else:
                        hasil.append({
                            "idx": idx,
                            "file": foto,
                            "nama": foto.name,
                            "nasi": 0, "sayur": 0, "lauk": 0,
                            "alasan": "AI tidak tersedia",
                            "error": None
                        })
                except Exception as e:
                    hasil.append({
                        "idx": idx,
                        "file": foto,
                        "nama": foto.name,
                        "nasi": 0, "sayur": 0, "lauk": 0,
                        "alasan": "",
                        "error": str(e)
                    })
                
                progress_bar.progress((idx + 1) / len(foto_list))
            
            status_text.success(f"✅ Analisa selesai! Silakan koreksi di bawah.")
            st.session_state["hasil_upload"] = hasil
            st.rerun()
    
    # Tampilkan hasil analisa
    if "hasil_upload" in st.session_state and st.session_state["hasil_upload"]:
        hasil = st.session_state["hasil_upload"]
        
        st.markdown("---")
        st.markdown("### ✏️ Koreksi Skor (kalau AI salah)")
        st.caption("Ubah skor di dropdown kalau AI salah. Kalau sudah benar, langsung klik Simpan Semua.")
        
        # Tampilkan tiap foto dengan dropdown
        for i, h in enumerate(hasil):
            with st.expander(f"📷 {h['nama']} — Nasi:{h['nasi']} Sayur:{h['sayur']} Lauk:{h['lauk']}", expanded=False):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(h['file'], use_container_width=True)
                with col2:
                    st.caption(f"💬 {h['alasan']}")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        new_nasi = st.selectbox("🍚 Nasi", [0,1,2,3,4,5], index=h['nasi'], key=f"nasi_{i}")
                    with c2:
                        new_sayur = st.selectbox("🥬 Sayur", [0,1,2,3,4,5], index=h['sayur'], key=f"sayur_{i}")
                    with c3:
                        new_lauk = st.selectbox("🍗 Lauk", [0,1,2,3,4,5], index=h['lauk'], key=f"lauk_{i}")
                    
                    st.session_state["hasil_upload"][i]['nasi'] = new_nasi
                    st.session_state["hasil_upload"][i]['sayur'] = new_sayur
                    st.session_state["hasil_upload"][i]['lauk'] = new_lauk
        
        st.markdown("---")
        
        # Tombol simpan semua
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Simpan Semua"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                sukses = 0
                gagal = 0
                
                for i, h in enumerate(st.session_state["hasil_upload"]):
                    status_text.info(f"⏳ Menyimpan {i+1}/{len(st.session_state['hasil_upload'])}: {h['nama']}")
                    
                    try:
                        # Upload foto ke Drive
                        filename = f"{user['kode_sekolah']}_{tanggal_upload}_{i+1:03d}_{h['nama']}"
                        link_foto = upload_foto(
                            h['file'].getvalue(),
                            filename,
                            subfolder=f"{user['kode_sekolah']}/{tanggal_upload}"
                        )
                        
                        # Hitung
                        total_awal = ba_nasi + ba_sayur + ba_lauk
                        pn = skor_ke_persentase_sisa(h['nasi'])
                        ps = skor_ke_persentase_sisa(h['sayur'])
                        pl = skor_ke_persentase_sisa(h['lauk'])
                        bsn = ba_nasi * pn
                        bss = ba_sayur * ps
                        bsl = ba_lauk * pl
                        total_sisa = bsn + bss + bsl
                        el = hitung_economic_loss(total_awal, total_sisa, harga_upload)
                        
                        row = {
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Tanggal": str(tanggal_upload),
                            "Hari Ke-": 0,
                            "Kode Sekolah": user['kode_sekolah'],
                            "Nama Sekolah": SEKOLAH_LIST[user['kode_sekolah']],
                            "Nama Enumerator": user['nama'],
                            "Email Enumerator": user.get('email', '-'),
                            "ID Siswa": str(i + 1),
                            "Kelas": "-",
                            "Skor Visual Nasi": h['nasi'], "Berat Awal Nasi (g)": ba_nasi,
                            "Berat Sisa Nasi (g)": round(bsn,1), "% Sisa Nasi": round(pn,4),
                            "Skor Visual Sayur": h['sayur'], "Berat Awal Sayur (g)": ba_sayur,
                            "Berat Sisa Sayur (g)": round(bss,1), "% Sisa Sayur": round(ps,4),
                            "Skor Visual Lauk": h['lauk'], "Berat Awal Lauk (g)": ba_lauk,
                            "Berat Sisa Lauk (g)": round(bsl,1), "% Sisa Lauk": round(pl,4),
                            "Total Awal (g)": total_awal, "Total Sisa (g)": round(total_sisa,1),
                            "Harga Satuan (Rp)": harga_upload,
                            "Economic Loss (Rp)": round(el,0),
                            "Keterangan": h['alasan'],
                            "Link Foto Sebelum": "",
                            "Link Foto Sesudah": link_foto,
                        }
                        simpan_data(row)
                        sukses += 1
                    except Exception as e:
                        gagal += 1
                    
                    progress_bar.progress((i + 1) / len(st.session_state["hasil_upload"]))
                
                status_text.success(f"✅ Selesai! {sukses} sukses, {gagal} gagal.")
                st.balloons()
                
                del st.session_state["hasil_upload"]
                
                if st.button("🔄 Upload Lagi"):
                    st.rerun()
        
        with col2:
            if st.button("🗑️ Batal"):
                del st.session_state["hasil_upload"]
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
                    filter_tgl = st.selectbox("Filter Tanggal", tgl_list)
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
    if st.button("⬅️ Kembali ke Upload"):
        st.session_state.halaman = "upload"
        st.rerun()
