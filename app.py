"""Comstock Digital MBG - Aplikasi Utama."""
import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
from io import BytesIO

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
    
    :root {
        --cream: #f6e3b4;
        --cream-dark: #efd48a;
        --brown: #8a5a2b;
        --brown-dark: #5c3a1a;
        --gold: #c99a3a;
        --white: #ffffff;
        --black: #1a1a1a;
        --text: #1a1a1a;
        --muted: #6c5a3e;
    }
    
    html, body, [class*="css"] { 
        font-family: 'Poppins', sans-serif; 
        color: var(--black);
    }
    
    /* Background cream */
    .stApp { 
        background: var(--cream); 
    }
    
    /* Header - judul HITAM */
    .main-header {
        background: linear-gradient(135deg, var(--cream-dark) 0%, var(--cream) 100%);
        border: 2px solid var(--gold);
        border-radius: 20px;
        padding: 1.8rem 1.5rem;
        text-align: center;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 18px rgba(138, 90, 43, 0.15);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: "🌿";
        position: absolute;
        top: -10px;
        right: 10px;
        font-size: 60px;
        opacity: 0.25;
    }
    
    .main-header h1 { 
        color: var(--black) !important; 
        font-size: 1.8rem; 
        font-weight: 800; 
        margin: 0; 
        letter-spacing: 1px;
    }
    
    .main-header p { 
        color: var(--brown-dark) !important; 
        font-size: 0.85rem; 
        margin: 0.5rem 0 0 0; 
        letter-spacing: 2px;
        text-transform: uppercase;
        font-weight: 600;
    }
    
    /* Card putih dengan border gold */
    .card {
        background: var(--white);
        border: 2px solid var(--gold);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 12px rgba(138, 90, 43, 0.08);
    }
    
    .section-title {
        color: var(--black) !important;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid var(--gold);
        display: inline-block;
        letter-spacing: 0.5px;
    }
    
    /* Metric card - gold gradient */
    .metric-card {
        background: linear-gradient(135deg, var(--gold) 0%, var(--brown) 100%);
        border-radius: 14px;
        padding: 1.1rem;
        color: var(--white);
        text-align: center;
        margin: 0.3rem 0;
        box-shadow: 0 4px 12px rgba(201, 154, 58, 0.3);
    }
    
    .metric-value { 
        font-size: 1.6rem; 
        font-weight: 800; 
        letter-spacing: 0.5px;
    }
    
    .metric-label { 
        font-size: 0.72rem; 
        opacity: 0.95; 
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 0.3rem;
    }
    
    /* Metric card merah - untuk economic loss */
    .metric-card-red {
        background: linear-gradient(135deg, #c0392b 0%, #8a1a10 100%);
        border-radius: 14px;
        padding: 1.1rem;
        color: var(--white);
        text-align: center;
        margin: 0.3rem 0;
        box-shadow: 0 4px 12px rgba(192, 57, 43, 0.3);
    }
    
    /* Tombol gold - style Warner */
    .stButton > button {
        background: var(--gold) !important;
        color: var(--white) !important;
        border: none !important;
        border-radius: 22px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        width: 100% !important;
        letter-spacing: 0.5px;
        transition: all 0.25s;
        box-shadow: 0 4px 10px rgba(201, 154, 58, 0.25);
    }
    
    .stButton > button:hover { 
        background: var(--brown) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(138, 90, 43, 0.4);
    }
    
    /* ============================================
       INPUT FIELDS - SEMUA HITAM SOLID
       ============================================ */
    
    /* Text Input, Number Input */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: var(--black) !important;
        color: var(--white) !important;
        border: 2px solid var(--black) !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.8rem !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--gold) !important;
        box-shadow: 0 0 0 3px rgba(201, 154, 58, 0.25) !important;
        background-color: var(--black) !important;
        color: var(--white) !important;
    }
    
    /* Placeholder text */
    .stTextInput > div > div > input::placeholder,
    .stNumberInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: #888888 !important;
    }
    
    /* Selectbox - main container */
    .stSelectbox > div > div {
        background-color: var(--black) !important;
        border: 2px solid var(--black) !important;
        border-radius: 10px !important;
        color: var(--white) !important;
    }
    
    .stSelectbox > div > div > div {
        background-color: var(--black) !important;
        color: var(--white) !important;
    }
    
    /* Selectbox - selected value text */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: var(--black) !important;
        color: var(--white) !important;
        border: 2px solid var(--black) !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: var(--gold) !important;
    }
    
    .stSelectbox [data-baseweb="select"] svg {
        fill: var(--white) !important;
        color: var(--white) !important;
    }
    
    /* Selectbox - dropdown menu (popover) */
    [data-baseweb="popover"] {
        background-color: var(--black) !important;
    }
    
    [data-baseweb="popover"] > div {
        background-color: var(--black) !important;
    }
    
    [role="listbox"] {
        background-color: var(--black) !important;
    }
    
    [role="option"] {
        background-color: var(--black) !important;
        color: var(--white) !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    [role="option"]:hover {
        background-color: var(--gold) !important;
        color: var(--black) !important;
    }
    
    [aria-selected="true"] {
        background-color: var(--gold) !important;
        color: var(--black) !important;
    }
    
    /* Date input */
    .stDateInput > div > div > input {
        background-color: var(--black) !important;
        color: var(--white) !important;
        border: 2px solid var(--black) !important;
        border-radius: 10px !important;
    }
    
    /* Number input - stepper buttons */
    .stNumberInput > div > div > button {
        background-color: var(--gold) !important;
        color: var(--white) !important;
        border: none !important;
    }
    
    .stNumberInput > div > div > button:hover {
        background-color: var(--brown) !important;
    }
    
    /* ============================================
       LABELS - SEMUA HITAM
       ============================================ */
    .stTextInput label, 
    .stNumberInput label, 
    .stSelectbox label, 
    .stTextArea label,
    .stFileUploader label,
    .stDateInput label {
        color: var(--black) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }
    
    /* Markdown text */
    .stMarkdown p, .stMarkdown span, .stMarkdown div {
        color: var(--black);
    }
    
    /* File uploader */
    .stFileUploader > div > div {
        border: 2px dashed var(--gold) !important;
        border-radius: 12px !important;
        background: var(--cream) !important;
    }
    
    .stFileUploader > div > div > div {
        color: var(--black) !important;
    }
    
    .stFileUploader button {
        background-color: var(--gold) !important;
        color: var(--white) !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    /* ============================================
       SIDEBAR
       ============================================ */
    section[data-testid="stSidebar"] {
        background: var(--cream-dark);
        border-right: 2px solid var(--gold);
    }
    
    section[data-testid="stSidebar"] * {
        color: var(--black);
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: var(--white) !important;
        color: var(--black) !important;
        border: 2px solid var(--brown) !important;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        font-weight: 600 !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--brown) !important;
        color: var(--white) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: var(--gold) !important;
    }
    
    /* Metric (native streamlit) */
    [data-testid="stMetricValue"] {
        color: var(--black) !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-weight: 600 !important;
    }
    
    /* Info/Success/Error box */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid var(--gold) !important;
        color: var(--black) !important;
    }
    
    .stAlert p {
        color: var(--black) !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        border-radius: 12px !important;
        overflow: hidden !important;
    }
    
    /* Caption text */
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--brown-dark) !important;
        font-weight: 500 !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* Scrollbar custom */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--cream);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--gold);
        border-radius: 4px;
    }
    
    @media (max-width: 768px) {
        .main-header h1 { font-size: 1.3rem; }
        .main-header { padding: 1.2rem 1rem; }
        .card { padding: 1rem; }
        .metric-value { font-size: 1.3rem; }
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "halaman" not in st.session_state: st.session_state.halaman = "input"
if "batch_data" not in st.session_state: st.session_state.batch_data = []
if "setup_batch" not in st.session_state: st.session_state.setup_batch = {}
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
    if st.button("📝 Input Data"): st.session_state.halaman = "input"; st.rerun()
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

# ==================== HALAMAN INPUT ====================
if st.session_state.halaman == "input":
    if not st.session_state.setup_batch:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚙️ Setup Sesi Input</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            tanggal = st.date_input("Tanggal", datetime.now())
            jumlah_siswa = st.number_input("Jumlah Siswa Hari Ini", 1, 200, 70)
        with col2:
            hari_ke = st.number_input("Hari Ke-", 1, 30, 1)
            harga_porsi = st.number_input("Harga Satuan Porsi (Rp)", 0.0, 100000.0, 15000.0)
        
        st.markdown("**⚖️ Berat Awal Referensi Hari Ini (gram)** — harus diisi, beda tiap hari")
        col1, col2, col3 = st.columns(3)
        with col1: ba_nasi = st.number_input("Nasi (g)", 0.0, 500.0, 136.0)
        with col2: ba_sayur = st.number_input("Sayur (g)", 0.0, 500.0, 29.0)
        with col3: ba_lauk = st.number_input("Lauk (g)", 0.0, 500.0, 64.0)
        
        if st.button("🚀 Mulai Sesi Input"):
            st.session_state.setup_batch = {
                "tanggal": str(tanggal),
                "hari_ke": hari_ke,
                "jumlah_siswa": jumlah_siswa,
                "ba_nasi": ba_nasi, "ba_sayur": ba_sayur, "ba_lauk": ba_lauk,
                "harga_porsi": harga_porsi,
            }
            st.session_state.batch_data = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        setup = st.session_state.setup_batch
        sudah = len(st.session_state.batch_data)
        target = setup["jumlah_siswa"]
        
        st.markdown(f"""
        <div class="card">
            <div class="section-title">📍 {SEKOLAH_LIST[user['kode_sekolah']]} — {setup['tanggal']}</div>
            <p style="color: var(--black); font-weight: 600;">Progress: <b style="color: var(--brown-dark);">{sudah}/{target}</b> siswa</p>
        </div>
        """, unsafe_allow_html=True)
        st.progress(sudah / target if target > 0 else 0)
        
        if sudah < target:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown(f'<div class="section-title">👤 Siswa #{sudah + 1}</div>', unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                id_siswa = st.text_input("ID Siswa", key=f"id_{sudah}", placeholder="001")
            with col2:
                kelas = st.selectbox("Kelas", ["Tinggi (4-6)", "Rendah (1-3)"], key=f"kls_{sudah}")
            
            if sudah == 0:
                st.markdown("**📷 Foto Sebelum Makan (referensi porsi hari ini)**")
                foto_sebelum = st.file_uploader("Upload foto porsi awal", type=["jpg","jpeg","png"], key="foto_sebelum")
                if foto_sebelum: st.image(foto_sebelum, caption="Porsi Awal", use_container_width=True)
            else:
                foto_sebelum = None
            
            st.markdown("**📷 Foto Sisa Makanan Siswa Ini**")
            foto_sisa = st.file_uploader("Upload foto sisa", type=["jpg","jpeg","png"], key=f"fs_{sudah}")
            
            skor_ai = None
            if foto_sisa:
                st.image(foto_sisa, caption="Sisa Makanan", use_container_width=True)
                with st.spinner("🤖 AI menganalisis..."):
                    skor_ai = prediksi_skor_dari_foto(foto_sisa.getvalue())
                if skor_ai:
                    st.success(f"🤖 Saran AI: Nasi={skor_ai.get('nasi',0)}, Sayur={skor_ai.get('sayur',0)}, Lauk={skor_ai.get('lauk',0)}")
                else:
                    st.info("ℹ️ Mode manual aktif (AI akan aktif setelah model siap).")
            
            st.markdown("**🎯 Skor Comstock (0-5)**")
            col1, col2, col3 = st.columns(3)
            with col1:
                sn = st.selectbox("Nasi", [0,1,2,3,4,5], index=(skor_ai or {}).get('nasi', 0), key=f"sn_{sudah}")
                st.caption(KETERANGAN_SKOR[sn])
            with col2:
                ss = st.selectbox("Sayur", [0,1,2,3,4,5], index=(skor_ai or {}).get('sayur', 0), key=f"ss_{sudah}")
                st.caption(KETERANGAN_SKOR[ss])
            with col3:
                sl = st.selectbox("Lauk", [0,1,2,3,4,5], index=(skor_ai or {}).get('lauk', 0), key=f"sl_{sudah}")
                st.caption(KETERANGAN_SKOR[sl])
            
            keterangan = st.text_input("Keterangan (opsional)", key=f"ket_{sudah}")
            
            if st.button("💾 Simpan & Lanjut"):
                if not id_siswa:
                    st.error("ID Siswa wajib diisi!")
                elif not foto_sisa:
                    st.error("Foto sisa wajib diupload!")
                else:
                    with st.spinner("Menyimpan ke Google Sheets..."):
                        try:
                            link_sisa = upload_foto(
                                foto_sisa.getvalue(),
                                f"{user['kode_sekolah']}_{setup['tanggal']}_{id_siswa}_sisa.jpg",
                                subfolder=f"{user['kode_sekolah']}/{setup['tanggal']}"
                            )
                            link_sebelum = ""
                            if foto_sebelum:
                                link_sebelum = upload_foto(
                                    foto_sebelum.getvalue(),
                                    f"{user['kode_sekolah']}_{setup['tanggal']}_referensi.jpg",
                                    subfolder=f"{user['kode_sekolah']}/{setup['tanggal']}"
                                )
                            
                            total_awal = setup['ba_nasi'] + setup['ba_sayur'] + setup['ba_lauk']
                            pn = skor_ke_persentase_sisa(sn)
                            ps = skor_ke_persentase_sisa(ss)
                            pl = skor_ke_persentase_sisa(sl)
                            bsn = setup['ba_nasi'] * pn
                            bss = setup['ba_sayur'] * ps
                            bsl = setup['ba_lauk'] * pl
                            total_sisa = bsn + bss + bsl
                            el = hitung_economic_loss(total_awal, total_sisa, setup['harga_porsi'])
                            
                            row = {
                                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "Tanggal": setup['tanggal'],
                                "Hari Ke-": setup['hari_ke'],
                                "Kode Sekolah": user['kode_sekolah'],
                                "Nama Sekolah": SEKOLAH_LIST[user['kode_sekolah']],
                                "Nama Enumerator": user['nama'],
                                "Email Enumerator": user.get('email', '-'),
                                "ID Siswa": id_siswa,
                                "Kelas": kelas,
                                "Skor Visual Nasi": sn, "Berat Awal Nasi (g)": setup['ba_nasi'],
                                "Berat Sisa Nasi (g)": round(bsn,1), "% Sisa Nasi": round(pn,4),
                                "Skor Visual Sayur": ss, "Berat Awal Sayur (g)": setup['ba_sayur'],
                                "Berat Sisa Sayur (g)": round(bss,1), "% Sisa Sayur": round(ps,4),
                                "Skor Visual Lauk": sl, "Berat Awal Lauk (g)": setup['ba_lauk'],
                                "Berat Sisa Lauk (g)": round(bsl,1), "% Sisa Lauk": round(pl,4),
                                "Total Awal (g)": total_awal, "Total Sisa (g)": round(total_sisa,1),
                                "Harga Satuan (Rp)": setup['harga_porsi'],
                                "Economic Loss (Rp)": round(el,0),
                                "Keterangan": keterangan,
                                "Link Foto Sebelum": link_sebelum,
                                "Link Foto Sesudah": link_sisa,
                            }
                            simpan_data(row)
                            st.session_state.batch_data.append(row)
                            st.success(f"✅ Siswa {id_siswa} tersimpan!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Gagal: {e}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"🎉 Selesai! {target} siswa sudah diinput.")
            if st.button("📊 Lihat Dashboard"): st.session_state.halaman = "dashboard"; st.rerun()
            if st.button("🔄 Sesi Baru"): st.session_state.setup_batch = {}; st.session_state.batch_data = []; st.rerun()

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
                    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Siswa</div></div>', unsafe_allow_html=True)
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