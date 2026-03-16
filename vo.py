import streamlit as st
import re
import os
import json
from datetime import datetime
import calendar

# --- KONFIGURASI KUOTA ---
FILE_KUOTA = "pemakaian_tts.json"
BATAS_MAKSIMAL = 1000000  # 1 Juta karakter
BATAS_WARNING = 990000    # Peringatan di 990 Ribu karakter

# Fungsi untuk menghitung sisa hari dalam bulan ini
def hitung_sisa_hari():
    sekarang = datetime.now()
    hari_terakhir = calendar.monthrange(sekarang.year, sekarang.month)[1]
    return hari_terakhir - sekarang.day + 1 # +1 agar hari H dihitung

# Fungsi untuk membaca dan mencatat pemakaian
def catat_pemakaian(tambahan_karakter=0):
    bulan_ini = datetime.now().strftime("%Y-%m")
    
    # Membaca file memori di drive
    if os.path.exists(FILE_KUOTA):
        try:
            with open(FILE_KUOTA, "r") as f:
                data = json.load(f)
        except:
            data = {"bulan": bulan_ini, "jumlah": 0}
    else:
        data = {"bulan": bulan_ini, "jumlah": 0}
        
    # Otomatis Reset jika berganti bulan!
    if data.get("bulan") != bulan_ini:
        data = {"bulan": bulan_ini, "jumlah": 0}
        
    # Menambahkan pemakaian baru
    data["jumlah"] += tambahan_karakter
    
    # Menyimpan kembali ke file drive
    with open(FILE_KUOTA, "w") as f:
        json.dump(data, f)
        
    return data["jumlah"]

