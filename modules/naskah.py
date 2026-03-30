import streamlit as st
import google.generativeai as genai
import os
import re

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI ABSOLUT ANTI BOCOR) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif, Scriptwriter, dan Ahli Copywriting Profesional. Kamu sangat ahli menyusun naskah berjiwa, memikat, dan natural dengan gaya bahasa komunitas UMKM yang hangat dan persuasif.

[ATURAN KONDISIONAL FORMAT NASKAH - WAJIB MUTLAK DIIKUTI!]
1. KHUSUS JIKA TARGET ADALAH "Pesan Singkat", "WhatsApp", ATAU "Caption":
   - Output WAJIB 100% TEKS BERSIH SIAP COPAS. Leburkan kalimat pembuka dan naskah utama menjadi satu kesatuan pesan yang mengalir natural.
   - HARAM HUKUMNYA (DILARANG KERAS) menggunakan label kurung siku seperti [Hook] atau [Naskah Utama] di dalam teks.
   - HARAM HUKUMNYA (DILARANG KERAS) memunculkan elemen [Poin Infografis] maupun [Objek Visual Aman]. JANGAN DITULIS SAMA SEKALI. Kotak kode HANYA boleh berisi teks naskah promosi/edukasi yang siap kirim.
   - Naskah siap copas ini WAJIB diakhiri dengan kalimat persis: "Dapatkan produk berkualitas ini sekarang juga di ktbukm-jatim.store"

2. JIKA TARGET ADALAH "Video", "Audio", "Voice Over", atau "Teks Infografis/Carousel":
   - WAJIB gunakan pemecahan modular dengan label: [Hook / Judul Pemikat], [Naskah Utama], [Poin Infografis], dan [Objek Visual Aman].
   - Jika diminta "1 Slide", berikan [Poin Infografis] yang padat (maks 5 kata per poin), abaikan naskah lisan panjang.
   - Naskah utama WAJIB diakhiri dengan: "Dapatkan produk berkualitas ini sekarang juga di ktbukm-jatim.store"

3. ATURAN UMUM:
   - Gunakan bahasa membumi khas UMKM, hindari jargon teknis tingkat tinggi.

