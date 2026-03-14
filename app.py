import streamlit as st
import google.generativeai as genai
from google.cloud import texttospeech
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="AI Voice Over Natural", page_icon="🎙️", layout="centered")

st.title("🎙️ AI Voice Over Natural")
st.write("Mengubah teks kaku menjadi suara manusia yang mengalir menggunakan **Gemini** dan **Google Cloud TTS**.")

# --- SETUP KREDENSIAL (SECRETS) ---
try:
    gemini_key = st.secrets["GEMINI_API_KEY"]
    gcp_json_string = st.secrets["GCP_CREDENTIALS"]

    # Konfigurasi Gemini
    genai.configure(api_key=gemini_key)

    # Konfigurasi Google Cloud (Menyimpan JSON ke file sementara)
    if not os.path.exists("google_creds.json"):
        with open("google_creds.json", "w", encoding="utf-8") as f:
            f.write(gcp_json_string)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google_creds.json"
    
except Exception as e:
    st.error("Waduh! Sepertinya ada masalah di bagian 'Secrets'. Pastikan Anda sudah memasukkan GEMINI_API_KEY dan GCP_CREDENTIALS di pengaturan Streamlit Cloud.")
    st.stop()

# --- INTERFACE APLIKASI ---
st.divider()

user_input = st.text_area("Masukkan teks kaku (artikel/naskah):", 
                         placeholder="Contoh: Selamat pagi. Silakan baca ebook saya tentang kesehatan.",
                         height=150)

col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Pilih Jenis Suara:", ["Wanita (Neural2-A)", "Pria (Neural2-B)"])
with col2:
    speed = st.slider("Kecepatan Bicara:", 0.5, 1.5, 1.0, 0.1)

if st.button("🔥 Proses & Buat Suara", use_container_width=True):
    if user_input:
        try:
            # 1. Optimasi Teks dengan Gemini
            with st.spinner("Gemini sedang merangkai kata agar lebih natural..."):
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="Ubah teks input menjadi skrip voice over Bahasa Indonesia yang sangat natural, manusiawi, dan mengalir. Gunakan jeda (...) dan bahasa tutur yang tidak kaku. HANYA berikan skrip finalnya saja tanpa penjelasan tambahan."
                )
                response = model.generate_content(user_input)
                skrip_final = response.text.strip()
                
                st.subheader("Skrip Hasil Optimasi:")
                st.info(skrip_final)

            # 2. Kirim ke Google Cloud TTS
            with st.spinner("Google Cloud sedang mengisi suara..."):
                client = texttospeech.TextToSpeechClient()
                synthesis_input = texttospeech.SynthesisInput(text=skrip_final)
                
                voice_name = "id-ID-Neural2-A" if "Wanita" in gender else "id-ID-Neural2-B"
                voice = texttospeech.VoiceSelectionParams(
                    language_code="id-ID",
                    name=voice_name
                )

                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=speed
                )

                response_audio = client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )

                # 3. Tampilkan Player Audio
                st.success("Berhasil! Silakan dengarkan hasilnya di bawah ini:")
                st.audio(response_audio.audio_content, format="audio/mp3")
                
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses suara: {e}")
    else:
        st.warning("Mohon isi teksnya dulu ya, Pak.")
