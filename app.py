import streamlit as st
import naskah
import vo

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Alih Suara Pro", page_icon="🎙️", layout="wide")

# Inisialisasi state navigasi
if 'menu_aktif' not in st.session_state:import streamlit as st
import naskah
import vo

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Alih Suara Pro", page_icon="🎙️", layout="wide")

# Inisialisasi state navigasi
if 'menu_aktif' not in st.session_state:
    st.session_state.menu_aktif = "Home"

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🎙️ Navigasi Studio")
pilihan = st.sidebar.radio(
    "Pilih Ruangan:", 
    ["Home", "1. Ruang Naskah", "2. Studio Rekaman"],
    index=["Home", "1. Ruang Naskah", "2. Studio Rekaman"].index(st.session_state.menu_aktif)
)

# Sinkronisasi pilihan sidebar dengan state
if st.session_state.menu_aktif != pilihan:
    st.session_state.menu_aktif = pilihan
    st.rerun()

# --- ROUTER LOGIC ---
if st.session_state.menu_aktif == "Home":
    st.title("🎙️ Selamat Datang di Studio Alih Suara Pro")
    st.markdown("Sesuai dengan arsitektur modular, aplikasi ini dibagi menjadi dua ruangan untuk **mencegah konflik sistem kredensial**.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📝 Ruang 1: Pembuatan Naskah\nBerdiskusi dengan AI Direktur Kreatif untuk menyusun naskah yang berjiwa.")
        if st.button("➡️ Masuk ke Ruang Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Ruang Naskah"
            st.rerun()
            
    with col2:
        st.success("### 🎧 Ruang 2: Studio Rekaman\nMengubah naskah final menjadi suara natural Neural2.")
        if st.button("➡️ Masuk ke Studio Rekaman", use_container_width=True):
            st.session_state.menu_aktif = "2. Studio Rekaman"
            st.rerun()

elif st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()

elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
    st.session_state.menu_aktif = "Home"

# --- SIDEBAR NAVIGASI ---
st.sidebar.title("🎙️ Navigasi Studio")
pilihan = st.sidebar.radio(
    "Pilih Ruangan:", 
    ["Home", "1. Ruang Naskah", "2. Studio Rekaman"],
    index=["Home", "1. Ruang Naskah", "2. Studio Rekaman"].index(st.session_state.menu_aktif)
)

# Sinkronisasi pilihan sidebar dengan state
if st.session_state.menu_aktif != pilihan:
    st.session_state.menu_aktif = pilihan
    st.rerun()

# --- ROUTER LOGIC ---
if st.session_state.menu_aktif == "Home":
    st.title("🎙️ Selamat Datang di Studio Alih Suara Pro")
    st.markdown("Sesuai dengan arsitektur modular, aplikasi ini dibagi menjadi dua ruangan untuk **mencegah konflik sistem kredensial**.")
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("### 📝 Ruang 1: Pembuatan Naskah\nBerdiskusi dengan AI Direktur Kreatif untuk menyusun naskah yang berjiwa.")
        if st.button("➡️ Masuk ke Ruang Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Ruang Naskah"
            st.rerun()
            
    with col2:
        st.success("### 🎧 Ruang 2: Studio Rekaman\nMengubah naskah final menjadi suara natural Neural2.")
        if st.button("➡️ Masuk ke Studio Rekaman", use_container_width=True):
            st.session_state.menu_aktif = "2. Studio Rekaman"
            st.rerun()

elif st.session_state.menu_aktif == "1. Ruang Naskah":
    naskah.run()

elif st.session_state.menu_aktif == "2. Studio Rekaman":
    vo.run()
