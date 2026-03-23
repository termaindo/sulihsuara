import streamlit as st
import google.generativeai as genai
import os
import re

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI PENAJAMAN COPYWRITING & MODULAR) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif, Scriptwriter, dan Ahli Copywriting Profesional. Kamu sangat ahli menyusun naskah berjiwa, memikat, dan natural dengan gaya bahasa komunitas UMKM yang hangat dan persuasif.

[ALUR KERJA]
Berdasarkan data wawancara pengguna, susunlah output ke dalam 3 bagian utama berikut:

1. 💡 Alasan Kreatif & Strategi:
Jelaskan secara singkat dengan bahasa awam yang ramah, mengapa pendekatan naskah ini digunakan (misal: menggunakan formula Problem-Agitate-Solution untuk menyentuh masalah pembaca dulu, atau formula AIDA).

2. 🎛️ Arahan Rekaman / Publikasi:
Berikan panduan tone suara, emosi, atau gaya visual yang paling cocok untuk naskah ini.

3. 🎙️ Naskah Final (Di dalam Kotak Kode):
Kamu WAJIB membungkus naskah di dalam kotak kode (markdown code block) dengan awalan ```text dan akhiran ```.
Di dalam kotak kode tersebut, bagilah naskah menjadi blok-blok modular agar siap pakai di berbagai format:

- [Hook / Judul Pemikat]: 1-2 kalimat super pendek yang langsung memancing rasa penasaran atau menyentuh masalah (pain point) audiens.
- [Naskah Utama]: Ditulis dengan gaya bahasa lisan (bertutur), natural, hangat, akrab, dan menghindari singkatan/simbol aneh. Terapkan formula PAS (Problem-Agitate-Solution) atau AIDA. JANGAN langsung berjualan di kalimat pertama!
   * KHUSUS AUDIO/VIDEO: Jika tujuannya untuk suara, gunakan tag SSML (<speak>, <break time="400ms"/>, <prosody pitch="+1st" rate="1.1">) untuk mengatur intonasi.
   * KHUSUS NON-AUDIO: Jika bukan untuk suara, DILARANG KERAS memakai tag SSML. Gunakan bahasa copywriting biasa.
- [Poin Infografis]: Rangkuman inti dari naskah di atas ke dalam poin-poin (bullet points) yang SANGAT PADAT (maksimal 3-5 kata per poin) khusus untuk kebutuhan visual slide.
- [Objek Visual Aman]: WAJIB berikan 1 kalimat deskripsi fisik kemasan produk dalam Bahasa Inggris sebagai murni benda mati (contoh: "A minimalist pump bottle of liquid soap on a bathroom sink with green leaves"). DILARANG KERAS menyebutkan efeknya pada kulit, tubuh, atau kesehatan.
- [Call to Action / Ajakan Bertindak]: WAJIB selalu ditutup dengan kalimat ajakan baku ini persis tanpa diubah: "Dapatkan produk berkualitas ini sekarang juga di ktbukm-jatim.store"

