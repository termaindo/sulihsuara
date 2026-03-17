import streamlit as st
import re

def run():
    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Informasi:** Studio ini secara otomatis mengubah format naskah Anda menjadi lembar kerja visual (berupa slide atau poin). Ini akan memudahkan Anda menyalin-tempel (*copy-paste*) teks ke aplikasi desain seperti Canva, Photoshop, atau Illustrator.")

    # --- 1. TARIK NASKAH DARI STATE ---
    raw_text = st.session_state.get("hasil_naskah", "")
    
    if not raw_text:
        st.warning("Belum ada naskah yang ditarik. Silakan buat naskah terlebih dahulu di Ruang 1 (Rapat Naskah).")
        return

    # --- 2. EKSTRAKSI TEKS DARI KOTAK MARKDOWN ---
    naskah_final = raw_text
    bt = "```" 
    pattern = rf"{bt}(?:text|markdown|xml)?\n(.*?)({bt})"
    match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_naskah:
        naskah_final = match_naskah.group(1).strip()
        st.success("✅ Naskah visual berhasil ditarik dari Ruang 1!")
    else:
        st.info("💡 Naskah ditarik tanpa filter blok kode.")

    # --- 3. KOTAK EDITING UTAMA ---
    st.markdown("### 📝 Papan Kerja Teks Visual")
    st.write("Anda bisa mengedit dan merapikan finalisasi teks di sini sebelum dipindahkan ke aplikasi desain:")
    
    user_input = st.text_area(
        "Edit naskah Anda di sini:", 
        value=naskah_final, 
        height=250,
        help="Perubahan di sini bersifat sementara untuk memudahkan Anda menyalin teks."
    )

    st.divider()

    # --- 4. PEMISAHAN OTOMATIS MENJADI SLIDE / POIN ---
    st.markdown("### 🗂️ Pemecahan per Slide / Poin")
    st.write("Sistem mencoba memecah naskah Anda berdasarkan paragraf atau poin (*bullet points*) untuk mempermudah alur desain visual Anda:")

    # Logika sederhana pemecah paragraf (berdasarkan dua enter berturut-turut)
    paragraphs = [p.strip() for p in user_input.split('\n\n') if p.strip()]
    
    if len(paragraphs) == 1:
        # Jika hanya ada 1 paragraf panjang, coba pecah berdasarkan baris baru (enter tunggal)
        paragraphs = [p.strip() for p in user_input.split('\n') if p.strip()]

    # Menampilkan ke dalam kotak-kotak kartu
    for i, p in enumerate(paragraphs):
        with st.container():
            st.markdown(f"**Slide / Bagian {i+1}**")
            st.info(p)
            # Tombol copy bawaan dari Streamlit `st.code` bisa dimanfaatkan
            st.code(p, language="text")
            
    st.success("✨ Semua bagian teks di atas sudah siap dipindahkan ke kanvas desain Anda!")
