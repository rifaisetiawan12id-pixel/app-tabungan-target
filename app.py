import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Saving Goals", layout="centered")

# --- KONEKSI DATABASE ---
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # Di Streamlit Cloud, kita gunakan st.secrets agar lebih aman daripada file JSON
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = init_connection()
sheet = client.open("db_tabungan").sheet1

# --- LOGIKA APLIKASI ---
st.title("Target Tabungan 💰")

menu = st.sidebar.selectbox("Menu", ["Lihat Target", "Tambah Target"])

if menu == "Tambah Target":
    with st.form("tambah_form"):
        nama = st.text_input("Nama Barang")
        harga = st.number_input("Harga Target (Rp)", min_value=0)
        deadline = st.date_input("Tenggat Waktu")
        submit = st.form_submit_button("Simpan Target")
        
        if submit:
            sheet.append_row([nama, harga, 0, str(deadline)])
            st.success("Target Berhasil Disimpan!")

elif menu == "Lihat Target":
    data = sheet.get_all_records()
    for row in data:
        target = row['target_harga']
        terkumpul = row['terkumpul']
        
        # Hitung Persentase
        persen = min(int((terkumpul / target) * 100), 100)
        
        st.subheader(f"Target: {row['nama_barang']}")
        st.progress(persen / 100)
        st.write(f"Progres: {persen}% (Rp{terkumpul:,} / Rp{target:,})")
        
        # Tombol Update
        tambah_dana = st.number_input(f"Tambah tabungan untuk {row['nama_barang']}", min_value=0, key=row['nama_barang'])
        if st.button(f"Update {row['nama_barang']}"):
            cell = sheet.find(row['nama_barang'])
            sheet.update_cell(cell.row, 3, terkumpul + tambah_dana)
            st.rerun()
