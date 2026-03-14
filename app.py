import streamlit as st
import google.generativeai as genai
from google.cloud import texttospeech
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Studio Sulih Suara", page_icon="🎙️", layout="wide")

# --- PROMPT DIREKTUR KREATIF (DARI PAK MUSA) ---
DIREKTUR_PROMPT = """
[PERAN & PERSONA]
Kamu adalah Direktur Kreatif Script Alih Suara yang puitis namun teknis. Tugasmu adalah membantu pengguna menyusun naskah Text-to-Speech (TTS) yang memiliki "jiwa". Kamu menggunakan analogi untuk menjelaskan suasana dan sangat presisi dalam menghitung durasi.

[ALUR KERJA WAJIB]
1. Tahap Wawancara (Discovery)
Jangan langsung menulis naskah. Sapa pengguna dan mintalah detail berikut:
- Durasi: Berapa detik targetnya?
- Audiens: Siapa pendengarnya? (Gen Z, Profesional, Anak-anak, dsb).
- Vibe/Emosi: Perasaan apa yang ingin dibangun?
- Konteks: Untuk video (tanyakan momen visual kunci) atau audio mandiri?

2. Tahap Opsi Nuansa (Creative Pitch)
Sajikan 2-3 Pilihan Nuansa dalam tabel:
- Nuansa: Nama gaya (misal: "Zen", "Energetik").
- Visualisasi Suasana: Analogi puitis (misal: "Seperti embun di pagi hari").
- Rangkuman Alur: Penjelasan porsi waktu Hook-Heart-Action sesuai audiens.

3. Tahap Eksekusi (Final Script)
Setelah pengguna memilih nuansa, sajikan output dengan struktur:
### 🎙️ [Judul Proyek]
- Tabel Metadata: Target Durasi, Laju Bicara, dan Jumlah Kata Aktual.
- Tabel Identitas Suara: Persona & Suasana.
- Tabel Perbandingan Ritme: Bandingkan versi Tight Sync (Pas) dan Breathable (Longgar).
- Blok Kode Naskah: Gunakan tag [Jeda: 0.0s] dan (Instruksi Emosi).
- Catatan Sutradara: Rekomendasi Pitch/Speed TTS dan Atmosfer Audio (Musik/SFX).

[LOGIKA TEKNIS DURASI]
Gunakan referensi berikut untuk menghitung batas kata:
1) Bahasa Indonesia: 
a) Gaya cepat: 2,6 - 2,8 wps
b) Gaya normal: 2.1 - 2.3 wps
2) Bahasa Inggris:
a) Gaya cepat: 2.9 - 3.2 wps
b) Gaya normal: 2.4 - 2.6 wps
(wps = words per second).

[GAYA BAHASA]
Gunakan bahasa yang inspiratif. Hindari kata-kata membosankan. Gunakan istilah industri seperti "pacing", "intonasi", dan "vocal fry" jika relevan, dan beri penjelasan sederhana dan singkat untuk istilah teknis tersebut, supaya bisa dipahami juga oleh orang awam pemakai jasamu.
"""

# --- SETUP KREDENSIAL ---
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    gcp_json_string = st.secrets["GCP_CREDENTIALS"]

    genai.configure(api_key=gemini_key)

    if not os.path.exists("google_creds.json"):
        with open("google_creds.json", "w", encoding="utf-8") as f:
            f.write(gcp_json_string)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"
except Exception as e:
    st.error("Error Kredensial. Cek Secrets Anda.")
    st.stop()

# --- TAMPILAN ANTARMUKA ---
st.title("🎙️ Studio Sulih Suara AI")
st.markdown("Bersama Direktur Kreatif Naskah & Mesin Suara Neural2")

# Membuat 2 Tab
tab1, tab2 = st.tabs(["📝 Ruang 1: Rapat Naskah (Chat)", "🎧 Ruang 2: Studio Rekaman (TTS)"])

# ==========================================
# TAB 1: RUANG RAPAT DIREKTUR KREATIF
# ==========================================
with tab1:
    st.info("💡 **Tips:** Jawab pertanyaan Direktur di bawah ini untuk memulai proses kreatif.")
    
    # Inisialisasi sesi obrolan (Chat Session)
    if "chat_session" not in st.session_state:
        model_direktur = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=DIREKTUR_PROMPT
        )
        # Memulai chat kosong
        st.session_state.chat_session = model_direktur.start_chat(history=[])
        
        # Pancingan agar Direktur menyapa duluan
        sapaan_awal = st.session_state.chat_session.send_message("Halo Direktur, saya siap membuat naskah baru. Tolong mulai tahap wawancaranya.")
    
    # Menampilkan riwayat chat
    for message in st.session_state.chat_session.history[1:]: # Skip pesan pancingan sistem
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # Kotak Input Chat
    if prompt_user := st.chat_input("Ketik jawaban atau instruksi Anda di sini..."):
        # Tampilkan chat user
        with st.chat_message("user"):
            st.markdown(prompt_user)
        # Kirim ke Gemini dan tampilkan balasan
        with st.chat_message("assistant"):
            response = st.session_state.chat_session.send_message(prompt_user)
            st.markdown(response.text)

# ==========================================
# TAB 2: STUDIO REKAMAN
# ==========================================
with tab2:
    st.write("Silakan *copy* blok naskah final dari Ruang 1, dan *paste* di sini untuk diubah menjadi suara.")
    
    user_input = st.text_area("Masukkan Naskah Final:", height=200)

    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Pilih Jenis Suara:", ["Wanita (Neural2-A)", "Pria (Neural2-B)"])
    with col2:
        speed = st.slider("Kecepatan Bicara:", 0.5, 1.5, 1.0, 0.1)

    if st.button("🔥 Buat Suara Sekarang", use_container_width=True):
        if user_input:
            try:
                with st.spinner("Google Cloud sedang memproduksi suara..."):
                    client = texttospeech.TextToSpeechClient()
                    # Membersihkan tag [Jeda] atau (Emosi) agar tidak ikut terbaca oleh robot
                    naskah_bersih = user_input.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
                    
                    synthesis_input = texttospeech.SynthesisInput(text=naskah_bersih)
                    voice_name = "id-ID-Neural2-A" if "Wanita" in gender else "id-ID-Neural2-B"
                    
                    voice = texttospeech.VoiceSelectionParams(language_code="id-ID", name=voice_name)
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed)

                    response_audio = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

                    st.success("Berhasil! Silakan dengarkan:")
                    st.audio(response_audio.audio_content, format="audio/mp3")
            except Exception as e:
                st.error(f"Gagal merekam: {e}")
        else:
            st.warning("Mohon tempelkan naskahnya dulu ya.")
