import streamlit as st
import google.generativeai as genai
from google.cloud import texttospeech
import json

# Konfigurasi Halaman
st.set_page_config(page_title="AI Voice Over Natural", page_icon="🎙️")

st.title("🎙️ Generator Suara Natural (Gemini + Google TTS)")
st.write("Ubah teks kaku menjadi suara manusia yang mengalir.")

# --- SETUP KREDENSIAL (Diambil dari Streamlit Secrets) ---
gemini_key = st.secrets["GEMINI_API_KEY"]
gcp_json = st.secrets["GCP_CREDENTIALS"] # Berupa string JSON

# Konfigurasi Gemini
genai.configure(api_key=gemini_key)

# Konfigurasi Google Cloud TTS
# Kita buat file temporer untuk kredensial agar library Google bisa membacanya
if not os.path.exists("temp_creds.json"):
    with open("temp_creds.json", "w") as f:
        f.write(gcp_json)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_creds.json"

# --- UI STREAMLIT ---
input_text = st.text_area("Masukkan teks kaku Anda di sini:", placeholder="Contoh: Selamat datang di toko kami. Kami menjual sepatu.")

if st.button("Proses Menjadi Suara"):
    if input_text:
        with st.spinner("1. Gemini sedang mengoptimasi skrip..."):
            # Logika Gemini (sama seperti skrip sebelumnya)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"Ubah teks ini jadi skrip VO natural: {input_text}")
            skrip_natural = response.text
            st.subheader("Skrip Hasil Optimasi:")
            st.info(skrip_natural)

        with st.spinner("2. Mengubah teks menjadi audio..."):
            # Logika Google TTS
            client = texttospeech.TextToSpeechClient()
            synthesis_input = texttospeech.SynthesisInput(text=skrip_natural)
            voice = texttospeech.VoiceSelectionParams(
                language_code="id-ID", name="id-ID-Neural2-A"
            )
            audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
            
            res = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
            
            # Tampilkan Player Audio di Streamlit
            st.audio(res.audio_content, format="audio/mp3")
            st.success("Selesai! Anda bisa mendengarkan atau mengunduh audio di atas.")
    else:
        st.warning("Mohon masukkan teks terlebih dahulu.")
