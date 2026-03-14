import streamlit as st

def run():
    # Import HANYA dilakukan saat modul ini dipanggil
    import google.generativeai as genai
    import os

    # --- KARANTINA SISTEM ---
    # 1. Hapus memori KTP Google Cloud TTS agar tidak dibaca Gemini
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        del os.environ["GOOGLE_APPLICATION_CREDENTIALS"]

    # --- PROMPT DIREKTUR KREATIF ---
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
    - Nuansa: Nama gaya (misal: "Zen", "Energetik", "Informatif", "Rileks").
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

    # --- SETUP KREDENSIAL GEMINI (ISOLASI TOTAL) ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        
        # Paksa Gemini menggunakan jalur REST dan tetapkan API Key di environment
        os.environ["GOOGLE_API_KEY"] = gemini_key
        genai.configure(api_key=gemini_key, transport="rest")
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Rapat Naskah Direktur Kreatif")
    st.info("💡 **Tips:** Jawab pertanyaan Direktur di bawah ini.")

    # KUNCI PERBAIKAN: Hapus prefix 'models/' dan gunakan v3 untuk memori bersih
    if "chat_session_naskah_v3" not in st.session_state:
        model_direktur = genai.GenerativeModel(
            model_name="gemini-1.5-flash", # Penulisan standar yang benar
            system_instruction=DIREKTUR_PROMPT
        )
        st.session_state.chat_session_naskah_v3 = model_direktur.start_chat(history=[])
        st.session_state.chat_session_naskah_v3.send_message("Halo Direktur, saya siap membuat naskah baru. Tolong mulai tahap wawancaranya.")

    for message in st.session_state.chat_session_naskah_v3.history[1:]:
        role = "assistant" if message.role == "model" else "user"
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    if prompt_user := st.chat_input("Ketik instruksi/jawaban Anda di sini..."):
        with st.chat_message("user"):
            st.markdown(prompt_user)
        with st.chat_message("assistant"):
            try:
                response = st.session_state.chat_session_naskah_v3.send_message(prompt_user)
                st.markdown(response.text)
            except Exception as e:
                st.error(f"Error AI: {e}")

    # TOMBOL LANJUTAN MENUJU STUDIO REKAMAN
    st.divider()
    if st.button("🚀 Naskah Selesai? Lanjut ke Studio Rekaman (VO)", use_container_width=True):
        st.session_state.menu_aktif = "2. Studio Rekaman"
        st.rerun()
