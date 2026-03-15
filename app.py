import streamlit as st
import naskah
import vo

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Alih Suara Pro", page_icon="🎙️", layout="wide")

# --- INISIALISASI STATE ---
if 'nama_pengguna' not in st.session_state:
    st.session_state.nama_pengguna = ""
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Home"

# --- HALAMAN PENYAPAAN (LOGIN NAMA) ---
if st.session_state.nama_pengguna == "":
    st.title("🎙️ Selamat Datang di Studio Alih Suara Pro")
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
st.title("🎙️ Studio Alih Suara Pro")
st.markdown(f"Halo, sobat **{st.session_state.nama_pengguna}**! Pilih ruangan kerja Anda di bawah ini:")

# Membuat 3 tombol sejajar sebagai menu utama
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🏠 Halaman Utama", use_container_width=True):
        st.session_state.menu_aktif = "Home"
        st.rerun()
with col2:
    if st.button("📝 Ruang Naskah", use_container_width=True):
        st.session_state.menu_aktif = "1. Ruang Naskah"
        st.rerun()
with col3:
    if st.button("🎧 Studio Rekaman", use_container_width=True):
        st.session_state.menu_aktif = "2. Studio Rekaman"
        st.rerun()

st.divider()

# --- ROUTER LOGIC ---
if st.session_state.menu_aktif == "Home":
    st.subheader(f"Selamat Datang di Lobi Studio, sobat {st.session_state.nama_pengguna}!")
    st.write("Untuk memastikan sistem berjalan tanpa gangguan memori, aplikasi ini dibagi menjadi dua ruangan. Silakan pilih ruangan yang Anda perlukan:")
    
    st.info("""
    **📝 1. Ruang Naskah (Direktur Kreatif Penyusun Naskah)**
    Di sini Anda akan dibimbing selangkah demi selangkah menyusun naskah *Voice Over* (VO) yang berjiwa dan sesuai target audiens. Hasil akhirnya adalah naskah matang yang langsung siap disalin (di-copy).
    
    **🎧 2. Studio Rekaman (Direktur Kreatif Perekaman Suara)**
    Jika Anda sudah memiliki teks naskah final yang siap baca, silakan bawa ke sini. Mesin AI Google Cloud akan mengubah tulisan Anda menjadi audio bersuara manusia yang natural.
    """)

elif st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()

elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
