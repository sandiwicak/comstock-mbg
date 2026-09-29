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
