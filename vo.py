import streamlit as st
import re

def run():
    # Import dilakukan di dalam fungsi agar isolasi modul tetap terjaga
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    import json

    # --- 1. SETUP KREDENSIAL GOOGLE CLOUD TTS ---
    try:
        gcp_creds = st.secrets["GCP_CREDENTIALS"]
        if isinstance(gcp_creds, str):
            gcp_creds_dict = json.loads(gcp_creds)
        else:
            gcp_creds_dict = dict(gcp_creds)
            
        tts_credentials = service_account.Credentials.from_service_account_info(gcp_creds_dict)
    except Exception as e:
        st.error(f"Kredensial Google Cloud bermasalah: {e}")
        st.stop()

    st.title("🎧 Ruang 2: Studio Rekaman Pro")
    st.info("💡 **Informasi:** Studio ini memakai dukungan AI untuk membaca naskah yang dibuat di Ruang 1. Anda memiliki kendali penuh untuk mengedit naskah dan memodifikasi suara mesin di sini.")
    
    # --- 2. LOGIKA PENARIKAN & PENYIMPANAN DATA OTOMATIS ---
    # Memastikan variabel memori lokal tersedia untuk menyimpan hasil editan pengguna
    if "naskah_vo" not in st.session_state:
        st.session_state.naskah_vo = ""
    if "last_raw_naskah" not in st.session_state:
        st.session_state.last_raw_naskah = ""

    instruksi_rekaman = ""
    
    # Cek apakah ada data mentah dari Ruang 1 (naskah.py)
    raw_text = st.session_state.get("hasil_naskah", "")
    if raw_text:
        # A. Ekstraksi Arahan Rekaman (Mencari teks antara 🎛️ dan 🎙️)
        try:
            search_arahan = re.search(r"🎛️ Arahan Rekaman:(.*?)🎙️", raw_text, re.DOTALL | re.IGNORECASE)
            if search_arahan:
                instruksi_rekaman = search_arahan.group(1).strip()
        except:
            pass

        # B. Deteksi apakah ini naskah BARU dari Ruang 1
        if raw_text != st.session_state.last_raw_naskah:
            st.session_state.last_raw_naskah = raw_text # Catat naskah mentah terbaru
            
            # Ekstraksi Naskah Final di dalam blok kode ```
            bt = "```" 
            pattern = rf"{bt}(?:text|markdown)?\n(.*?){bt}"
            match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            
            if match_naskah:
                # Timpa naskah di Studio dengan yang baru ditarik
                st.session_state.naskah_vo = match_naskah.group(1).strip()
                st.success("✅ Naskah baru berhasil ditarik otomatis dari Ruang 1!")
            else:
                st.session_state.naskah_vo = raw_text
                st.info("💡 Naskah ditarik tanpa filter blok kode.")
    else:
        if not st.session_state.naskah_vo:
            st.info("💡 Belum ada naskah dari Ruang 1. Silakan buat naskah dulu atau ketik manual di bawah.")

    # --- 3. TAMPILAN ARAHAN, PANDUAN TEKNIS & KOTAK KERJA ---
    if instruksi_rekaman:
        with st.expander("📖 Lihat Panduan Suara dari Direktur Kreatif", expanded=True):
            st.markdown(instruksi_rekaman)

    # Contekan Teknis untuk mengarahkan pengguna awam
    with st.expander("💡 CONTEKAN: Cara Mengatur Mesin agar Lebih Natural", expanded=True):
        st.markdown("""
        Jika Anda bingung bagaimana menerapkan arahan di atas ke dalam pengaturan mesin, gunakan rumus ini:
        
        * 🔥 **Energetik / Promo:** Nada (Pitch) **+1.0 s/d +3.0** | Laju (Speed) **1.1 s/d 1.2**
        * 👔 **Berwibawa / Serius:** Nada (Pitch) **-2.0 s/d -4.0** | Laju (Speed) **0.8 s/d 0.9**
        * ☕ **Ramah / Santai:** Nada (Pitch) **+0.5 s/d +1.5** | Laju (Speed) **0.9 s/d 1.1**
        
        **Trik Mengatur Napas AI (Edit langsung di kotak bawah!):**
        * Jika mesin bicara terlalu kaku/terpotong: **HAPUS tanda koma (,)** di area tersebut.
        * Jika mesin bicara terlalu cepat tanpa jeda: **TAMBAHKAN tanda koma (,)** atau ganti menjadi titik (.) untuk napas yang lebih panjang.
        """)

    # Kotak Teks Utama (Bisa diketik dan diedit langsung oleh pengguna)
    st.markdown("**📱 PENGGUNA HP:** Abaikan tulisan *'Press Ctrl+Enter'* di dalam kotak. Cukup ketuk di area luar kotak atau langsung klik tombol **Produksi Suara** setelah selesai mengedit naskah.")
    user_input = st.text_area(
        "📝 Kotak Kerja Naskah (Anda BEBAS mengetik, menghapus, atau mengubah tanda baca di sini):", 
        value=st.session_state.naskah_vo, 
        height=350,
        help="Semua perubahan yang Anda ketik di sini akan disimpan otomatis saat Anda menekan tombol produksi."
    )
    
    # Simpan hasil editan pengguna kembali ke session_state agar tidak hilang
    st.session_state.naskah_vo = user_input

    # Panel Kontrol Mesin
    col1, col2, col3 = st.columns(3)
    with col1:
        voice_opt = st.selectbox(
            "Pilih Karakter Suara:", 
            [
                "Wanita (Wavenet-D)", 
                "Wanita (Wavenet-A)", 
                "Pria (Wavenet-B)", 
                "Pria (Wavenet-C)"
            ]
        )
    with col2:
        speed = st.slider("Laju Bicara (Speed):", 0.5, 1.5, 1.0, 0.1)
    with col3:
        pitch = st.slider("Nada Suara (Pitch):", -10.0, 10.0, 0.0, 0.5)

    # --- 4. PROSES PRODUKSI AUDIO ---
    if st.button("🔥 Produksi Suara Pro Sekarang", use_container_width=True):
        if user_input:
            try:
                with st.spinner("Mesin sedang meracik frekuensi suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    # Pembersihan teks dari instruksi non-verbal (berjaga-jaga jika pengguna mengetiknya)
                    clean_text = re.sub(r'\[.*?\]', '', user_input)
                    clean_text = re.sub(r'\(.*?\)', '', clean_text)
                    
                    synthesis_input = texttospeech.SynthesisInput(text=clean_text.strip())
                    
                    # Mapping Suara yang sudah diurutkan sesuai dropdown
                    voice_map = {
                        "Wanita (Wavenet-D)": "id-ID-Wavenet-D",
                        "Wanita (Wavenet-A)": "id-ID-Wavenet-A",
                        "Pria (Wavenet-B)": "id-ID-Wavenet-B",
                        "Pria (Wavenet-C)": "id-ID-Wavenet-C"
                    }
                    
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="id-ID", 
                        name=voice_map.get(voice_opt, "id-ID-Wavenet-D")
                    )
                    
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=speed,
                        pitch=pitch
                    )

                    response = client.synthesize_speech(
                        input=synthesis_input, 
                        voice=voice, 
                        audio_config=audio_config
                    )

                    st.success("✅ Berhasil! Silakan dengarkan hasilnya:")
                    st.audio(response.audio_content, format="audio/mp3")
                    
            except Exception as e:
                st.error(f"Gagal memproduksi suara. Detail: {e}")
        else:
            st.warning("Silakan isi naskah terlebih dahulu.")
