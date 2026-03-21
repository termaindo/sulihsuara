import streamlit as st
from modules import naskah, vo, infografis

st.set_page_config(page_title="Studio Kreatif Pro", page_icon="✨", layout="wide")

# Set menu default ke Studio Kreasi Naskah
if "menu_aktif" not in st.session_state:
    st.session_state.menu_aktif = "1. Studio Kreasi Naskah"

st.sidebar.title("✨ Menu Navigasi")

# Membuat daftar menu standar baru yang telah dipatenkan
daftar_menu = [
    "1. Studio Kreasi Naskah", 
    "2. Studio Kreasi Suara / Audio", 
    "3. Studio Kreasi Cetak / Visual"
]

menu = st.sidebar.radio(
    "Pilih Ruang Kerja:",
    daftar_menu,
    index=daftar_menu.index(st.session_state.menu_aktif)
)

st.session_state.menu_aktif = menu

# Pengalihan (Routing) berdasarkan nama baru
if menu == "1. Studio Kreasi Naskah":
    naskah.run()
elif menu == "2. Studio Kreasi Suara / Audio":
    vo.run()
elif menu == "3. Studio Kreasi Cetak / Visual":
    infografis.run()
