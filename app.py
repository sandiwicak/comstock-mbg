"""Comstock Digital MBG - Aplikasi Utama (tanpa login, tanpa foto sebelum)."""
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
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea { 
        background-color: #1a1a1a !important; 
        color: #ffffff !important; 
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #1a1a1a !important; 
        border-radius: 10px !important; 
    }
    .stTextInput > div > div > input::placeholder,
    .stNumberInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder { color: #888888 !important; -webkit-text-fill-color: #888888 !important; }
    
    .stDateInput > div > div > input {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border: 2px solid #1a1a1a !important;
        border-radius: 10px !important;
    }
    
    .stSelectbox > div > div { background-color: #1a1a1a !important; border: 2px solid #1a1a1a !important; border-radius: 10px !important; color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] > div { background-color: #1a1a1a !important; color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] span { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    .stSelectbox [data-baseweb="select"] svg { fill: #ffffff !important; }
    [role="listbox"] { background-color: #1a1a1a !important; }
    [role="option"] { background-color: #1a1a1a !important; color: #ffffff !important; }
    [role="option"]:hover { background-color: #c99a3a !important; color: #1a1a1a !important; }
    [aria-selected="true"] { background-color: #c99a3a !important; color: #1a1a1a !important; }
    
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label, .stFileUploader label, .stDateInput label { color: #1a1a1a !important; font-weight: 600 !important; }
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * { color: #5c3a1a !important; font-weight: 500 !important; }
    .stMarkdown p, .stMarkdown li, .stMarkdown span { color: #1a1a1a; }
    
    .stFileUploader > div > div { border: 2px dashed #c99a3a !important; border-radius: 12px !important; background: #f6e3b4 !important; }
    .stFileUploader > div > div > div { color: #1a1a1a !important; }
    .stFileUploader button { background-color: #c99a3a !important; color: white !important; border-radius: 10px !important; border: none !important; }
    
    [data-testid="stFileUploaderFile"], [data-testid="stUploadedFile"], [data-testid="stFileUploaderFileName"] { background-color: #1a1a1a !important; }
    [data-testid="stFileUploaderFile"] *, [data-testid="stUploadedFile"] *, [data-testid="stFileUploaderFileName"] * { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
    [data-testid="stFileUploaderDeleteBtn"] svg { fill: #ffffff !important; }
    
    .stAlert { border-radius: 12px !important; }
    .stAlert p { color: #1a1a1a !important; }
    
    section[data-testid="stSidebar"] { background: #efd48a; border-right: 2px solid #c99a3a; }
    section[data-testid="stSidebar"] * { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] .stButton > button { background: white !important; color: #1a1a1a !important; border: 2px solid #8a5a2b !important; border-radius: 12px; margin-bottom: 0.5rem; }
    section[data-testid="stSidebar"] .stButton > button p { color: #1a1a1a !important; }
    section[data-testid="stSidebar"] .stButton > button:hover { background: #8a5a2b !important; }
    section[data-testid="stSidebar"] .stButton > button:hover p { color: white !important; }
    
    .stProgress > div > div > div > div { background: #c99a3a !important; }
    
    [data-testid="stMetricValue"] { color: #1a1a1a !important; font-weight: 800 !important; }
    [data-testid="stMetricLabel"] { color: #5c3a1a !important; font-weight: 600 !important; }
    
    .stDataFrame, .stDataFrame * { color: #1a1a1a; }
    
    #MainMenu, footer, header {visibility: hidden;}
    
    @media (max-width: 768px) { 
        .main-header h1 { font-size: 1.3rem; } 
        .card { padding: 1rem; } 
    }
</style>
""", unsafe_allow_html=True)

# Session state
if "halaman" not in st.session_state: st.session_state.halaman = "input"
if "batch_data" not in st.session_state: st.session_state.batch_data = []
if "setup_batch" not in st.session_state: st.session_state.setup_batch = {}
if "kode_sekolah" not in st.session_state: st.session_state.kode_sekolah = "SDN01-LB"
if "nama_enum" not in st.session_state: st.session_state.nama_enum = "Enumerator"

# User dari session state
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
        key="pilih_sekolah_sidebar",
        label_visibility="collapsed"
    )
    st.session_state.kode_sekolah = pilihan
    user["kode_sekolah"] = pilihan
    
    st.markdown("---")
    
    nama_input = st.text_input("Nama Anda (opsional)", value=st.session_state.nama_enum, key="nama_enum_sidebar")
    st.session_state.nama_enum = nama_input if nama_input else "Enumerator"
    user["nama"] = st.session_state.nama_enum
    
    st.markdown("---")
    
    if st.button("📝 Input Data"): st.session_state.halaman = "input"; st.rerun()
    if st.button("📊 Dashboard"): st.session_state.halaman = "dashboard"; st.rerun()

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
        with col2: ba_sayur = st.number_input("Sayur (g)", 0.0, 500.0, 24.0)
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
            <p style="color: #1a1a1a; font-weight: 600;">Progress: <b style="color: #5c3a1a;">{sudah}/{target}</b> siswa</p>
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
            
            st.markdown("**📷 Foto Sisa Makanan Siswa Ini**")
            foto_sisa = st.file_uploader("Upload foto sisa", type=["jpg","jpeg","png"], key=f"fs_{sudah}")
            
            default_nasi = 0
            default_sayur = 0
            default_lauk = 0
            ai_alasan = ""
            ai_version = "0_0_0_0"
            
            if foto_sisa:
                st.image(foto_sisa, caption="Sisa Makanan", use_container_width=True)
                
                cache_key = f"ai_result_{sudah}"
                
                if cache_key not in st.session_state:
                    with st.spinner("🤖 AI menganalisis foto..."):
                        skor_ai = prediksi_skor_dari_foto(foto_sisa.getvalue())
                        st.session_state[cache_key] = skor_ai
                else:
                    skor_ai = st.session_state[cache_key]
                
                if skor_ai:
                    default_nasi = int(skor_ai.get("nasi", 0))
                    default_sayur = int(skor_ai.get("sayur", 0))
                    default_lauk = int(skor_ai.get("lauk", 0))
                    ai_alasan = skor_ai.get("alasan", "")
                    
                    ai_version = f"{default_nasi}_{default_sayur}_{default_lauk}_{len(ai_alasan)}"
                    
                    st.success("🤖 AI sudah mengisi skor otomatis. Silakan verifikasi/koreksi.")
                    if ai_alasan:
                        st.caption(f"💬 {ai_alasan}")
                else:
                    st.info("ℹ️ AI tidak tersedia. Silakan input manual.")
            
            st.markdown("**🎯 Skor Comstock (0-5)**")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                sn = st.selectbox("Nasi", [0,1,2,3,4,5], index=default_nasi, key=f"sn_{sudah}_{ai_version}")
                st.caption(KETERANGAN_SKOR[sn])
            with col2:
                ss = st.selectbox("Sayur", [0,1,2,3,4,5], index=default_sayur, key=f"ss_{sudah}_{ai_version}")
                st.caption(KETERANGAN_SKOR[ss])
            with col3:
                sl = st.selectbox("Lauk", [0,1,2,3,4,5], index=default_lauk, key=f"sl_{sudah}_{ai_version}")
                st.caption(KETERANGAN_SKOR[sl])
            
            keterangan = st.text_input("Keterangan (opsional)", key=f"ket_{sudah}")
            
            col_save, col_skip = st.columns(2)
            with col_save:
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
                                    "Link Foto Sebelum": "",
                                    "Link Foto Sesudah": link_sisa,
                                }
                                simpan_data(row)
                                st.session_state.batch_data.append(row)
                                
                                if f"ai_result_{sudah}" in st.session_state:
                                    del st.session_state[f"ai_result_{sudah}"]
                                
                                st.success(f"✅ Siswa {id_siswa} tersimpan!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Gagal: {e}")
            with col_skip:
                if st.button("⏭️ Lewati Siswa Ini"):
                    st.session_state.batch_data.append({"skip": True})
                    if f"ai_result_{sudah}" in st.session_state:
                        del st.session_state[f"ai_result_{sudah}"]
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.success(f"🎉 Selesai! {target} siswa sudah diinput.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 Lihat Dashboard"): 
                    st.session_state.halaman = "dashboard"; st.rerun()
            with col2:
                if st.button("🔄 Sesi Baru"): 
                    st.session_state.setup_batch = {}; st.session_state.batch_data = []; st.rerun()

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
    
    st.markdown("---")
    if st.button("⬅️ Kembali ke Input"):
        st.session_state.halaman = "input"
        st.rerun()
