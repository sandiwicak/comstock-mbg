"""Koneksi & operasi Google Sheets."""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import os

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


def get_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # PRIORITAS 1: Baca dari Streamlit Secrets (untuk cloud)
    try:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        return gspread.authorize(creds)
    except Exception:
        pass
    
    # PRIORITAS 2: Baca dari file credentials.json (untuk lokal)
    if os.path.exists("credentials.json"):
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
        return gspread.authorize(creds)
    
    raise Exception("Credentials tidak ditemukan. Set Secrets di Streamlit Cloud.")


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
