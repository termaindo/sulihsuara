import streamlit as st
import naskah
import vo

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Alih Suara Pro", page_icon="🎙️", layout="wide")

# --- INISIALISASI STATE ---
# Menyimpan nama pengguna agar tidak ditanyakan berulang kali
if 'nama_pengguna' not in st.session_state:
    st.session_state.nama_pengguna = ""
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Home"

# --- HALAMAN PENYAPAAN (LOGIN NAMA) ---
if st.session_state.nama_pengguna == "":
    st.title("🎙️ Selamat Datang di Studio Alih Suara Pro")
    st.markdown("Sebelum kita mulai memproduksi naskah dan rekaman yang memukau, bolehkah saya tahu dengan siapa saya berinteraksi?")
    
    with st.form("form_nama"):
        nama_input = st.text_input("Masukkan Nama Anda:", placeholder="Contoh: Bapak Musa")
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
st.markdown(f"Halo, **{st.session_state.nama_pengguna}**! Pilih ruangan kerja Anda di bawah ini:")

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
    st.subheader(f"Selamat Datang di Lobi Studio, {st.session_state.nama_pengguna}!")
    st.write("Untuk memudahkan alur kerja Anda, aplikasi ini dibagi menjadi dua ruangan utama. Silakan pilih ruangan dan Direktur Kreatif yang Anda perlukan:")
    
    st.info("""
    **📝 1. Ruang Naskah (Modul Penyusun Naskah)**
    Ruangan ini dikhususkan untuk **Direktur Kreatif Penyusun Naskah**. Di sini, Anda akan dibimbing selangkah demi selangkah menyusun naskah *Voice Over* (VO) yang berjiwa, natural, dan sesuai target audiens. Hasil akhirnya adalah naskah matang yang langsung siap disalin.
    
    **🎧 2. Studio Rekaman (Modul Perekaman Suara)**
    Ruangan ini adalah wilayah **Direktur Kreatif Perekaman Suara**. Jika Anda sudah memiliki teks naskah final (baik yang dibuat dari Ruang 1 maupun naskah Anda sendiri), silakan bawa ke sini untuk diubah menjadi audio berkualitas tinggi menggunakan teknologi kecerdasan buatan.
    """)
    
    st.markdown("💡 **Petunjuk:** Silakan klik tombol navigasi di atas untuk mulai bekerja!")

elif st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()

elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
