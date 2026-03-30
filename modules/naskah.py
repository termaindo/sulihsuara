import streamlit as st
import google.generativeai as genai
import os
import re

def run():
    # --- 1. KARANTINA MEMORI SISTEM ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- 2. PROMPT DIREKTUR KREATIF (VERSI KONDISIONAL & MODULAR) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif, Scriptwriter, dan Ahli Copywriting Profesional. Kamu sangat ahli menyusun naskah berjiwa, memikat, dan natural dengan gaya bahasa komunitas UMKM yang hangat dan persuasif.

[ATURAN KONDISIONAL DURASI & PANJANG NASKAH - WAJIB MUTLAK DIIKUTI!]
- JIKA target panjang naskah adalah "1 Paragraf", "Pesan WA", atau sangat singkat: DILARANG KERAS membuat naskah panjang menggunakan pola PAS/AIDA penuh. Cukup buat 1 kalimat pembuka yang kuat, inti penawaran, dan langsung ke Call to Action.
- JIKA target platform adalah "Infografis/Visual" dan diminta "1 Slide": DILARANG KERAS membuat naskah narasi panjang. Langsung berikan maksimal 3-5 poin padat (tiap poin maks 3-5 kata) untuk [Poin Infografis], abaikan narasi lisan.
- JIKA audiens adalah UMKM: Gunakan bahasa yang membumi, hindari jargon teknis tingkat tinggi kecuali dijelaskan dengan bahasa sederhana.

[ALUR KERJA]
Berdasarkan data wawancara pengguna, susunlah output ke dalam 3 bagian utama berikut:

1. 💡 Alasan Kreatif & Strategi:
Jelaskan secara singkat dengan bahasa awam yang ramah, mengapa pendekatan naskah ini digunakan.

2. 🎛️ Arahan Rekaman / Publikasi:
Berikan panduan tone suara, emosi, atau gaya visual yang paling cocok untuk naskah ini.

3. 🎙️ Naskah Final (Di dalam Kotak Kode):
Kamu WAJIB membungkus naskah di dalam kotak kode (markdown code block) dengan awalan ```text dan akhiran ```.
Di dalam kotak kode tersebut, bagilah naskah menjadi blok-blok modular agar siap pakai:

- [Hook / Judul Pemikat]: 1-2 kalimat super pendek yang langsung memancing rasa penasaran atau menyentuh masalah.
- [Naskah Utama]: Ditulis natural. (Ingat Aturan Kondisional: Jika diminta singkat, buatlah SANGAT singkat).
   * KHUSUS AUDIO/VIDEO: Jika tujuannya untuk suara, gunakan tag SSML (<speak>, <break time="400ms"/>, <prosody pitch="+1st" rate="1.1">) untuk mengatur intonasi.
   * KHUSUS NON-AUDIO: Jika bukan untuk suara, DILARANG KERAS memakai tag SSML. Gunakan bahasa copywriting biasa.
