import streamlit as st
import google.generativeai as genai
import os
import re

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI NATURAL & AWAM) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif Script dan Copywriting. Tugasmu adalah menyusun naskah yang terdengar natural, berjiwa, dan tidak kaku, yang juga dioptimalkan JIKA dibaca oleh mesin AI (Text-to-Speech).

[ALUR KERJA]
Berdasarkan data wawancara pengguna, susunlah output sebagai berikut:

1. 💡 Penjelasan Singkat:
Jelaskan dengan bahasa yang SANGAT SEDERHANA (bahasa awam yang ramah) mengapa naskah ini dibuat seperti ini. Hindari sama sekali istilah teknis industri, kode pemrograman, atau kata-kata rumit.

2. 🎛️ Arahan Rekaman / Publikasi:
Berikan panduan sederhana mengenai tone dan suasana (misal: "Gunakan suara Wanita dengan kecepatan sedang" atau "Gunakan banyak emoji jika ini untuk caption media sosial").

3. 🎙️ Naskah Final:
Kamu WAJIB membungkus naskah di dalam kotak kode (markdown code block) dengan format ```text ... ```.
PENTING UNTUK RITME MESIN & KETERBACAAN:
- Sesuaikan gaya bahasa dengan Platform (Konteks) yang dipilih pengguna. Jika untuk Caption IG/WA, buat semenarik mungkin untuk dibaca. Jika untuk Video/YouTube, buat senatural mungkin untuk didengar.
- DILARANG menggunakan kode SSML, tanda kurung (), atau kurung siku [] yang berisi instruksi emosi di dalam naskah. Naskah harus berisi murni kata-kata.
- Gunakan TANDA BACA biasa secara cerdas untuk mengatur ritme.
- Gunakan tanda koma (,) untuk jeda napas pendek.
- Gunakan tanda titik (.) untuk jeda napas panjang atau di akhir kalimat.
- Tuliskan angka menjadi kata-kata jika perlu (misal "Rp 10.000" menjadi "sepuluh ribu rupiah") agar mesin tidak salah baca jika dijadikan Voice Over.