ATURAN MUTLAK:
- Selalu gunakan sapaan yang sopan, hangat, dan mengundang kedekatan (relatable) khas komunitas.
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Studio Kreasi Naskah")
    
    # Blok informasi pengantar fungsi studio (Paten)
    st.info("💡 **Informasi:** Studio ini adalah titik awal produksi Anda. Di sini, Kecerdasan Buatan (AI) bertindak sebagai Direktur Kreatif yang akan membantu Anda menyusun naskah, skrip, atau *copywriting* profesional hanya dengan menjawab beberapa pertanyaan sederhana. Hasil dari studio ini akan otomatis tersambung ke studio lainnya.")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {
            "produk": "", 
            "poin_penting": "", 
            "tujuan": "",
            "durasi": "", 
            "audiens": "", 
            "vibe": "", 
            "konteks": "", 
            "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1: PRODUK / JASA (DAFTAR PATEN)
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", 
                                "1. Aplikasi Kesehatan - Konsultan Puasa IF", 
                                "2. Aplikasi Pintar Saham - Konsultan Saham Indonesia", 
                                "3. Produk Kesehatan & Perawatan Pribadi", 
                                "4. Produk Makanan, Minuman & Suplemen", 
                                "5. Layanan / Jasa Komunitas", 
                                "6. Barang Elektronik / Gadget", 
                                "7. Acara / Webinar",
                                "8. Isi Sendiri ..."])
        
        jawaban_final = pilihan
        if pilihan == "8. Isi Sendiri ...":
            jawaban_final = st.text_input("Sebutkan produk atau jasa Anda:")

        if st.button("Selanjutnya ➡️"):
            if jawaban_final and jawaban_final != "Pilih...":
                st.session_state.jawaban["produk"] = jawaban_final
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon pilih atau isi produk/jasa terlebih dahulu.")

    # ==========================================
    # LANGKAH 2: POIN PENTING / KEUNGGULAN (DAFTAR PATEN)
    # ==========================================
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", 
                               ["Pilih...", 
                                "Aplikasi Kesehatan: i) IF Aman: Pola puasa yang disesuaikan usia, jenis kelamin, gemuk kurusnya badan (BMI), dan riwayat kesehatan (Maag, Diabetes, Jantung, dll). ii) Nutrisi Cerdas: Rekomendasi makanan & suplemen sesuai profil alergi Anda. iii) Olahraga Terukur: Panduan detak jantung agar latihan efektif dan bebas risiko fatal. iv) Laporan Instan: Download rangkuman kesehatan Anda dalam format PDF.",
                                "Aplikasi Pintar Saham: i) 6 Modul Analisa Premium: Dari Teknikal Pro hingga Kalkulator Dividen. ii) Screening Otomatis: Temukan saham undervalued dalam hitungan detik. iii) Risk Management: Fitur Stop Loss & Target Price otomatis di setiap analisa. iv) Data Real-Time: Akses langsung ke data pasar Bursa Efek Indonesia. v) Laporan PDF: Hasil analisa bisa didownload dalam bentuk PDF.",
                                "Manfaat kesehatan & bahan alami yang digunakan", 
                                "Promo diskon terbatas & harga spesial", 
                                "Solusi praktis untuk masalah sehari-hari", 
                                "Ajakan bergabung ke komunitas / acara",
                                "Isi Sendiri ..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi Sendiri ...":
            jawaban_final = st.text_area("Tuliskan poin penting/keunggulan produk Anda:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["poin_penting"] = jawaban_final
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi poin penting terlebih dahulu.")

    # ==========================================
    # LANGKAH 3: TUJUAN & DURASI (DINAMIS PATEN)
    # ==========================================
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Tujuan & Target Panjang/Durasi")
        
        pilihan_tujuan = st.selectbox("Apa tujuan pembuatan naskah ini?", 
                               ["Pilih...", 
                                "Teks Copywriting / Naskah Iklan / Promosi", 
                                "Naskah Rekaman Audio", 
                                "Naskah Suara Penjelasan di Video",
                                "Teks Infografis / Presentasi Visual", 
                                "Isi Sendiri ..."])
        
        jawaban_tujuan = pilihan_tujuan
        if pilihan_tujuan == "Isi Sendiri ...":
            jawaban_tujuan = st.text_input("Sebutkan tujuan pembuatan naskah Anda:")

        st.markdown("<br>", unsafe_allow_html=True) 

        # --- LOGIKA DROPDOWN DINAMIS BERDASARKAN TUJUAN ---
        opsi_durasi = ["Pilih..."]
        
        if jawaban_tujuan != "Pilih...":
            if "Audio" in jawaban_tujuan or "Video" in jawaban_tujuan:
                opsi_durasi.extend(["15 detik (Singkat / Iklan Cepat)", "30 detik (Standar Iklan/Reels)", "60 detik (Edukasi / Penjelasan Lengkap)", "Isi Sendiri ..."])
            elif "Copywriting" in jawaban_tujuan or "Iklan" in jawaban_tujuan:
                opsi_durasi.extend(["1 Paragraf Singkat (Caption IG/WA/Tiktok)", "2-3 Paragraf (Email/Brosur/Artikel Pendek)", "Maksimal 500 Kata (Detail Lengkap)", "Isi Sendiri ..."])
            elif "Infografis" in jawaban_tujuan or "Visual" in jawaban_tujuan:
                opsi_durasi.extend(["1 Slide Penuh (Poster Tunggal)", "3 Slide (Carousel Singkat)", "5 Slide (Carousel Standar)", "7-10 Slide (Carousel Maksimal)", "Isi Sendiri ..."])
            else:
                opsi_durasi.extend(["Pendek", "Sedang", "Panjang", "Isi Sendiri ..."]) # Fallback jika isi sendiri tidak terbaca kata kuncinya

        pilihan_durasi = st.selectbox("Berapa panjang atau target durasi/ukuran naskah Anda?", opsi_durasi)
        
        jawaban_durasi = pilihan_durasi
        if pilihan_durasi == "Isi Sendiri ...":
            jawaban_durasi = st.text_input("Masukkan target ukuran naskah Anda secara spesifik:")
            
            # --- LOGIKA PEMBATASAN DURASI WAKTU (HARD CAP 180 DETIK) ---
            if jawaban_durasi:
                angka_ditemukan = re.findall(r'\d+', jawaban_durasi)
                if angka_ditemukan:
                    nilai_angka = int(angka_ditemukan[0])
                    teks_kecil = jawaban_durasi.lower()
                    
                    if "jam" in teks_kecil:
                        total_detik = nilai_angka * 3600
                    elif "menit" in teks_kecil:
                        total_detik = nilai_angka * 60
                    elif "detik" in teks_kecil:
                        total_detik = nilai_angka
                    else:
                        total_detik = 0 
                    
                    if total_detik > 180:
                        st.warning("⏳ **Perhatian:** Maksimal target durasi adalah **180 detik (3 menit)** untuk menjaga kualitas naskah. Isian Anda otomatis dikunci ke batas maksimal tersebut.")
                        jawaban_durasi = "180 detik (Batas maksimal)"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_tujuan and jawaban_durasi and jawaban_tujuan != "Pilih..." and jawaban_durasi != "Pilih...":
                    st.session_state.jawaban["tujuan"] = jawaban_tujuan
                    st.session_state.jawaban["durasi"] = jawaban_durasi
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi tujuan dan durasi terlebih dahulu.")

    # ==========================================
    # LANGKAH 4: AUDIENS & VIBE
    # ==========================================
    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Audiens & Suasana")
        pilihan_audiens = st.selectbox("Untuk siapa pendengar atau pembaca dari naskah ini?", 
                               ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi Sendiri ..."])
        
        jawaban_audiens = pilihan_audiens
        if pilihan_audiens == "Isi Sendiri ...":
            jawaban_audiens = st.text_input("Masukkan target audiens Anda:")

        pilihan_vibe = st.selectbox("Perasaan apa yang ingin dibangun?", 
                               ["Pilih...", "Semangat & Menggebu-gebu (Promosi)", "Tenang & Meyakinkan (Kesehatan/Edukasi)", "Santai & Menghibur (Kasual)", "Isi Sendiri ..."])
        
        jawaban_vibe = pilihan_vibe
        if pilihan_vibe == "Isi Sendiri ...":
            jawaban_vibe = st.text_input("Masukkan vibe/emosi yang Anda inginkan:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_audiens and jawaban_vibe and jawaban_audiens != "Pilih..." and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi audiens dan suasana terlebih dahulu.")

    # ==========================================
    # LANGKAH 5: KONTEKS & RANGKUMAN FINAL
    # ==========================================
    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Konteks & Koreksi")
        
        pilihan_konteks = st.selectbox("Naskah ini akan digunakan untuk platform apa?", 
                               ["Pilih...", 
                                "Video Pendek (TikTok / Reels / Shorts)", 
                                "Voice Over Video YouTube", 
                                "Audio Presentasi / Komunitas", 
                                "Pesan Teks (WhatsApp / Telegram / Threads)",
                                "Caption Media Sosial (Instagram / Facebook / TikTok)",
                                "Postingan Infografis (Feed / Carousel Instagram / LinkedIn)",
                                "Isi Sendiri ..."])
        
        jawaban_konteks = pilihan_konteks
        if pilihan_konteks == "Isi Sendiri ...":
            jawaban_konteks = st.text_input("Masukkan platform tujuan Anda:")

        st.divider()
        st.info("📋 **Periksa Kembali Panduan Naskah Anda:**\nSilakan edit langsung di dalam kotak jika ada yang ingin diubah sebelum diserahkan ke Direktur Kreatif.")

        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""))
        edit_poin = st.text_area("2. Poin Penting", value=st.session_state.jawaban.get("poin_penting", ""))
        edit_tujuan = st.text_input("3. Tujuan Naskah", value=st.session_state.jawaban.get("tujuan", ""))
        
        edit_durasi = st.text_input("4. Target Panjang/Durasi", value=st.session_state.jawaban.get("durasi", ""))
        if edit_durasi:
            angka_ditemukan = re.findall(r'\d+', edit_durasi)
            if angka_ditemukan:
                nilai_angka = int(angka_ditemukan[0])
                teks_kecil = edit_durasi.lower()
                
                if "jam" in teks_kecil:
                    total_detik = nilai_angka * 3600
                elif "menit" in teks_kecil:
                    total_detik = nilai_angka * 60
                elif "detik" in teks_kecil:
                    total_detik = nilai_angka
                else:
                    total_detik = 0
                
                if total_detik > 180:
                    st.warning("⏳ **Perhatian:** Maksimal target durasi adalah **180 detik (3 menit)**. Sistem akan menggunakan batas maksimal tersebut untuk naskah Anda.")
                    edit_durasi = "180 detik (Batas maksimal)"

        edit_audiens = st.text_input("5. Target Audiens", value=st.session_state.jawaban.get("audiens", ""))
        edit_vibe = st.text_input("6. Suasana", value=st.session_state.jawaban.get("vibe", ""))
        edit_tambahan = st.text_area("Catatan Tambahan (Opsional)", placeholder="Misal: Wajib sebutkan kata 'Autofagi'.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("✨ Hasilkan Naskah Berjiwa", type="primary"):
                if jawaban_konteks and jawaban_konteks != "Pilih...":
                    st.session_state.jawaban["konteks"] = jawaban_konteks
                    st.session_state.jawaban["produk"] = edit_produk
                    st.session_state.jawaban["poin_penting"] = edit_poin
                    st.session_state.jawaban["tujuan"] = edit_tujuan
                    st.session_state.jawaban["durasi"] = edit_durasi
                    st.session_state.jawaban["audiens"] = edit_audiens
                    st.session_state.jawaban["vibe"] = edit_vibe
                    st.session_state.jawaban["tambahan"] = edit_tambahan
                    st.session_state.wizard_step = 6
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi konteks platform terlebih dahulu.")

    # ==========================================
    # LANGKAH 6: PROSES AI & HASIL
    # ==========================================
    elif st.session_state.wizard_step == 6:
        st.subheader("🎬 Hasil Naskah Pro")

        if not st.session_state.hasil_naskah:
            if "Threads" in st.session_state.jawaban['konteks']:
                st.info("💡 **Info Batasan:** Karena Anda memilih platform Pesan Teks (termasuk Threads), sistem membatasi panjang naskah final maksimal **500 karakter** agar dapat diposting tanpa terpotong.")
            elif "Infografis" in st.session_state.jawaban['tujuan'] or "Infografis" in st.session_state.jawaban['konteks']:
                st.info("💡 **Info Format:** Karena Anda memilih pembuatan Infografis, AI akan secara otomatis memformat teks menjadi poin-poin padat (bullet points/slide) yang siap disalin ke desain Anda.")
                
            with st.spinner("Direktur sedang menyusun naskah yang natural dan berjiwa..."):
                try:
                    model_direktur = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=DIREKTUR_PROMPT
                    )
                    
                    instruksi_tambahan_platform = ""
                    if "Threads" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Karena platform mencakup Threads, PANJANG NASKAH FINAL DI DALAM KOTAK KODE TIDAK BOLEH LEBIH DARI 500 KARAKTER (termasuk spasi)!"
                    elif "Infografis" in st.session_state.jawaban['tujuan'] or "Infografis" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Ini adalah teks untuk INFOGRAFIS/PRESENTASI VISUAL. Buat naskah yang sangat terstruktur, gunakan BULLET POINTS atau penomoran slide (Slide 1, Slide 2, dst). Gunakan kalimat yang SUPER PADAT, JELAS, dan HINDARI paragraf panjang naratif. Fokus pada data dan *punchline*. HINDARI SSML SAMA SEKALI."

                    prompt_final = f"""
                    Tolong buatkan naskah berdasarkan panduan berikut:
                    - Produk/Jasa: {st.session_state.jawaban['produk']}
                    - Poin Penting/Keunggulan: {st.session_state.jawaban['poin_penting']}
                    - Tujuan Pembuatan Naskah: {st.session_state.jawaban['tujuan']}
                    - Durasi Target: {st.session_state.jawaban['durasi']}
                    - Target Audiens/Pembaca: {st.session_state.jawaban['audiens']}
                    - Vibe/Emosi: {st.session_state.jawaban['vibe']}
                    - Konteks Platform: {st.session_state.jawaban['konteks']} {instruksi_tambahan_platform}
                    - Catatan Tambahan: {st.session_state.jawaban['tambahan'] if st.session_state.jawaban['tambahan'] else "Tidak ada"}
                    """
                    
                    response = model_direktur.generate_content(prompt_final)
                    st.session_state.hasil_naskah = response.text
                    st.rerun()
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")
                    if st.button("Coba Lagi"):
                        st.rerun()
        else:
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            st.info("💡 **Catatan:** Sistem kami akan otomatis menarik naskah di dalam kotak hitam di atas saat Anda berpindah ruangan. Naskah ini kini sudah terstruktur dan siap digunakan! Silakan pilih langkah selanjutnya:")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔄 Buat Naskah Baru"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col2:
                if st.button("🎨 Ke Studio Kreasi Cetak / Visual", use_container_width=True):
                    st.session_state.menu_aktif = "3. Studio Kreasi Cetak / Visual"
                    st.rerun()
            with col3:
                if st.button("🚀 Ke Studio Kreasi Suara / Audio", use_container_width=True):
                    st.session_state.menu_aktif = "2. Studio Kreasi Suara / Audio"
                    st.rerun()
