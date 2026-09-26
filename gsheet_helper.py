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
    try:
        if "gcp
