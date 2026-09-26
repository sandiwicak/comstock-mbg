"""Koneksi & operasi Google Sheets - baca dari Streamlit Secrets."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json
import base64

SHEET_NAME = "Data_Comstock_MBG"
WORKSHEET_NAME = "Data"

HEADERS = [
    "Timestamp", "Tanggal", "Hari Ke-", "Kode Sekolah", "Nama Sekolah",
    "Nama Enumerator", "Email Enumerator", "ID Siswa", "Kelas",
    "Skor Visual Nasi", "Berat Awal Nasi (g)", "Berat Sisa Nasi (g)", "% Sisa Nasi",
    "Skor Visual Sayur", "Berat Awal Sayur (g)", "Berat Sisa Sayur (g)", "% Sisa Sayur",
    "Skor Visual Lauk", "Berat Awal Lauk (g)", "Berat Sisa Lauk (g)", "% Sisa Lauk",
    "Total Awal (g)", "Total Sisa (g)", "Harga Satuan (Rp)", "Economic Loss (Rp)",
    "Keterangan", "Link Foto Sebelum", "Link Foto Sesudah"
]


def get_credentials_dict():
    """Ambil credentials dari Streamlit Secrets."""
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])

            # Decode private_key dari base64
            if "private_key_b64" in creds_dict:
                creds_dict["private_key"] = base64.b64decode(
                    creds_dict["private_key_b64"]
                ).decode("utf-8")
                del creds_dict["private_key_b64"]

            return creds_dict
    except Exception as e:
        st.error(f"Gagal baca Secrets: {e}")

    return None


def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = get_credentials_dict()
    if creds_dict is None:
        raise Exception("Credentials tidak ditemukan di Streamlit Secrets.")

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)


def get_or_create_worksheet():
    client = get_client()
    try:
        sh = client.open(SHEET_NAME)
    except gspread.SpreadsheetNotFound:
        sh = client.create(SHEET_NAME)
    try:
        ws = sh.worksheet(WORKSHEET_NAME)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=WORKSHEET_NAME, rows=10000, cols=len(HEADERS))
        ws.append_row(HEADERS)
        ws.format("A1:AB1", {"textFormat": {"bold": True}})
    return ws


def simpan_data(row_dict: dict):
    ws = get_or_create_worksheet()
    row = [row_dict.get(h, "") for h in HEADERS]
    ws.append_row(row, value_input_option="USER_ENTERED")
    return True


def ambil_semua_data() -> list:
    ws = get_or_create_worksheet()
    return ws.get_all_records()
