import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Inisialisasi koneksi
def init_connection():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

client = init_connection()
sheet = client.open("db_tabungan").sheet1

st.title("Target Tabungan 💰")
menu = st.sidebar.selectbox("Menu", ["Lihat Target", "Tambah Target"])

if menu == "Tambah Target":
    with st.form("tambah_form"):
        nama = st.text_input("Nama Barang")
        harga = st.number_input("Harga Target (Rp)", min_value=0)
        deadline = st.date_input("Tenggat Waktu")
        submit = st.form_submit_button("Simpan Target")
        if submit and nama:
            sheet.append_row([nama, harga, 0, str(deadline)])
            st.success(f"Target {nama} berhasil disimpan!")

elif menu == "Lihat Target":
    data = sheet.get_all_records()
    if not data:
        st.info("Belum ada data. Silakan tambah di menu 'Tambah Target'.")
    else:
        for row in data:
            nama_brg = row.get('nama_barang')
            if not nama_brg: continue
            
            target = int(row.get('target_harga', 0))
            terkumpul = int(row.get('terkumpul', 0))
            
            st.subheader(f"Target: {nama_brg}")
            persen = min(int((terkumpul / target) * 100), 100) if target > 0 else 0
            st.progress(persen / 100)
            st.write(f"Progres: {persen}% (Rp{terkumpul:,} / Rp{target:,})")
            
            tambah_dana = st.number_input(f"Tambah saldo {nama_brg}", min_value=0, key=f"in_{nama_brg}")
            if st.button(f"Update {nama_brg}", key=f"btn_{nama_brg}"):
                try:
                    cell = sheet.find(nama_brg)
                    if cell:
                        # Update kolom ke-3 (terkumpul)
                        sheet.update_cell(cell.row, 3, terkumpul + tambah_dana)
                        st.success("Saldo berhasil diupdate!")
                        st.rerun()
                except:
                    st.error("Gagal menemukan data di Google Sheets.")
