import streamlit as st

# Mengimpor modul dari dalam folder 'modules'
from modules import naskah
from modules import vo
from modules import infografis

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Kreatif Pro", page_icon="🎙️", layout="wide")

# --- INISIALISASI STATE ---
if 'nama_pengguna' not in st.session_state:
    st.session_state.nama_pengguna = ""
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Home"

# --- HALAMAN PENYAPAAN (LOGIN NAMA) ---
if st.session_state.nama_pengguna == "":
    st.title("🎙️ Selamat Datang di Studio Kreatif Pro")
    st.markdown("Sebelum kita mulai memproduksi naskah dan rekaman yang memukau, bolehkah saya tahu dengan siapa saya berinteraksi?")
    
    with st.form("form_nama"):
        nama_input = st.text_input("Masukkan Nama Anda:", placeholder="Contoh: Bapak Rudi")
        submit_nama = st.form_submit_button("Masuk ke Studio ➡️")
        
        if submit_nama:
            if nama_input.strip() != "":
                st.session_state.nama_pengguna = nama_input.strip()
                st.rerun()
            else:
                st.warning("Mohon isi nama Anda terlebih dahulu untuk melanjutkan.")
    st.stop() # Hentikan eksekusi kode di bawahnya sampai nama diisi

# --- HEADER & NAVIGASI HALAMAN UTAMA ---
st.title("🎙️ Studio Kreatif Pro")
st.markdown(f"Halo, sobat **{st.session_state.nama_pengguna}**! Pilih ruangan kerja Anda di bawah ini:")

# Membuat 3 tombol sejajar sebagai menu utama
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📝 Ruang 1: Rapat Naskah", use_container_width=True):
        st.session_state.menu_aktif = "1. Ruang Naskah"
with col2:
    if st.button("🚀 Ruang 2: Studio Rekaman (VO)", use_container_width=True):
        st.session_state.menu_aktif = "2. Studio Rekaman"
with col3:
    if st.button("🎨 Ruang 3: Studio Cetak (Visual)", use_container_width=True):
        st.session_state.menu_aktif = "3. Studio Cetak"

st.divider()

# --- ROUTING MENU (PENGARAHAN KE MODUL) ---
if st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()
elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
elif st.session_state.menu_aktif == "3. Studio Cetak":
    infografis.run()
else:
    st.info("👈 Silakan pilih ruangan kerja di atas untuk memulai produksi Anda.")
