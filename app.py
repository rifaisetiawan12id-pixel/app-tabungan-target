import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 1. Fungsi Inisialisasi Koneksi
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

# Hubungkan ke Google Sheets
try:
    client = init_connection()
    sheet = client.open("db_tabungan").sheet1
except Exception as e:
    st.error(f"Koneksi Gagal: {e}")

st.title("Target Tabungan 💰")

# 2. Sidebar Menu
menu = st.sidebar.selectbox("Menu", ["Lihat Target", "Tambah Target"])

if menu == "Tambah Target":
    with st.form("tambah_form"):
        nama = st.text_input("Nama Barang")
        harga = st.number_input("Harga Target (Rp)", min_value=0)
        deadline = st.date_input("Tenggat Waktu")
        submit = st.form_submit_button("Simpan Target")
        
        if submit and nama:
            # Simpan ke Google Sheets (nama, target, terkumpul, deadline)
            sheet.append_row([nama, harga, 0, str(deadline)])
            st.success(f"Target '{nama}' berhasil disimpan!")

elif menu == "Lihat Target":
    data = sheet.get_all_records()
    
    if not data:
        st.info("Belum ada target tabungan. Silakan tambah di menu 'Tambah Target'.")
    else:
        # Loop data menggunakan enumerate agar setiap input punya ID unik (key)
        for i, row in enumerate(data):
            nama_brg = row.get('nama_barang')
            if not nama_brg: continue # Skip jika baris kosong
            
            target = int(row.get('target_harga', 0))
            terkumpul = int(row.get('terkumpul', 0))
            
            st.subheader(f"Target: {nama_brg}")
            
            # Hitung Progres
            if target > 0:
                persen = min(int((terkumpul / target) * 100), 100)
            else:
                persen = 0
                
            st.progress(persen / 100)
            st.write(f"Progres: {persen}% (Rp{terkumpul:,} / Rp{target:,})")
            
            # Form untuk tambah saldo
            tambah_dana = st.number_input(f"Tambah saldo untuk {nama_brg}", min_value=0, key=f"input_{i}")
            if st.button(f"Update Saldo {nama_brg}", key=f"btn_{i}"):
                # Update kolom ke-3 (terkumpul) di baris yang sesuai (i+2 karena header di baris 1)
                sheet.update_cell(i + 2, 3, terkumpul + tambah_dana)
                st.success(f"Saldo {nama_brg} berhasil ditambah!")
                st.rerun()
            st.divider()
