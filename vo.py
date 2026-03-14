import streamlit as st

def run():
    # Import HANYA dilakukan saat modul ini dipanggil
    from google.cloud import texttospeech
    from google.oauth2 import service_account
    import json

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
    st.write("Silakan *copy* naskah final dari Ruang Naskah, lalu *paste* ke kotak di bawah ini.")

    user_input = st.text_area("Masukkan Naskah Final:", height=200)

    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Pilih Jenis Suara:", ["Wanita (Neural2-A)", "Pria (Neural2-B)"])
    with col2:
        speed = st.slider("Kecepatan Bicara:", 0.5, 1.5, 1.0, 0.1)

    if st.button("🔥 Buat Suara Sekarang", use_container_width=True):
        if user_input:
            try:
                with st.spinner("Mesin Google Cloud sedang meracik suara..."):
                    client = texttospeech.TextToSpeechClient(credentials=tts_credentials)
                    
                    # Pembersihan naskah dari instruksi sutradara
                    naskah_bersih = user_input.replace("[", "").replace("]", "").replace("(", "").replace(")", "")
                    
                    synthesis_input = texttospeech.SynthesisInput(text=naskah_bersih)
                    voice_name = "id-ID-Neural2-A" if "Wanita" in gender else "id-ID-Neural2-B"
                    
                    voice = texttospeech.VoiceSelectionParams(language_code="id-ID", name=voice_name)
                    audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3, speaking_rate=speed)

                    response_audio = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)

                    st.success("✅ Berhasil! Silakan dengarkan audionya:")
                    st.audio(response_audio.audio_content, format="audio/mp3")
            except Exception as e:
                st.error(f"Gagal merekam: {e}")
        else:
            st.warning("Mohon tempelkan naskahnya terlebih dahulu.")
