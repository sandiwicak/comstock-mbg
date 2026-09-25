"""Utilitas perhitungan Comstock."""

COMSTOCK_MAPPING = {
    0: 0.00, 1: 0.25, 2: 0.50, 3: 0.75, 4: 0.95, 5: 1.00,
}

KETERANGAN_SKOR = {
    0: "Habis seluruhnya",
    1: "Tersisa 1/4 porsi",
    2: "Tersisa 1/2 porsi",
    3: "Tersisa 3/4 porsi",
    4: "Hanya dikonsumsi sedikit (±5%)",
    5: "Utuh (tidak dikonsumsi)",
}

SEKOLAH_LIST = {
    "SDN01-LB": "SDN 1 Labuhan Badas",
    "SDN02-LB": "SDN 2 Labuhan Badas",
    "SDN03-LB": "SDN 3 Labuhan Badas",
    "SDN04-LB": "SDN 4 Labuhan Badas",
    "SDN05-LB": "SDN 5 Labuhan Badas",
    "SDN06-LB": "SDN 6 Labuhan Badas",
    "SDN07-LB": "SDN 7 Labuhan Badas",
    "SDN08-LB": "SDN 8 Labuhan Badas",
    "SDN09-LB": "SDN 9 Labuhan Badas",
    "SDN10-LB": "SDN 10 Labuhan Badas",
}

def skor_ke_persentase_sisa(skor: int) -> float:
    return COMSTOCK_MAPPING.get(skor, 0.0)

def hitung_economic_loss(total_awal, total_sisa, harga_porsi):
    if total_awal > 0:
        return (total_sisa / total_awal) * harga_porsi
    return 0.0