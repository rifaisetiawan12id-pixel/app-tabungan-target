import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Saving Goals", layout="centered")

def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

try:
    client = init_connection()
    sheet = client.open("db_tabungan").sheet1
except Exception as e:
    st.error(f"Koneksi Gagal: {e}")

st.title("Target Tabungan 💰")

menu = st.sidebar.selectbox("Menu", ["Lihat Target", "Tambah Target"])

if menu == "Tambah Target":
    with st.form("tambah_form"):
        nama = st.text_input("Nama Barang")
        harga = st.number_input("Harga Target (Rp)", min_value=0)
        deadline = st.date_input("Tenggat Waktu")
        submit = st.form_submit_button("Simpan Target")
        
        if submit:
            # Pastikan urutan kolom sesuai: nama_barang, target_harga, terkumpul, deadline
            sheet.append_row([nama, harga, 0, str(deadline)])
            st.success("Target Berhasil Disimpan!")

elif menu == "Lihat Target":
    data = sheet.get_all_records()
    
    if not data:
        st.info("Belum ada target tabungan. Silakan tambah di menu samping.")
    else:
        for row in data:
            # Menggunakan .get() agar tidak error jika kolom tidak ditemukan
            nama_brg = row.get('nama_barang', 'Tanpa Nama')
            target = row.get('target_harga', 0)
            terkumpul = row.get('terkumpul', 0)
            
            if target > 0:
                persen = min(int((terkumpul / target) * 100), 100)
            else:
                persen = 0
            
            st.subheader(f"Target: {nama_brg}")
            st.progress(persen / 100)
            st.write(f"Progres: {persen}% (Rp{terkumpul:,} / Rp{target:,})")
            
            tambah_dana = st.number_input(f"Tambah saldo {nama_brg}", min_value=0, key=f"input_{nama_brg}")
            if st.button(f"Update {nama_brg}", key=f"btn_{nama_brg}"):
                cell = sheet.find(nama_brg)
                # Kolom 3 adalah 'terkumpul'
                sheet.update_cell(cell.row, 3, terkumpul + tambah_dana)
                st.rerun()
