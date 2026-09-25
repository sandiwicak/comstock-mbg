"""Upload foto ke Google Drive - VERSI SEMENTARA (upload dimatikan)."""

def upload_foto(file_bytes, filename, subfolder=""):
    """
    SEMENTARA: Upload foto dimatikan karena Service Account tidak punya kuota.
    Foto tetap diproses di aplikasi, tapi tidak disimpan ke Drive.
    """
    print(f"[INFO] Foto {filename} tidak diupload (fitur sementara dimatikan).")
    return ""  # Kosongkan link foto