[ALUR KERJA]
1. 💡 Alasan Kreatif & Strategi
2. 🎛️ Arahan Rekaman / Publikasi
3. 🎙️ Naskah Final (Di dalam Kotak Kode):
Kamu WAJIB membungkus naskah final di dalam kotak kode (markdown code block) dengan awalan ```text dan akhiran ```. (Terapkan Aturan Kondisional di atas dengan SANGAT KETAT untuk isi di dalam kotak ini).
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Studio Kreasi Naskah")
    
    st.info("💡 **Informasi:** Studio ini adalah titik awal produksi Anda. Di sini, Kecerdasan Buatan (AI) bertindak sebagai Direktur Kreatif yang akan membantu Anda menyusun naskah profesional.")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {
            "produk": "", "poin_penting": "", "audiens": "", "platform_tujuan": "", 
            "durasi": "", "vibe": "", "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1 TO 5 (WIZARD INPUTS)
    # ==========================================
    
    # --- LANGKAH 1: PRODUK ---
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", "1. Aplikasi Kesehatan - Konsultan Puasa IF", "2. Aplikasi Pintar Saham - Konsultan Saham Indonesia", "3. Produk Kesehatan & Perawatan Pribadi", "4. Produk Makanan, Minuman & Suplemen", "5. Layanan / Jasa Komunitas", "6. Barang Elektronik / Gadget", "7. Acara / Webinar", "8. Isi Sendiri ..."], key="sb_prod")
        jawaban_final = pilihan
        if pilihan == "8. Isi Sendiri ...":
            jawaban_final = st.text_input("Sebutkan produk atau jasa Anda:", key="ti_prod")

        if st.button("Selanjutnya ➡️", key="btn_next_1"):
            if jawaban_final and jawaban_final != "Pilih...":
                st.session_state.jawaban["produk"] = jawaban_final
                st.session_state.wizard_step = 2
                st.rerun()
            else:
                st.warning("Mohon pilih atau isi produk/jasa terlebih dahulu.")

    # --- LANGKAH 2: KEUNGGULAN ---
    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", 
                               ["Pilih...", "Aplikasi Kesehatan: i) IF Aman: Pola puasa disesuaikan. ii) Nutrisi Cerdas. iii) Olahraga Terukur. iv) Laporan Instan.", "Aplikasi Pintar Saham: i) 6 Modul Analisa Premium. ii) Screening Otomatis. iii) Risk Management. iv) Data Real-Time. v) Laporan PDF.", "Manfaat kesehatan & bahan alami yang digunakan", "Promo diskon terbatas & harga spesial", "Solusi praktis untuk masalah sehari-hari", "Ajakan bergabung ke komunitas / acara", "Isi Sendiri ..."], key="sb_poin")
        jawaban_final = pilihan
        if pilihan == "Isi Sendiri ...":
            jawaban_final = st.text_area("Tuliskan poin penting/keunggulan produk Anda:", key="ta_poin")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_2"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️", key="btn_next_2"):
                if jawaban_final and jawaban_final != "Pilih...":
                    st.session_state.jawaban["poin_penting"] = jawaban_final
                    st.session_state.wizard_step = 3
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi poin penting terlebih dahulu.")

    # --- LANGKAH 3: SASARAN KONSUMEN (AUDIENS) ---
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Sasaran Konsumen")
        pilihan_audiens = st.selectbox("Siapa target audiens atau pembaca naskah ini?", 
                                       ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi Sendiri ..."], key="sb_aud")
        jawaban_audiens = pilihan_audiens
        if pilihan_audiens == "Isi Sendiri ...":
            jawaban_audiens = st.text_input("Masukkan target audiens Anda secara spesifik:", key="ti_aud")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_3"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️", key="btn_next_3"):
                if jawaban_audiens and jawaban_audiens != "Pilih...":
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi sasaran konsumen terlebih dahulu.")

    # --- LANGKAH 4: PLATFORM & TUJUAN ---
    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Platform & Tujuan Penggunaan")
        # Pre-fill dengan jawaban sebelumnya jika ada (membantu saat klik Ganti Format)
        pilihan_platform = st.selectbox("Di mana naskah ini akan dipublikasikan?", 
                                        ["Pilih...", 
                                         "Pesan Singkat (WhatsApp / Telegram / Threads)", 
                                         "Caption Media Sosial (Instagram / Facebook / TikTok)", 
                                         "Teks Infografis / Carousel (Feed IG / Presentasi)", 
                                         "Video Pendek (TikTok / Reels / Shorts)", 
                                         "Voice Over Video YouTube / Audio Komunitas", 
                                         "Isi Sendiri ..."], key="sb_plat")
        jawaban_platform = pilihan_platform
        if pilihan_platform == "Isi Sendiri ...":
            jawaban_platform = st.text_input("Sebutkan platform tujuan spesifik Anda:", key="ti_plat")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_4"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️", key="btn_next_4"):
                if jawaban_platform and jawaban_platform != "Pilih...":
                    st.session_state.jawaban["platform_tujuan"] = jawaban_platform
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi platform tujuan terlebih dahulu.")

    # --- LANGKAH 5: DURASI, VIBE & KOREKSI AKHIR ---
    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Target Durasi, Suasana & Koreksi Akhir")
        
        platform_terpilih = st.session_state.jawaban.get("platform_tujuan", "")
        opsi_durasi = ["Pilih..."]
        
        if "WhatsApp" in platform_terpilih or "Pesan" in platform_terpilih or "Caption" in platform_terpilih:
            opsi_durasi.extend(["1 Paragraf Singkat (Sangat Padat)", "2-3 Paragraf (Standar Promo)", "Maksimal 300 Kata (Detail Lengkap)", "Isi Sendiri ..."])
        elif "Infografis" in platform_terpilih or "Carousel" in platform_terpilih:
            opsi_durasi.extend(["1 Slide Penuh (Poster Tunggal)", "3 Slide (Carousel Singkat)", "5 Slide (Carousel Standar)", "Isi Sendiri ..."])
        elif "Video" in platform_terpilih or "Voice Over" in platform_terpilih or "Audio" in platform_terpilih:
            opsi_durasi.extend(["15 detik (Iklan Cepat)", "30 detik (Standar Reels/TikTok)", "60 detik (Edukasi)", "Isi Sendiri ..."])
        else:
            opsi_durasi.extend(["Sangat Pendek / Singkat", "Sedang", "Panjang / Detail", "Isi Sendiri ..."])

        col_dur, col_vib = st.columns(2)
        with col_dur:
            pilihan_durasi = st.selectbox("Target Panjang/Durasi?", opsi_durasi, key="sb_dur")
            jawaban_durasi = pilihan_durasi
            if pilihan_durasi == "Isi Sendiri ...":
                jawaban_durasi = st.text_input("Masukkan target ukuran/durasi spesifik:", key="ti_dur")

            if jawaban_durasi and jawaban_durasi != "Pilih...":
                angka_ditemukan = re.findall(r'\d+', jawaban_durasi)
                if angka_ditemukan:
                    nilai_angka = int(angka_ditemukan[0])
                    teks_kecil = jawaban_durasi.lower()
                    if "jam" in teks_kecil: total_detik = nilai_angka * 3600
                    elif "menit" in teks_kecil: total_detik = nilai_angka * 60
                    elif "detik" in teks_kecil: total_detik = nilai_angka
                    else: total_detik = 0 
                    
                    if total_detik > 180:
                        st.warning("⏳ Maksimal target durasi untuk Audio/Video adalah **180 detik**. Isian dikunci ke batas maksimal.")
                        jawaban_durasi = "180 detik (Batas maksimal)"

        with col_vib:
            pilihan_vibe = st.selectbox("Suasana (Vibe)?", ["Pilih...", "Semangat (Promosi)", "Tenang (Edukasi)", "Santai (Kasual)", "Isi Sendiri ..."], key="sb_vibe")
            jawaban_vibe = pilihan_vibe
            if pilihan_vibe == "Isi Sendiri ...":
                jawaban_vibe = st.text_input("Masukkan emosi/suasana:", key="ti_vibe")

        st.divider()
        st.info("📋 **Koreksi Akhir Naskah Anda:**\nPastikan data di bawah ini sudah tepat sebelum dieksekusi oleh AI.")

        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""), key="ed_prod")
        edit_poin = st.text_area("2. Keunggulan", value=st.session_state.jawaban.get("poin_penting", ""), key="ed_poin")
        edit_audiens = st.text_input("3. Sasaran Konsumen", value=st.session_state.jawaban.get("audiens", ""), key="ed_aud")
        edit_platform = st.text_input("4. Platform/Tujuan", value=st.session_state.jawaban.get("platform_tujuan", ""), key="ed_plat")
        edit_tambahan = st.text_area("Catatan Tambahan (Opsional)", placeholder="Misal: Wajib sebutkan promo bebas ongkir.", key="ed_tambahan")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali", key="btn_back_5"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("✨ Lanjutkan ke Tahap Produksi", type="primary", key="btn_next_5"):
                if jawaban_durasi and jawaban_vibe and jawaban_durasi != "Pilih..." and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["produk"] = edit_produk
                    st.session_state.jawaban["poin_penting"] = edit_poin
                    st.session_state.jawaban["audiens"] = edit_audiens
                    st.session_state.jawaban["platform_tujuan"] = edit_platform
                    st.session_state.jawaban["durasi"] = jawaban_durasi
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.jawaban["tambahan"] = edit_tambahan
                    st.session_state.wizard_step = 6
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi Target Durasi dan Suasana (Vibe) terlebih dahulu.")

    # ==========================================
    # LANGKAH 6: PROSES AI & HASIL
    # ==========================================
    elif st.session_state.wizard_step == 6:
        platform_tujuan = st.session_state.jawaban.get("platform_tujuan", "")
        if "Audio" in platform_tujuan or "Video" in platform_tujuan or "Voice Over" in platform_tujuan:
            header_text = "🎬 Hasil Naskah Pro (Format Audio / Skrip Video)"
            spinner_text = "Direktur sedang menyusun naskah dengan teknik intonasi/SSML..."
            instruksi_tambahan = "Gunakan label skrip modular. WAJIB gunakan tag SSML untuk rekaman."
        elif "Pesan" in platform_tujuan or "WhatsApp" in platform_tujuan or "Caption" in platform_tujuan:
            header_text = "📱 Hasil Naskah Pro (Siap Copas)"
            spinner_text = "Direktur sedang menyusun pesan siap copas..."
            instruksi_tambahan = "WAJIB bentuk teks SIAP COPAS bersih 100%. DILARANG KERAS menyertakan [Poin Infografis] maupun [Objek Visual Aman]. JANGAN DITULIS SAMA SEKALI. DILARANG menggunakan tag SSML."
        else:
            header_text = "📝 Hasil Naskah Pro (Format Teks / Visual)"
            spinner_text = "Direktur sedang menyusun naskah Copywriting visual..."
            instruksi_tambahan = "Gunakan label skrip modular. DILARANG KERAS menggunakan tag SSML."

        st.subheader(header_text)

        if not st.session_state.hasil_naskah:
            st.info("💡 **Pengaturan naskah Anda sudah diamankan!** Silakan tekan tombol di bawah ini untuk menginstruksikan AI menyusun naskah Anda.")
            
            if st.button("✨ Eksekusi Naskah Sekarang", type="primary", use_container_width=True, key="btn_eksekusi_final"):
                with st.spinner(spinner_text):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=DIREKTUR_PROMPT)
                        
                        prompt_final = f"""
                        Tolong buatkan naskah berdasarkan panduan berikut:
                        - Produk/Jasa: {st.session_state.jawaban.get('produk', '')}
                        - Keunggulan Utama: {st.session_state.jawaban.get('poin_penting', '')}
                        - Sasaran Konsumen: {st.session_state.jawaban.get('audiens', '')}
                        - Platform & Tujuan: {st.session_state.jawaban.get('platform_tujuan', '')}
                        - Target Durasi/Panjang: {st.session_state.jawaban.get('durasi', '')}
                        - Suasana/Vibe: {st.session_state.jawaban.get('vibe', '')}
                        - Catatan Tambahan: {st.session_state.jawaban.get('tambahan', '')}
                        
                        ATURAN KHUSUS SAAT INI (BACA DENGAN TELITI): {instruksi_tambahan}.
                        """
                        
                        response = model.generate_content(prompt_final)
                        st.session_state.hasil_naskah = response.text
                        st.rerun()
                        
                    except Exception as e:
                        err_msg = str(e).lower()
                        if "429" in err_msg or "quota" in err_msg:
                            st.error("⏳ **Mesin AI Sedang Beristirahat (Batas Kuota Beruntun).**")
                            st.info("💡 **Solusi Aman:** Karena request beruntun terlalu cepat, Google menghentikan sementara aksesnya. **TIDAK PERLU KEMBALI KE AWAL ATAU MENEKAN TOMBOL LAIN**. Cukup lepaskan *mouse* Anda, **tunggu 1 menit penuh**, lalu klik kembali tombol **'✨ Eksekusi Naskah Sekarang'** di atas. Data Anda aman dan tidak akan hilang.")
                        else:
                            st.error(f"❌ Terjadi kesalahan saat menghubungi AI: {e}")
        else:
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            st.info("🛠️ **Opsi Perubahan Naskah:**\nAnda bisa membuat ulang untuk produk/jasa lain, atau mengubah platform/format untuk produk ini (misal: dari WA ke Infografis) tanpa mengetik ulang info dari awal.")
            
            col_reset1, col_reset2 = st.columns(2)
            with col_reset1:
                # Tombol Ganti Format memicu rerun ke Langkah 4 dan MENGHAPUS memori hasil naskah lama
                if st.button("🔁 Ganti Format (Platform/Tujuan) untuk Produk Ini", use_container_width=True, key="btn_ganti_format"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 4
                    st.rerun()
            with col_reset2:
                if st.button("🔄 Buat Naskah Baru (Produk/Jasa Lain)", use_container_width=True, key="btn_buat_baru"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 1
                    for key in st.session_state.jawaban:
                        st.session_state.jawaban[key] = ""
                    st.rerun()

            st.divider()
            st.info("🚀 **Lanjut Tahap Produksi:**\nSistem kami akan otomatis menarik data dari naskah di atas. Silakan pilih studio selanjutnya:")
            
            # Mendefinisikan kolom navigasi dengan sangat eksplisit untuk mencegah NameError
            col_nav1, col_nav2 = st.columns(2)
            with col_nav1:
                if st.button("🎨 Ke Studio Kreasi Cetak / Visual", use_container_width=True, key="btn_nav_visual"):
                    st.session_state.menu_aktif = "3. Studio Kreasi Cetak / Visual"
                    st.rerun()
            with col_nav2:
                if st.button("🎙️ Ke Studio Kreasi Suara / Audio", use_container_width=True, key="btn_nav_audio"):
                    st.session_state.menu_aktif = "2. Studio Kreasi Suara / Audio"
                    st.rerun()