PENTING: Pastikan teks di dalam kotak naskah final benar-benar bersih, rapi, dan siap digunakan.
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
        st.session_state.jawaban = {
            "produk": "", 
            "merk": "",             
            "jenis_spesifik": "",   
            "poin_penting": "", 
            "audiens": "", 
            "vibe": "", 
            "tujuan": "",
            "konteks": "", 
            "durasi": "", 
            "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1: PRODUK / JASA
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", 
                                "Aplikasi Sehat - Konsultan IF",
                                "Aplikasi Expert Stock Pro - Konsultan Saham Indonesia",
                                "Produk Kesehatan & Perawatan Pribadi", 
                                "Makanan, Minuman & Suplemen", 
                                "Layanan / Jasa Komunitas", 
                                "Barang Elektronik / Gadget", 
                                "Acara / Webinar",
                                "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            if "produk_custom_1" not in st.session_state:
                st.session_state.produk_custom_1 = ""
            jawaban_final = st.text_input("Sebutkan produk atau jasa Anda secara spesifik:", key="produk_custom_1")

        if st.button("Selanjutnya ➡️"):
            if jawaban_final and jawaban_final != "Pilih...":
                st.session_state.jawaban["produk"] = jawaban_final
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon pilih atau isi produk/jasa terlebih dahulu.")

    # ==========================================
    # LANGKAH 2: POIN PENTING / KEUNGGULAN
    # ==========================================
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        
        produk_terpilih = st.session_state.jawaban.get("produk", "")
        
        kategori_umum = [
            "Produk Kesehatan & Perawatan Pribadi", 
            "Makanan, Minuman & Suplemen", 
            "Layanan / Jasa Komunitas", 
            "Barang Elektronik / Gadget", 
            "Acara / Webinar"
        ]

        merk_input = ""
        jenis_input = ""
        
        # 1. Menampilkan input Merk & Jenis jika memilih kategori umum
        if produk_terpilih in kategori_umum:
            st.info(f"💡 Anda memilih kategori umum **{produk_terpilih}**. Mohon lengkapi detail berikut:")
            if "merk_input_2" not in st.session_state:
                st.session_state.merk_input_2 = st.session_state.jawaban.get("merk", "")
            if "jenis_input_2" not in st.session_state:
                st.session_state.jenis_input_2 = st.session_state.jawaban.get("jenis_spesifik", "")
                
            merk_input = st.text_input("Apa Merk / Brand produk Anda?", key="merk_input_2")
            jenis_input = st.text_input("Apa jenis produk / jasa Anda secara spesifik?", placeholder="Misal: Sabun Cair Alami, Jasa Bersih AC, dll", key="jenis_input_2")
            st.markdown("<br>", unsafe_allow_html=True)

        # 2. Logika Opsi Dropdown Dinamis Berdasarkan Produk
        opsi_keunggulan = ["Pilih..."]
        
        if produk_terpilih == "Aplikasi Sehat - Konsultan IF":
            opsi_keunggulan.extend([
                "Rekomendasi Pola Puasa IF: Memakai usia, jenis kelamin, gemuk kurusnya tubuh (BMI), dan riwayat kesehatan untuk mendeteksi & menyarankan pola puasa intermiten yang aman & menyehatkan.",
                "Rekomendasi Nutrisi Cerdas: Menyusunkan pola nutrisi yang perlu diterapkan sesuai kondisi pribadi, termasuk riwayat alergi, serta suplemen/superfood apa yang cocok dan mana yang harus dihindari berdasarkan riwayat medis Anda.",
                "Rekomendasi Olahraga Personal: Memakai riwayat kesehatan untuk merekomendasi pola Olahraga yang sesuai, termasuk angka detak jantung yang perlu dipantau ketika berolahraga, sesuai dengan kondisi pribadi Anda, sehingga tidak berakibat fatal."
            ])
        elif produk_terpilih == "Aplikasi Expert Stock Pro - Konsultan Saham Indonesia":
            opsi_keunggulan.extend([
                "Screening Saham Harian Pro (Audio Alert), yang tersedia dalam 2 mode: Day Trade dan Swing Trade, lengkap dengan Trading Plan (Entry, SL & TP).",
                "Analisa Cepat Pro, menyajikan ringkasan analisa Fundamental & Teknikal, lengkap dengan rekomendasi BUY/HOLD/SELL, Target Price, dan Stop Loss dalam satu kali jalan.",
                "Analisa Teknikal Pro, menyajikan Analisa Teknikal yang dipakai oleh para trader profesional, lengkap dengan Trading Plan (SL & TP) dihitung otomatis menggunakan volatilitas dinamis (ATR), sesuai scoring analisa teknikal yang menyeluruh plus analisa berita terbaru, agar tidak mudah kena \"gocek\".",
                "Analisa Fundamental Pro, menganalisa kesehatan perusahaan, dan valuasi wajar sesuai 3 pendekatan: Rata-rata PBV 5 tahun, Rata-rata PER 5 tahun, dan Graham Number, serta tren laba 4 tahun terakhir, dan analisa berita ter-update, sebelum Anda berinvestasi jangka panjang.",
                "Analisa Dividen Pro, mengecek kesehatan perusahaan, apakah dividen dibayar menggunakan uang tunai (Free Cash Flow) atau utang, termasuk riwayat 5 tahun pemberian dividennya.",
                "Perbandingan Antar 2 Saham Pro, membantu memutuskan mana saham yang secara teknikal maupun fundamental, lebih patut untuk Anda beli."
            ])
        else:
            opsi_keunggulan.extend([
                "Manfaat kesehatan & bahan alami yang digunakan", 
                "Promo diskon terbatas & harga spesial", 
                "Solusi praktis untuk masalah sehari-hari", 
                "Ajakan bergabung ke komunitas / acara"
            ])
            
        opsi_keunggulan.append("Isi sendiri...")

        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", opsi_keunggulan)
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            if "poin_custom_2" not in st.session_state:
                st.session_state.poin_custom_2 = ""
            jawaban_final = st.text_area("Tuliskan poin penting/keunggulan produk Anda:", key="poin_custom_2")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if produk_terpilih in kategori_umum and (not merk_input.strip() or not jenis_input.strip()):
                    st.warning("⚠️ Mohon isi Merk/Brand dan Jenis Spesifik terlebih dahulu.")
                elif jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["merk"] = merk_input
                    st.session_state.jawaban["jenis_spesifik"] = jenis_input
                    st.session_state.jawaban["poin_penting"] = jawaban_final
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("⚠️ Mohon pilih atau isi poin penting terlebih dahulu.")

    # ==========================================
    # LANGKAH 3: AUDIENS & VIBE (Dahulu Langkah 4)
    # ==========================================
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Target Audiens & Suasana")
        
        pilihan_audiens = st.selectbox("Untuk siapa pendengar atau pembaca dari naskah ini?", 
                               ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi sendiri..."])
        
        jawaban_audiens = pilihan_audiens
        if pilihan_audiens == "Isi sendiri...":
            if "audiens_custom_3" not in st.session_state:
                st.session_state.audiens_custom_3 = ""
            jawaban_audiens = st.text_input("Masukkan target audiens Anda:", key="audiens_custom_3")

        pilihan_vibe = st.selectbox("Perasaan atau suasana apa yang ingin dibangun?", 
                               ["Pilih...", "Semangat & Menggebu-gebu (Promosi)", "Tenang & Meyakinkan (Kesehatan/Edukasi)", "Santai & Menghibur (Kasual)", "Isi sendiri..."])
        
        jawaban_vibe = pilihan_vibe
        if pilihan_vibe == "Isi sendiri...":
            if "vibe_custom_3" not in st.session_state:
                st.session_state.vibe_custom_3 = ""
            jawaban_vibe = st.text_input("Masukkan vibe/emosi yang Anda inginkan:", key="vibe_custom_3")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_audiens and jawaban_vibe and jawaban_audiens != "Pilih..." and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi audiens dan suasana terlebih dahulu.")

    # ==========================================
    # LANGKAH 4: MEDIA YANG DIPAKAI & DURASI
    # ==========================================
    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Media yang Dipakai & Durasi")
        
        # 1. Tujuan Naskah
        pilihan_tujuan = st.selectbox("1. Apa tujuan pembuatan naskah ini?", 
                               ["Pilih...", 
                                "Copywriting / Naskah Iklan / Promosi", 
                                "Naskah Rekaman Audio", 
                                "Naskah Suara Penjelasan di Video",
                                "Teks Infografis / Presentasi Visual", 
                                "Isi sendiri..."])
        
        jawaban_tujuan = pilihan_tujuan
        if pilihan_tujuan == "Isi sendiri...":
            if "tujuan_custom_4" not in st.session_state:
                st.session_state.tujuan_custom_4 = ""
            jawaban_tujuan = st.text_input("Sebutkan tujuan pembuatan naskah Anda:", key="tujuan_custom_4")

        # 2. Konteks / Platform Media
        pilihan_konteks = st.selectbox("2. Naskah ini akan digunakan untuk platform media apa?", 
                               ["Pilih...", 
                                "Video Pendek (TikTok / Reels / Shorts)", 
                                "Voice Over Video YouTube", 
                                "Audio Presentasi / Komunitas", 
                                "Pesan Teks (WhatsApp / Telegram / Threads)",
                                "Caption Media Sosial (Instagram / Facebook / TikTok)",
                                "Postingan Infografis (Feed / Carousel Instagram / LinkedIn)",
                                "Isi sendiri..."])
        
        jawaban_konteks = pilihan_konteks
        if pilihan_konteks == "Isi sendiri...":
            if "konteks_custom_4" not in st.session_state:
                st.session_state.konteks_custom_4 = ""
            jawaban_konteks = st.text_input("Masukkan platform tujuan Anda:", key="konteks_custom_4")

        # 3. Logika Durasi Dinamis
        st.markdown("<br>", unsafe_allow_html=True)
        
        tujuan_terdeteksi = (jawaban_tujuan or "").lower()
        konteks_terdeteksi = (jawaban_konteks or "").lower()
        
        is_infografis = "infografis" in tujuan_terdeteksi or "infografis" in konteks_terdeteksi or "presentasi visual" in tujuan_terdeteksi
        is_teks = "pesan teks" in konteks_terdeteksi or "caption" in konteks_terdeteksi or "whatsapp" in konteks_terdeteksi or "threads" in konteks_terdeteksi
        
        if is_infografis:
            label_durasi = "3. Berapa jumlah slide / tampilan halaman yang diinginkan?"
            opsi_durasi = ["Pilih...", "1 Halaman Penuh (Poster/Infografis Panjang)", "3 Slide (Carousel Singkat)", "5 Slide (Carousel Standar)", "10 Slide (Carousel Maksimal)", "Isi sendiri..."]
        elif is_teks:
            label_durasi = "3. Berapa panjang teks yang Anda inginkan?"
            opsi_durasi = ["Pilih...", "Pendek (1-2 paragraf padat / < 500 karakter)", "Sedang (3-4 paragraf)", "Panjang (Bercerita / Storytelling detail)", "Isi sendiri..."]
        else:
            label_durasi = "3. Berapa target durasi/panjang naskah Anda?"
            opsi_durasi = ["Pilih...", "15 detik (Singkat / Iklan Cepat / Pesan Pendek)", "30 detik (Standar Iklan/Reels/Caption Menengah)", "60 detik (Edukasi / Penjelasan Lengkap)", "Isi sendiri..."]

        pilihan_durasi = st.selectbox(label_durasi, opsi_durasi)
        
        jawaban_durasi = pilihan_durasi
        if pilihan_durasi == "Isi sendiri...":
            if "durasi_custom_4" not in st.session_state:
                st.session_state.durasi_custom_4 = ""
            jawaban_durasi = st.text_input("Masukkan target (misal: 45 detik, 2 paragraf, 5 slide):", key="durasi_custom_4")
            
            # --- LOGIKA PEMBATASAN DURASI (HARD CAP 180 DETIK) ---
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
                        total_detik = 0 # Abaikan jika isian berupa slide/paragraf
                    
                    if total_detik > 180:
                        st.warning("⏳ **Perhatian:** Maksimal target durasi audio/video adalah **180 detik (3 menit)**. Isian otomatis dibatasi.")
                        jawaban_durasi = "180 detik (Batas maksimal)"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_tujuan and jawaban_konteks and jawaban_durasi and jawaban_tujuan != "Pilih..." and jawaban_konteks != "Pilih..." and jawaban_durasi != "Pilih...":
                    st.session_state.jawaban["tujuan"] = jawaban_tujuan
                    st.session_state.jawaban["konteks"] = jawaban_konteks
                    st.session_state.jawaban["durasi"] = jawaban_durasi
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi tujuan, media, dan durasi terlebih dahulu.")

    # ==========================================
    # LANGKAH 5: KONTEKS & RANGKUMAN FINAL
    # ==========================================
    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Draft Brief & Koreksi")
        
        st.info("📋 **Draft Brief untuk Direktur Kreatif AI:**\nSilakan periksa dan edit isi kotak di bawah ini jika ada yang kurang pas sebelum diproses menjadi naskah akhir.")

        if "edit_produk_5" not in st.session_state:
            st.session_state.edit_produk_5 = st.session_state.jawaban.get("produk", "")
        edit_produk = st.text_input("1. Kategori Produk/Jasa", key="edit_produk_5")
        
        edit_merk = st.session_state.jawaban.get("merk", "")
        edit_jenis = st.session_state.jawaban.get("jenis_spesifik", "")
        
        if edit_merk or edit_jenis:
            if "edit_merk_5" not in st.session_state:
                st.session_state.edit_merk_5 = edit_merk
            if "edit_jenis_5" not in st.session_state:
                st.session_state.edit_jenis_5 = edit_jenis
                
            edit_merk = st.text_input("1a. Merk / Brand", key="edit_merk_5")
            edit_jenis = st.text_input("1b. Jenis Spesifik", key="edit_jenis_5")

        if "edit_poin_5" not in st.session_state:
            st.session_state.edit_poin_5 = st.session_state.jawaban.get("poin_penting", "")
        edit_poin = st.text_area("2. Keunggulan Utama", key="edit_poin_5")
        
        col_draft1, col_draft2 = st.columns(2)
        with col_draft1:
            if "edit_audiens_5" not in st.session_state:
                st.session_state.edit_audiens_5 = st.session_state.jawaban.get("audiens", "")
            edit_audiens = st.text_input("3. Target Audiens", key="edit_audiens_5")
            
            if "edit_vibe_5" not in st.session_state:
                st.session_state.edit_vibe_5 = st.session_state.jawaban.get("vibe", "")
            edit_vibe = st.text_input("4. Suasana / Tone", key="edit_vibe_5")
            
        with col_draft2:
            if "edit_tujuan_5" not in st.session_state:
                st.session_state.edit_tujuan_5 = st.session_state.jawaban.get("tujuan", "")
            edit_tujuan = st.text_input("5. Tujuan", key="edit_tujuan_5")

            if "edit_konteks_5" not in st.session_state:
                st.session_state.edit_konteks_5 = st.session_state.jawaban.get("konteks", "")
            edit_konteks = st.text_input("6. Platform Media", key="edit_konteks_5")

        if "edit_durasi_5" not in st.session_state:
            st.session_state.edit_durasi_5 = st.session_state.jawaban.get("durasi", "")
        edit_durasi = st.text_input("7. Target Panjang/Durasi", key="edit_durasi_5")
        
        st.divider()
        st.markdown("### 📝 Instruksi Tambahan (Opsional)")
        if "edit_tambahan_5" not in st.session_state:
            st.session_state.edit_tambahan_5 = st.session_state.jawaban.get("tambahan", "")
        edit_tambahan = st.text_area("Tuliskan permintaan khusus Anda di sini (Misal: 'Wajib sebutkan kata Diskon 50%', atau 'Jangan gunakan bahasa gaul')", key="edit_tambahan_5")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("✨ Hasilkan Naskah Berjiwa", type="primary"):
                st.session_state.jawaban["produk"] = edit_produk
                st.session_state.jawaban["merk"] = edit_merk
                st.session_state.jawaban["jenis_spesifik"] = edit_jenis
                st.session_state.jawaban["poin_penting"] = edit_poin
                st.session_state.jawaban["audiens"] = edit_audiens
                st.session_state.jawaban["vibe"] = edit_vibe
                st.session_state.jawaban["tujuan"] = edit_tujuan
                st.session_state.jawaban["konteks"] = edit_konteks
                st.session_state.jawaban["durasi"] = edit_durasi
                st.session_state.jawaban["tambahan"] = edit_tambahan
                st.session_state.wizard_step = 6
                st.rerun()

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
                    instruksi_tambahan_platform = ""
                    if "Threads" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Karena platform mencakup Threads, PANJANG NASKAH FINAL DI DALAM KOTAK KODE TIDAK BOLEH LEBIH DARI 500 KARAKTER (termasuk spasi)!"
                    elif "Infografis" in st.session_state.jawaban['tujuan'] or "Infografis" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Ini adalah teks untuk INFOGRAFIS/PRESENTASI VISUAL. Buat naskah yang sangat terstruktur, gunakan BULLET POINTS atau penomoran slide (Slide 1, Slide 2, dst). Gunakan kalimat yang SUPER PADAT, JELAS, dan HINDARI paragraf panjang naratif. Fokus pada data dan *punchline*."

                    prompt_final = f"""
                    {DIREKTUR_PROMPT}

                    TOLONG BUATKAN NASKAH BERDASARKAN PANDUAN BERIKUT:
                    - Kategori Produk/Jasa: {st.session_state.jawaban['produk']}
                    - Merk/Brand: {st.session_state.jawaban['merk'] if st.session_state.jawaban.get('merk') else '-'}
                    - Jenis Spesifik: {st.session_state.jawaban['jenis_spesifik'] if st.session_state.jawaban.get('jenis_spesifik') else '-'}
                    - Poin Penting/Keunggulan: {st.session_state.jawaban['poin_penting']}
                    - Target Audiens/Pembaca: {st.session_state.jawaban['audiens']}
                    - Vibe/Emosi: {st.session_state.jawaban['vibe']}
                    - Tujuan Pembuatan Naskah: {st.session_state.jawaban['tujuan']}
                    - Konteks Platform: {st.session_state.jawaban['konteks']} {instruksi_tambahan_platform}
                    - Durasi / Panjang Target: {st.session_state.jawaban['durasi']}
                    - Catatan Tambahan: {st.session_state.jawaban['tambahan'] if st.session_state.jawaban['tambahan'] else "Tidak ada"}
                    """
                    
                    # --- SISTEM AUTO-FALLBACK MODEL AI ---
                    models_to_try = ["gemini-1.5-flash", "gemini-1.0-pro", "gemini-2.5-flash"]
                    response = None
                    last_error = None
                    
                    for model_name in models_to_try:
                        try:
                            model_direktur = genai.GenerativeModel(model_name=model_name)
                            response = model_direktur.generate_content(prompt_final)
                            break
                        except Exception as inner_e:
                            last_error = inner_e
                            if "404" in str(inner_e):
                                continue 
                            else:
                                raise inner_e 
                                
                    if not response:
                        raise last_error

                    st.session_state.hasil_naskah = response.text
                    st.rerun()
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Quota exceeded" in error_msg:
                        if "limit" in error_msg.lower() or "perday" in error_msg.lower():
                            st.error("⏳ **Kuota Harian AI Terkuras Habis!** Anda telah melewati batas maksimal permintaan gratis per hari dari Google. Silakan ganti API Key dengan akun Google lain, atau tunggu esok hari.")
                        else:
                            st.error("⏳ **Sistem AI Sedang Sibuk!** Anda melakukan permintaan terlalu cepat. Silakan tunggu sekitar **1 menit** sebelum menekan tombol coba lagi.")
                    else:
                        st.error(f"Terjadi kesalahan saat menghubungi AI: {e}")
                    
                    if st.button("🔄 Coba Lagi"):
                        st.rerun()
        else:
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            st.info("💡 **Catatan:** Sistem kami akan otomatis menarik naskah di dalam kotak hitam di atas saat Anda berpindah ruangan. Silakan pilih langkah selanjutnya:")
            
            st.markdown("### Lanjut Produksi Karya:")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎨 Ke Studio Cetak (Visual)", use_container_width=True):
                    st.session_state.menu_aktif = "3. Studio Cetak"
                    st.rerun()
            with col2:
                if st.button("🚀 Ke Studio Rekaman (VO)", use_container_width=True):
                    st.session_state.menu_aktif = "2. Studio Rekaman"
                    st.rerun()
                    
            st.markdown("### Pembuatan Naskah Baru:")
            col3, col4 = st.columns(2)
            with col3:
                # Kembali ke Langkah 4 (Media & Durasi) untuk adaptasi naskah platform lain
                if st.button("🔁 Buat Versi Platform Lain", use_container_width=True, help="Ubah platform media tanpa mengetik ulang data produk, audiens, dan keunggulan."):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 4
                    st.rerun()
            with col4:
                if st.button("🔄 Reset & Buat Naskah Baru", use_container_width=True, help="Hapus semua data dan mulai dari awal."):
                    st.session_state.hasil_naskah = ""
                    for key in st.session_state.jawaban.keys():
                        st.session_state.jawaban[key] = ""
                    
                    keys_to_clear = list(st.session_state.keys())
                    for k in keys_to_clear:
                        if k.endswith("_1") or k.endswith("_2") or k.endswith("_3") or k.endswith("_4") or k.endswith("_5"):
                            del st.session_state[k]
                            
                    st.session_state.wizard_step = 1
                    st.rerun()
