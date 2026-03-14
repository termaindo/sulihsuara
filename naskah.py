import streamlit as st
import google.generativeai as genai
import os

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    # Memastikan tidak ada KTP Google Cloud TTS yang tersangkut di ruangan ini
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF ---
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

    # --- 3. SETUP KREDENSIAL GEMINI (STANDAR) ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}\nPastikan GEMINI_API_KEY sudah ada di Secrets.")
        st.stop()

    # --- 4. TAMPILAN ANTARMUKA ---
    st.title("📝 Ruang 1: Rapat Naskah Direktur Kreatif")
    st.info("💡 **Tips:** Jawab pertanyaan Direktur di bawah ini untuk memulai proses kreatif pembuatan naskah yang berjiwa.")

    # --- 5. LOGIKA CHAT AI ---
    # KUNCI PERBAIKAN 1: Naikkan ke v5 untuk mereset memori error Streamlit
    if "chat_naskah_v5" not in st.session_state:
        # KUNCI PERBAIKAN 2: Hapus 'models/' dari penulisan nama model
        model_direktur = genai.GenerativeModel(
            model_name="gemini-1.5-flash", 
            system_instruction=DIREKTUR_PROMPT
        )
        st.session_state.chat_naskah_v5 = model_direktur.start_chat(history=[])
        
        try:
            st.session_state.chat_naskah_v5.send_message("Halo Direktur, saya siap membuat naskah baru. Tolong mulai tahap wawancaranya.")
        except Exception as e:
            st.error(f"Gagal menghubungi server Gemini API. Detail: {e}")
            st.stop()

    # Menampilkan riwayat chat ke layar (kecuali pesan pancingan awal)
    if len(st.session_state.chat_naskah_v5.history) > 1:
        for message in st.session_state.chat_naskah_v5.history[1:]:
            role = "assistant" if message.role == "model" else "user"
            with st.chat_message(role):
                try:
                    st.markdown(message.parts[0].text)
                except IndexError:
                    st.markdown("*(Pesan diblokir oleh sistem keamanan AI)*")

    # Menangkap input dari pengguna
    if prompt_user := st.chat_input("Ketik jawaban atau instruksi Anda di sini..."):
        with st.chat_message("user"):
            st.markdown(prompt_user)
            
        with st.chat_message("assistant"):
            try:
                with st.spinner("Direktur sedang menyusun strategi..."):
                    response = st.session_state.chat_naskah_v5.send_message(prompt_user)
                    st.markdown(response.text)
            except Exception as e:
                st.error(f"Mohon maaf, terjadi gangguan pada komunikasi AI: {e}")

    # --- 6. TOMBOL NAVIGASI MENUJU STUDIO REKAMAN ---
    st.divider()
    if st.button("🚀 Naskah Selesai? Lanjut ke Studio Rekaman (VO)", use_container_width=True):
        st.session_state.menu_aktif = "2. Studio Rekaman"
        st.rerun()