def run():
    # Import dilakukan di dalam fungsi agar isolasi modul tetap terjaga
    from google.cloud import texttospeech
    from google.oauth2 import service_account

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

    # --- INJEKSI CSS UNTUK MENYEMBUNYIKAN "Press Ctrl+Enter" ---
    st.markdown("""
        <style>
            div[data-testid="InputInstructions"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎧 Ruang 2: Studio Rekaman Pro")
    
    # --- SISTEM PANTAU KUOTA (TAMPILAN UI) ---
    pemakaian_saat_ini = catat_pemakaian(0) # Hanya membaca, belum menambah
    persentase = min(pemakaian_saat_ini / BATAS_MAKSIMAL, 1.0)
    
    st.caption(f"📊 **Pemakaian Kuota Gratis Bulan Ini:** {pemakaian_saat_ini:,} / 995.000 karakter")
    st.progress(persentase)
    
    if pemakaian_saat_ini >= BATAS_WARNING:
        sisa_hari = hitung_sisa_hari()
        st.warning(f"⚠️ **PERHATIAN: KUOTA HAMPIR HABIS!**\nAnda telah menggunakan {pemakaian_saat_ini:,} karakter. Harap berhemat. Kuota Google TTS Anda akan otomatis di-reset menjadi nol (0) dalam **{sisa_hari} hari** lagi.")

    st.info("💡 **Informasi:** Studio ini memakai dukungan AI untuk membaca naskah yang dibuat di Ruang 1. Anda memiliki kendali penuh untuk mengedit naskah dan memodifikasi suara mesin di sini.")
    
    # --- 2. LOGIKA PENARIKAN & PENYIMPANAN DATA OTOMATIS ---
    if "naskah_vo" not in st.session_state:
        st.session_state.naskah_vo = ""
    if "last_raw_naskah" not in st.session_state:
        st.session_state.last_raw_naskah = ""

    instruksi_rekaman = ""
    
    raw_text = st.session_state.get("hasil_naskah", "")
    if raw_text:
        # A. Ekstraksi Arahan Rekaman
        try:
            search_arahan = re.search(r"🎛️ Arahan Rekaman:(.*?)🎙️", raw_text, re.DOTALL | re.IGNORECASE)
            if search_arahan:
                instruksi_rekaman = search_arahan.group(1).strip()
        except:
            pass

        # B. Deteksi apakah ini naskah BARU
        if raw_text != st.session_state.last_raw_naskah:
            st.session_state.last_raw_naskah = raw_text 
            
            bt = "```" 
            pattern = rf"{bt}(?:text|markdown)?\n(.*?){bt}"
            match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            
            if match_naskah:
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

    # Contekan Teknis
    with st.expander("💡 CONTEKAN: Cara Mengatur Mesin agar Lebih Natural", expanded=True):
        st.markdown("""
        Jika Anda bingung bagaimana menerapkan arahan di atas ke dalam pengaturan mesin, gunakan rumus ini:
        
        * 🔥 **Energetik / Promo:** Laju (Speed) **1.1 s/d 1.2** | Nada (Pitch) **+1.0 s/d +3.0**
        * 👔 **Berwibawa / Serius:** Laju (Speed) **0.8 s/d 0.9** | Nada (Pitch) **-2.0 s/d -4.0**
        * ☕ **Ramah / Santai:** Laju (Speed) **0.9 s/d 1.1** | Nada (Pitch) **+0.5 s/d +1.5**
        
        **Trik Mengatur Napas AI (Edit langsung di kotak bawah!):**
        * Jika mesin bicara terlalu kaku/terpotong: **HAPUS tanda koma (,)** di area tersebut.
        * Jika mesin bicara terlalu cepat tanpa jeda: **TAMBAHKAN tanda koma (,)** atau ganti menjadi titik (.) untuk napas yang lebih panjang.
        """)

    # Kotak Teks Utama
    st.markdown("**📱 PENGGUNA HP:** Silakan ketuk area teks di bawah ini untuk mengedit. Jika sudah selesai, langsung saja klik tombol **Produksi Suara** di bagian bawah.")
    user_input = st.text_area(
        "📝 Kotak Kerja Naskah (Anda BEBAS mengetik, menghapus, atau mengubah tanda baca di sini):", 
        value=st.session_state.naskah_vo, 
        height=350,
        help="Semua perubahan yang Anda ketik di sini akan disimpan otomatis saat Anda menekan tombol produksi."
    )
    
    st.session_state.naskah_vo = user_input

    # Panel Kontrol Mesin
    col1, col2, col3 = st.columns(3)
    with col1:
        voice_opt = st.selectbox(
            "Pilih Karakter Suara:", 
            [
                "Wanita (Wavenet-A)", 
                "Wanita (Wavenet-B)", 
                "Pria (Wavenet-C)", 
                "Pria (Wavenet-D)"
            ]
        )
    with col2:
        speed = st.slider("Laju Bicara (Speed):", 0.5, 1.5, 1.0, 0.1)
    with col3:
        pitch = st.slider("Nada Suara (Pitch):", -10.0, 10.0, 0.0, 0.5)

    # --- 4. PROSES PRODUKSI AUDIO ---
    if st.button("🔥 Produksi Suara Pro Sekarang", use_container_width=True):
        if user_input:
            
            clean_text = re.sub(r'\[.*?\]', '', user_input)
            clean_text = re.sub(r'\(.*?\)', '', clean_text)
            naskah_final = clean_text.strip()
            panjang_teks = len(naskah_final)
            
            # CEK SISA KUOTA SEBELUM PROSES
            sisa_kuota = BATAS_MAKSIMAL - pemakaian_saat_ini
            if panjang_teks > sisa_kuota:
                st.error(f"❌ **GAGAL:** Naskah ini membutuhkan {panjang_teks:,} karakter, sedangkan sisa kuota Anda hanya {sisa_kuota:,} karakter. Mohon tunggu {hitung_sisa_hari()} hari lagi hingga awal bulan depan.")
                return # Hentikan proses!
                
            try:
                with st.spinner("Mesin sedang meracik frekuensi suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    synthesis_input = texttospeech.SynthesisInput(text=naskah_final)
                    
                    # Pemetaan Suara Khusus 
                    voice_map = {
                        "Wanita (Wavenet-A)": "id-ID-Wavenet-A", 
                        "Wanita (Wavenet-B)": "id-ID-Wavenet-D", 
                        "Pria (Wavenet-C)": "id-ID-Wavenet-B",   
                        "Pria (Wavenet-D)": "id-ID-Wavenet-C"    
                    }
                    
                    voice = texttospeech.VoiceSelectionParams(
                        language_code="id-ID", 
                        name=voice_map.get(voice_opt, "id-ID-Wavenet-A")
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

                    # Jika sukses memproduksi, catat jumlah karakternya ke file drive
                    catat_pemakaian(panjang_teks)

                    st.success("✅ Berhasil! Silakan dengarkan hasilnya:")
                    st.audio(response.audio_content, format="audio/mp3")
                    
                    # --- TOMBOL DOWNLOAD EKSPLISIT ---
                    st.download_button(
                        label="⬇️ Download Hasil Audio (MP3)",
                        data=response.audio_content,
                        file_name="hasil_rekaman_studio.mp3",
                        mime="audio/mp3",
                        use_container_width=True,
                        type="primary"
                    )
                    
            except Exception as e:
                st.error(f"Gagal memproduksi suara. Detail: {e}")
        else:
            st.warning("Silakan isi naskah terlebih dahulu.")
