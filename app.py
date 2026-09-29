# Input API Key di halaman utama
if not st.session_state.groq_api_key_input:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔑 Masukkan Groq API Key</div>', unsafe_allow_html=True)
    ...
    st.stop()
