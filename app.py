elif menu == "Lihat Target":
    data = sheet.get_all_records()
    if not data:
        st.info("Belum ada data. Silakan tambah di menu 'Tambah Target'.")
    else:
        # Gunakan enumerate untuk memberi nomor unik agar tidak Duplicate Key Error
        for i, row in enumerate(data):
            nama_brg = row.get('nama_barang')
            if not nama_brg: continue
            
            target = int(row.get('target_harga', 0))
            terkumpul = int(row.get('terkumpul', 0))
            
            st.subheader(f"Target: {nama_brg}")
            persen = min(int((terkumpul / target) * 100), 100) if target > 0 else 0
            st.progress(persen / 100)
            st.write(f"Progres: {persen}% (Rp{terkumpul:,} / Rp{target:,})")
            
            # Tambahkan i pada key agar unik: key=f"in_{i}"
            tambah_dana = st.number_input(f"Tambah saldo {nama_brg} (Baris {i+1})", min_value=0, key=f"in_{i}")
            if st.button(f"Update {nama_brg} #{i+1}", key=f"btn_{i}"):
                try:
                    # Update langsung berdasarkan nomor baris (i + 2 karena baris 1 adalah header)
                    sheet.update_cell(i + 2, 3, terkumpul + tambah_dana)
                    st.success("Saldo berhasil diupdate!")
                    st.rerun()
                except:
                    st.error("Gagal update ke Google Sheets.")