- [Poin Infografis]: Rangkuman inti dari naskah di atas ke dalam poin-poin yang SANGAT PADAT (maksimal 3-5 kata per poin) khusus untuk visual slide.
- [Objek Visual Aman]: WAJIB berikan 1 kalimat deskripsi fisik kemasan produk dalam Bahasa Inggris sebagai murni benda mati (contoh: "A minimalist pump bottle of liquid soap on a bathroom sink with green leaves"). DILARANG KERAS menyebutkan efeknya pada kulit, tubuh, atau kesehatan.
- [Call to Action / Ajakan Bertindak]: WAJIB selalu ditutup dengan kalimat ajakan baku ini persis tanpa diubah: "Dapatkan produk berkualitas ini sekarang juga di ktbukm-jatim.store"
    """

    # --- 3. SETUP KREDENSIAL GEMINI ---
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Studio Kreasi Naskah")
    
    st.info("💡 **Informasi:** Studio ini adalah titik awal produksi Anda. Di sini, Kecerdasan Buatan (AI) bertindak sebagai Direktur Kreatif yang akan membantu Anda menyusun naskah, skrip, atau *copywriting* profesional hanya dengan menjawab beberapa pertanyaan sederhana. Hasil dari studio ini akan otomatis tersambung ke studio lainnya.")

    # --- 4. INISIALISASI STATE (WIZARD) ---
    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {
            "produk": "", "poin_penting": "", "platform_tujuan": "", "durasi": "", 
            "audiens": "", "vibe": "", "tambahan": ""
        }
        st.session_state.hasil_naskah = ""

    # ==========================================
    # LANGKAH 1 TO 5 (WIZARD INPUTS)
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", "1. Aplikasi Kesehatan - Konsultan Puasa IF", "2. Aplikasi Pintar Saham - Konsultan Saham Indonesia", "3. Produk Kesehatan & Perawatan Pribadi", "4. Produk Makanan, Minuman & Suplemen", "5. Layanan / Jasa Komunitas", "6. Barang Elektronik / Gadget", "7. Acara / Webinar", "8. Isi Sendiri ..."])
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

    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", 
                               ["Pilih...", "Aplikasi Kesehatan: i) IF Aman: Pola puasa disesuaikan. ii) Nutrisi Cerdas. iii) Olahraga Terukur. iv) Laporan Instan.", "Aplikasi Pintar Saham: i) 6 Modul Analisa Premium. ii) Screening Otomatis. iii) Risk Management. iv) Data Real-Time. v) Laporan PDF.", "Manfaat kesehatan & bahan alami yang digunakan", "Promo diskon terbatas & harga spesial", "Solusi praktis untuk masalah sehari-hari", "Ajakan bergabung ke komunitas / acara", "Isi Sendiri ..."])
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

    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Platform & Tujuan Penggunaan")
        pilihan_platform = st.selectbox("Di mana naskah ini akan dipublikasikan?", 
                                        ["Pilih...", 
                                         "Pesan Singkat (WhatsApp / Telegram / Threads)", 
                                         "Caption Media Sosial (Instagram / Facebook / TikTok)", 
                                         "Teks Infografis / Carousel (Feed IG / Presentasi)", 
                                         "Video Pendek (TikTok / Reels / Shorts)", 
                                         "Voice Over Video YouTube / Audio Komunitas", 
                                         "Isi Sendiri ..."])
        jawaban_platform = pilihan_platform
        if pilihan_platform == "Isi Sendiri ...":
            jawaban_platform = st.text_input("Sebutkan platform tujuan spesifik Anda:")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_platform and jawaban_platform != "Pilih...":
                    st.session_state.jawaban["platform_tujuan"] = jawaban_platform
                    st.session_state.wizard_step = 4
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi platform tujuan terlebih dahulu.")

    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Target Panjang / Durasi")
        
        platform_terpilih = st.session_state.jawaban.get("platform_tujuan", "")
        opsi_durasi = ["Pilih..."]
        
        # Logika Dinamis Menyesuaikan Platform dari Langkah 3
        if "WhatsApp" in platform_terpilih or "Pesan" in platform_terpilih or "Caption" in platform_terpilih:
            opsi_durasi.extend(["1 Paragraf Singkat (Sangat Padat)", "2-3 Paragraf (Standar Promo)", "Maksimal 300 Kata (Detail Lengkap)", "Isi Sendiri ..."])
        elif "Infografis" in platform_terpilih or "Carousel" in platform_terpilih:
            opsi_durasi.extend(["1 Slide Penuh (Poster Tunggal)", "3 Slide (Carousel Singkat)", "5 Slide (Carousel Standar)", "Isi Sendiri ..."])
        elif "Video" in platform_terpilih or "Voice Over" in platform_terpilih or "Audio" in platform_terpilih:
            opsi_durasi.extend(["15 detik (Iklan Cepat)", "30 detik (Standar Reels/TikTok)", "60 detik (Edukasi)", "Isi Sendiri ..."])
        else:
            opsi_durasi.extend(["Sangat Pendek / Singkat", "Sedang", "Panjang / Detail", "Isi Sendiri ..."])

        pilihan_durasi = st.selectbox("Berapa panjang naskah yang Anda butuhkan?", opsi_durasi)
        jawaban_durasi = pilihan_durasi
        
        if pilihan_durasi == "Isi Sendiri ...":
            jawaban_durasi = st.text_input("Masukkan target ukuran naskah secara spesifik (contoh: 45 detik, atau 2 kalimat):")
            
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
                    st.warning("⏳ **Perhatian:** Maksimal target durasi untuk Audio/Video adalah **180 detik (3 menit)**. Isian Anda otomatis dikunci ke batas maksimal tersebut.")
                    jawaban_durasi = "180 detik (Batas maksimal)"

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 3
                st.rerun()
        with col2:
            if st.button("Selanjutnya ➡️"):
                if jawaban_durasi and jawaban_durasi != "Pilih...":
                    st.session_state.jawaban["durasi"] = jawaban_durasi
                    st.session_state.wizard_step = 5
                    st.rerun()
                else:
                    st.warning("Mohon pilih atau isi target durasi terlebih dahulu.")

    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Audiens, Suasana & Koreksi Akhir")
        
        col_aud, col_vib = st.columns(2)
        with col_aud:
            pilihan_audiens = st.selectbox("Target Audiens?", ["Pilih...", "Pensiunan / Senior (Jelas, santai)", "Profesional / Pekerja (Formal, lugas)", "Anak Muda / Gen Z (Kasual, gaul)", "Ibu Rumah Tangga (Hangat, praktis)", "Isi Sendiri ..."])
            jawaban_audiens = pilihan_audiens
            if pilihan_audiens == "Isi Sendiri ...":
                jawaban_audiens = st.text_input("Masukkan target audiens:")

        with col_vib:
            pilihan_vibe = st.selectbox("Suasana (Vibe)?", ["Pilih...", "Semangat (Promosi)", "Tenang (Edukasi)", "Santai (Kasual)", "Isi Sendiri ..."])
            jawaban_vibe = pilihan_vibe
            if pilihan_vibe == "Isi Sendiri ...":
                jawaban_vibe = st.text_input("Masukkan emosi/suasana:")

        st.divider()
        st.info("📋 **Koreksi Akhir Naskah Anda:**\nSilakan pastikan data di bawah ini sudah tepat sebelum dieksekusi oleh AI.")

        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""))
        edit_poin = st.text_area("2. Keunggulan", value=st.session_state.jawaban.get("poin_penting", ""))
        edit_platform = st.text_input("3. Platform/Tujuan", value=st.session_state.jawaban.get("platform_tujuan", ""))
        edit_durasi = st.text_input("4. Durasi/Panjang", value=st.session_state.jawaban.get("durasi", ""))
        edit_tambahan = st.text_area("5. Catatan Tambahan (Opsional)", placeholder="Misal: Wajib sebutkan promo bebas ongkir.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Kembali"):
                st.session_state.wizard_step = 4
                st.rerun()
        with col2:
            if st.button("✨ Lanjutkan ke Tahap Produksi", type="primary"):
                if jawaban_audiens and jawaban_vibe and jawaban_audiens != "Pilih..." and jawaban_vibe != "Pilih...":
                    st.session_state.jawaban["produk"] = edit_produk
                    st.session_state.jawaban["poin_penting"] = edit_poin
                    st.session_state.jawaban["platform_tujuan"] = edit_platform
                    st.session_state.jawaban["durasi"] = edit_durasi
                    st.session_state.jawaban["audiens"] = jawaban_audiens
                    st.session_state.jawaban["vibe"] = jawaban_vibe
                    st.session_state.jawaban["tambahan"] = edit_tambahan
                    st.session_state.wizard_step = 6
                    st.rerun()
                else:
                    st.warning("Mohon lengkapi pilihan Audiens dan Suasana terlebih dahulu.")

    # ==========================================
    # LANGKAH 6: PROSES AI & HASIL (TOMBOL STATIS + ANTI RERUN ERROR)
    # ==========================================
    elif st.session_state.wizard_step == 6:
        platform_tujuan = st.session_state.jawaban.get("platform_tujuan", "")
        if "Audio" in platform_tujuan or "Video" in platform_tujuan or "Voice Over" in platform_tujuan:
            header_text = "🎬 Hasil Naskah Pro (Format Audio / SSML)"
            spinner_text = "Direktur sedang menyusun naskah dengan teknik SSML..."
            instruksi_tambahan = "WAJIB gunakan tag SSML untuk rekaman."
        else:
            header_text = "📝 Hasil Naskah Pro (Format Teks / Visual)"
            spinner_text = "Direktur sedang menyusun naskah Copywriting visual..."
            instruksi_tambahan = "DILARANG KERAS menggunakan tag SSML. Gunakan bahasa copywriting biasa."

        st.subheader(header_text)

        if not st.session_state.hasil_naskah:
            st.info("💡 **Pengaturan naskah Anda sudah diamankan!** Silakan tekan tombol di bawah ini untuk menginstruksikan AI menyusun naskah Anda.")
            
            if st.button("✨ Eksekusi Naskah Sekarang", type="primary", use_container_width=True):
                with st.spinner(spinner_text):
                    try:
                        model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=DIREKTUR_PROMPT)
                        
                        prompt_final = f"""
                        Tolong buatkan naskah berdasarkan panduan berikut:
                        - Produk/Jasa: {st.session_state.jawaban.get('produk', '')}
                        - Poin Penting: {st.session_state.jawaban.get('poin_penting', '')}
                        - Platform & Tujuan: {st.session_state.jawaban.get('platform_tujuan', '')}
                        - Target Durasi/Panjang: {st.session_state.jawaban.get('durasi', '')}
                        - Target Audiens: {st.session_state.jawaban.get('audiens', '')}
                        - Suasana/Vibe: {st.session_state.jawaban.get('vibe', '')}
                        - Catatan Tambahan: {st.session_state.jawaban.get('tambahan', '')}
                        
                        ATURAN KHUSUS SAAT INI: {instruksi_tambahan}. Pastikan panjang teks sangat akurat dengan permintaan di bagian 'Target Durasi/Panjang'.
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
