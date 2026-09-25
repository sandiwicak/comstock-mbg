"""Autentikasi Google OAuth."""
import streamlit as st

def cek_login():
    """Cek apakah user sudah login. Return dict user atau None."""
    if "user" in st.session_state and st.session_state.user:
        return st.session_state.user
    return None

def login_google():
    """Tombol login Google (simulasi dengan kode akses untuk kecepatan)."""
    st.markdown("### 🔐 Login Enumerator")
    st.info("Masukkan kode akses yang diberikan admin sekolah.")
    
    kode = st.text_input("Kode Akses Sekolah", type="password", placeholder="Contoh: SDN01-2026")
    nama = st.text_input("Nama Anda", placeholder="Nama lengkap")
    
    if st.button("🚀 Masuk"):
        # Format kode: KODESEKOLAH-TAHUN (misal SDN01-LB-2026)
        if not kode or not nama:
            st.error("Kode akses dan nama wajib diisi!")
            return None
        
        # Validasi kode (bisa diperluas nanti ke database)
        kode_valid = {
            "SDN01-2026": "SDN01-LB",
            "SDN02-2026": "SDN02-LB",
            "SDN03-2026": "SDN03-LB",
            "SDN04-2026": "SDN04-LB",
            "SDN05-2026": "SDN05-LB",
            "SDN06-2026": "SDN06-LB",
            "SDN07-2026": "SDN07-LB",
            "SDN08-2026": "SDN08-LB",
            "SDN09-2026": "SDN09-LB",
            "SDN10-2026": "SDN10-LB",
        }
        
        if kode in kode_valid:
            st.session_state.user = {
                "nama": nama,
                "kode_sekolah": kode_valid[kode],
                "kode_akses": kode,
            }
            st.rerun()
        else:
            st.error("Kode akses tidak valid!")
    
    st.markdown("---")
    st.caption("💡 Kode akses dibagikan admin. Contoh: SDN01-2026 untuk SDN 1 Labuhan Badas.")
    return None

def logout():
    st.session_state.user = None
    st.rerun()