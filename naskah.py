import streamlit as st
import google.generativeai as genai
import os

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (DISESUAIKAN UNTUK MODE FORMULIR) ---
    DIREKTUR_PROMPT = """
[PERAN & PERSONA]
Kamu adalah Direktur Kreatif Script Alih Suara yang puitis namun teknis. Tugasmu adalah membantu pengguna menyusun naskah Text-to-Speech (TTS) yang memiliki "jiwa". Kamu menggunakan analogi untuk menjelaskan suasana dan sangat presisi dalam menghitung durasi.

[ALUR KERJA]
Pengguna sudah mengisi formulir wawancara. Berdasarkan rangkuman data yang diberikan pengguna, langsung lakukan dua langkah berikut:

1. Tahap Opsi Nuansa (Creative Pitch)
Sajikan 2-3 Pilihan Nuansa dalam tabel:
- Nuansa: Nama gaya (misal: "Zen", "Energetik", "Informatif").
- Visualisasi Suasana: Analogi puitis (misal: "Seperti embun di pagi hari").
- Rangkuman Alur: Penjelasan porsi waktu Hook-Heart-Action sesuai audiens.

2. Tahap Eksekusi (Final Script)
Sajikan SATU naskah final terbaik dari opsi nuansa yang paling relevan dengan struktur:
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
Gunakan bahasa yang inspiratif. Hindari kata-kata membosankan. Gunakan istilah industri seperti "pacing", "intonasi", dan "vocal fry" jika relevan, beri penjelasan sederhana.
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Rapat Naskah Direktur Kreatif")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {"durasi": "", "audiens": "", "vibe": "", "konteks": "", "tambahan": ""}
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1: DURASI
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 4: Target Durasi")
        pilihan = st.selectbox("Berapa detik target durasi naskah Anda?", 
                               ["Pilih...", "15 detik (Singkat / Hook)", "30 detik (Standar Iklan/Reels)", "60 detik (Edukasi / Penjelasan)", "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Masukkan durasi yang Anda inginkan (misal: 45 detik):")

        if st.button("Selanjutnya ➡️"):
            if jawaban_final and jawaban_final != "Pilih...":
                st.session_state.jawaban["durasi"] = jawaban_final
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon pilih atau isi durasi terlebih dahulu.")

    # ==========================================
    # LANGKAH 2: AUDIENS
    # ==========================================
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 4: Target Audiens")
        pilihan = st.selectbox("Siapa pendengar utama naskah ini?", 
                               ["Pilih...", "Pensiunan / Komunitas Senior (Jelas, santai, hormat)", "Profesional / Pekerja Kantoran (Formal, padat, lugas)", "Generasi Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Masukkan target audiens Anda:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_final
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi audiens terlebih dahulu.")

    # ==========================================
    # LANGKAH 3: VIBE / EMOSI
    # ==========================================
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 4: Vibe & Emosi")
        pilihan = st.selectbox("Perasaan apa yang ingin dibangun?", 
                               ["Pilih...", "Semangat & Menggebu-gebu (Energetik/Promosi)", "Tenang & Meyakinkan (Edukatif/Kesehatan)", "Santai & Menghibur (Rileks/Kasual)", "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Masukkan vibe/emosi yang Anda inginkan:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["vibe"] = jawaban_final
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi vibe terlebih dahulu.")

    # ==========================================
    # LANGKAH 4: KONTEKS
    # ==========================================
    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 4: Konteks Penggunaan")
        pilihan = st.selectbox("Naskah ini akan digunakan untuk platform apa?", 
                               ["Pilih...", "Video Edukasi Pendek (TikTok/Reels/Shorts)", "Audio Presentasi / Penjelasan Produk", "Voice Over Video YouTube", "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Masukkan konteks penggunaan Anda:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["konteks"] = jawaban_final
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi konteks terlebih dahulu.")

    # ==========================================
    # LANGKAH 5: RANGKUMAN & KOREKSI FINAL
    # ==========================================
    elif st.session_state.wizard_step == 5:
        st.subheader("📋 Koreksi Rangkuman Panduan Naskah")
        st.info("Silakan periksa dan perbaiki jika ada yang kurang pas sebelum diserahkan ke Direktur Kreatif AI.")

        # Pengguna bisa mengedit ulang di kolom ini jika mau
        edit_durasi = st.text_input("1. Target Durasi", value=st.session_state.jawaban["durasi"])
        edit_audiens = st.text_input("2. Target Audiens", value=st.session_state.jawaban["audiens"])
        edit_vibe = st.text_input("3. Vibe/Emosi", value=st.session_state.jawaban["vibe"])
        edit_konteks = st.text_input("4. Konteks Penggunaan", value=st.session_state.jawaban["konteks"])
        edit_tambahan = st.text_area("5. Catatan Tambahan (Opsional)", placeholder="Misal: Tolong wajib masukkan istilah 'Autofagi' atau 'Mocaf' di dalam naskah.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Ulangi dari Awal"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("✨ Hasilkan Naskah Sekarang", type="primary"):
                # Simpan hasil koreksi final
                st.session_state.jawaban["durasi"] = edit_durasi
                st.session_state.jawaban["audiens"] = edit_audiens
                st.session_state.jawaban["vibe"] = edit_vibe
                st.session_state.jawaban["konteks"] = edit_konteks
                st.session_state.jawaban["tambahan"] = edit_tambahan
                st.session_state.wizard_step = 6
                st.rerun()

    # ==========================================
    # LANGKAH 6: PROSES AI & HASIL
    # ==========================================
    elif st.session_state.wizard_step == 6:
        st.subheader("🎬 Hasil Naskah Direktur Kreatif")

        if not st.session_state.hasil_naskah:
            with st.spinner("Menyusun opsi nuansa dan menulis naskah final... (Tunggu sekitar 10-15 detik)"):
                try:
                    model_direktur = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=DIREKTUR_PROMPT
                    )
                    
                    # Menyusun paket data dari rangkuman untuk dikirim ke Gemini
                    prompt_final = f"""
                    Berikut adalah data panduan naskah saya:
                    - Durasi Target: {st.session_state.jawaban['durasi']}
                    - Target Audiens: {st.session_state.jawaban['audiens']}
                    - Vibe/Emosi: {st.session_state.jawaban['vibe']}
                    - Konteks Platform: {st.session_state.jawaban['konteks']}
                    - Catatan Tambahan/Kata Wajib: {st.session_state.jawaban['tambahan'] if st.session_state.jawaban['tambahan'] else "Tidak ada"}
                    
                    Tolong eksekusi pembuatan naskah sekarang sesuai alur kerjamu.
                    """
                    
                    response = model_direktur.generate_content(prompt_final)
                    st.session_state.hasil_naskah = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")
                    if st.button("Coba Lagi"):
                        st.rerun()
        else:
            # Menampilkan naskah yang sudah selesai
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Revisi Rangkuman (Buat Ulang)"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 5
                    st.rerun()
            with col2:
                if st.button("🚀 Naskah Selesai? Lanjut ke Studio Rekaman (VO)", use_container_width=True):
                    st.session_state.menu_aktif = "2. Studio Rekaman"
                    st.rerun()
