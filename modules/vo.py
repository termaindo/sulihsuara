import streamlit as st
import re
import os
from google.cloud import texttospeech
from google.oauth2 import service_account

def run():
    st.title("🎙️ Ruang 2: Studio Rekaman (Voice Over)")
    st.info("💡 **Informasi:** Studio ini telah dilengkapi filter **Auto-Clean Punctuation**. Semua tanda baca asing seperti bintang (*), pagar (#), atau titik dua (:) akan otomatis dibersihkan sehingga suara AI terdengar 100% natural!")

    # Setup credentials
    try:
        gcp_service_account_dict = st.secrets["gcp_service_account"]
        tts_credentials = service_account.Credentials.from_service_account_info(dict(gcp_service_account_dict))
    except Exception as e:
        st.error(f"Gagal memuat kredensial GCP TTS: {e}")
        return
        
    teks_bawaan = ""
    raw_text = st.session_state.get("hasil_naskah", "")
    if raw_text:
        bt = "```" 
        pattern = rf"{bt}(?:text|markdown)?\n(.*?)({bt})"
        match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if match:
            teks_bawaan = match.group(1).strip()
            st.success("✅ Naskah final dari Ruang Naskah berhasil ditarik otomatis ke studio!")
        else:
            st.info("💡 Sistem mendeteksi naskah di Ruang 1, namun formatnya tidak standar. Silakan copy-paste manual jika kotak di bawah kosong.")
    
    if not teks_bawaan:
        st.write("Silakan tempelkan (*paste*) naskah Anda di bawah ini untuk diubah menjadi suara.")

    # --- 3. ANTARMUKA STUDIO REKAMAN ---
    user_input = st.text_area("Kotak Naskah Studio:", value=teks_bawaan, height=250)

    # Panel Kontrol Suara
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox(
            "Pilih Karakter Suara:", 
            ["Wanita (Wavenet-A)", "Pria (Wavenet-B)", "Pria (Wavenet-C)", "Wanita (Wavenet-D)"]
        )
    with col2:
        speed = st.slider("Kecepatan (Pacing):", 0.5, 1.5, 1.0, 0.1, help="Lebih dari 1.0 untuk bicara cepat, kurang dari 1.0 untuk bicara lambat.")
    with col3:
        pitch = st.slider("Nada (Pitch):", -10.0, 10.0, 0.0, 0.5, help="Positif untuk suara ceria/tinggi, Negatif untuk suara berat/berwibawa.")

    # --- 4. PROSES PRODUKSI AUDIO ---
    if st.button("🔥 Produksi Suara Sekarang", use_container_width=True, type="primary"):
        if user_input:
            try:
                with st.spinner("Mesin Wavenet Google sedang meracik frekuensi suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    # ========================================================
                    # 🧹 ALGORITMA PEMBERSIHAN NASKAH (AUTO-CLEAN PUNCTUATION)
                    # ========================================================
                    # 1. Menghapus instruksi sutradara dalam tanda kurung [] atau ()
                    naskah_bersih = re.sub(r'\[.*?\]', '', user_input)
                    naskah_bersih = re.sub(r'\(.*?\)', '', naskah_bersih)
                    
                    # 2. Ganti tanda hubung (-) dan garis miring (/) dengan spasi agar tidak dibaca menyambung
                    naskah_bersih = naskah_bersih.replace('-', ' ').replace('/', ' ')
                    
                    # 3. HAPUS SEMUA TANDA BACA KECUALI TITIK (.), KOMA (,), SERU (!), TANYA (?)
                    # Logika Regex: Sisakan hanya huruf/angka (\w), spasi (\s), dan .,!?
                    naskah_bersih = re.sub(r'[^\w\s.,!?]', '', naskah_bersih)
                    
                    # 4. Hapus underscore (_) secara manual karena (\w) memasukkan underscore
                    naskah_bersih = naskah_bersih.replace('_', '')
                    
                    # 5. Hilangkan spasi ganda akibat penghapusan karakter
                    naskah_bersih = re.sub(r' +', ' ', naskah_bersih)
                    # ========================================================
                    
                    # Menampilkan naskah yang sudah dibersihkan ke layar (Opsional, agar user tahu)
                    with st.expander("🔍 Lihat Naskah Murni yang Dibaca AI (Telah Dibersihkan)"):
                        st.write(naskah_bersih.strip())

                    synthesis_input = texttospeech.SynthesisInput(text=naskah_bersih.strip())
                    
                    # Pemetaan nama suara Google Cloud
                    voice_map = {
                        "Wanita (Wavenet-A)": "id-ID-Wavenet-A",
                        "Pria (Wavenet-B)": "id-ID-Wavenet-B",
                        "Pria (Wavenet-C)": "id-ID-Wavenet-C",
                        "Wanita (Wavenet-D)": "id-ID-Wavenet-D"
                    }
                    voice_name = voice_map.get(gender, "id-ID-Wavenet-A")
                    
                    voice = texttospeech.VoiceSelectionParams(language_code="id-ID", name=voice_name)
                    
                    # Konfigurasi Audio dengan Pitch
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3, 
                        speaking_rate=speed,
                        pitch=pitch
                    )

                    response_audio = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

                    st.success("✅ Produksi Selesai! Klik tombol play di bawah untuk mendengarkan:")
                    st.audio(response_audio.audio_content, format="audio/mp3")
                    
                    st.caption("Tips: Jika suara terdengar terlalu datar, coba atur 'Nada (Pitch)' sedikit ke arah negatif untuk pria agar lebih berwibawa.")
            except Exception as e:
                st.error(f"Gagal memproduksi suara: {e}")
        else:
            st.warning("Kotak naskah masih kosong. Silakan isi terlebih dahulu.")
            
    # --- NAVIGASI BAWAH ---
    st.divider()
    st.markdown("### 🚀 Lanjut Produksi Karya Lain")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("📝 Kembali ke Ruang Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Ruang Naskah"
            st.rerun()
    with col_nav2:
        if st.button("🎨 Ke Studio Cetak (Visual)", use_container_width=True):
            st.session_state.menu_aktif = "3. Studio Cetak"
            st.rerun()
