"""Upload foto ke Google Drive - DIMATIKAN karena kebijakan Google 2025.

Sejak April 2025, Service Account tidak punya kuota Google Drive sendiri.
Upload foto tidak bisa dilakukan tanpa Shared Drive atau OAuth user.

Fungsi ini tetap ada supaya app.py tidak error, tapi tidak upload apa-apa.
"""


def upload_foto(file_bytes, filename, subfolder=""):
    """
    DIMATIKAN: Tidak upload ke Drive.
    
    Return string kosong supaya kolom 'Link Foto' di Sheets tetap terisi
    dengan nilai kosong, bukan error.
    
    Args:
        file_bytes: Bytes foto (diabaikan)
        filename: Nama file (diabaikan)
        subfolder: Subfolder tujuan (diabaikan)
    
    Returns:
        str: Selalu string kosong
    """
    print(f"[INFO] Foto '{filename}' tidak diupload (Service Account tidak punya kuota Drive).")
    return ""
