import streamlit as st
import google.generativeai as genai
import os
import re  # Ditambahkan untuk mendeteksi angka pada teks durasi

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
    # LANGKAH 1: PRODUK / JASA
    # ==========================================
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?", 
                               ["Pilih...", 
                                "Produk Kesehatan & Suplemen", 
                                "Makanan & Minuman", 
                                "Layanan / Jasa Komunitas", 
                                "Barang Elektronik / Gadget", 
                                "Acara / Webinar",
                                "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
            jawaban_final = st.text_input("Sebutkan produk atau jasa Anda:")

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
        pilihan = st.selectbox("Apa pesan utama atau keunggulan yang WAJIB disampaikan?", 
                               ["Pilih...", 
                                "Manfaat kesehatan & bahan alami yang digunakan", 
                                "Promo diskon terbatas & harga spesial", 
                                "Solusi praktis untuk masalah sehari-hari", 
                                "Ajakan bergabung ke komunitas / acara",
                                "Isi sendiri..."])
        
        jawaban_final = pilihan
        if pilihan == "Isi sendiri...":
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
    # LANGKAH 3: TUJUAN & DURASI
    # ==========================================
    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Tujuan & Target Panjang/Durasi")
        
        # Penambahan Tujuan Pembuatan Naskah (Termasuk Infografis)
        pilihan_tujuan = st.selectbox("Apa tujuan pembuatan naskah ini?", 
                               ["Pilih...", 
                                "Copywriting / Naskah Iklan / Promosi", 
                                "Naskah Rekaman Audio", 
                                "Naskah Suara Penjelasan di Video",
                                "Teks Infografis / Presentasi Visual", 
                                "Isi sendiri..."])
        
        jawaban_tujuan = pilihan_tujuan
        if pilihan_tujuan == "Isi sendiri...":
            jawaban_tujuan = st.text_input("Sebutkan tujuan pembuatan naskah Anda:")

        st.markdown("<br>", unsafe_allow_html=True) # Memberi sedikit jarak

        pilihan_durasi = st.selectbox("Berapa panjang atau target durasi naskah Anda?", 
                               ["Pilih...", "15 detik (Singkat / Iklan Cepat / Pesan Pendek)", "30 detik (Standar Iklan/Reels/Caption Menedah)", "60 detik (Edukasi / Penjelasan Lengkap)", "Isi sendiri..."])
        
        jawaban_durasi = pilihan_durasi
        if pilihan_durasi == "Isi sendiri...":
            jawaban_durasi = st.text_input("Masukkan target panjang naskah (misal: 45 detik, 2 paragraf, atau 5 slide):")
            
            # --- LOGIKA PEMBATASAN DURASI (HARD CAP 180 DETIK) ---
            if jawaban_durasi:
                angka_ditemukan = re.findall(r'\d+', jawaban_durasi)
                if angka_ditemukan:
                    nilai_angka = int(angka_ditemukan[0])
                    teks_kecil = jawaban_durasi.lower()
                    
                    # Konversi ke detik untuk pengecekan
                    if "jam" in teks_kecil:
                        total_detik = nilai_angka * 3600
                    elif "menit" in teks_kecil:
                        total_detik = nilai_angka * 60
                    elif "detik" in teks_kecil:
                        total_detik = nilai_angka
                    else:
                        total_detik = 0 # Abaikan jika isian berupa "5 slide" atau "2 paragraf"
                    
                    # Penguncian jika melebihi batas (Hanya jika terdeteksi unsur waktu)
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
        # Perubahan pertanyaan audiens
        pilihan_audiens = st.selectbox("Untuk siapa pendengar atau pembaca dari naskah ini?", 
                               ["Pilih...", "Pensiunan / Senior (Jelas, santai, hormat)", "Profesional / Pekerja (Formal, padat, lugas)", "Anak Muda / Gen Z (Cepat, kasual, gaul)", "Ibu Rumah Tangga (Hangat, akrab, praktis)", "Isi sendiri..."])
        
        jawaban_audiens = pilihan_audiens
        if pilihan_audiens == "Isi sendiri...":
            jawaban_audiens = st.text_input("Masukkan target audiens Anda:")

        pilihan_vibe = st.selectbox("Perasaan apa yang ingin dibangun?", 
                               ["Pilih...", "Semangat & Menggebu-gebu (Promosi)", "Tenang & Meyakinkan (Kesehatan/Edukasi)", "Santai & Menghibur (Kasual)", "Isi sendiri..."])
        
        jawaban_vibe = pilihan_vibe
        if pilihan_vibe == "Isi sendiri...":
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
        
        # Penambahan Platform Infografis
        pilihan_konteks = st.selectbox("Naskah ini akan digunakan untuk platform apa?", 
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
            jawaban_konteks = st.text_input("Masukkan platform tujuan Anda:")

        st.divider()
        st.info("📋 **Periksa Kembali Panduan Naskah Anda:**\nSilakan edit langsung di dalam kotak jika ada yang ingin diubah sebelum diserahkan ke Direktur Kreatif.")

        # Menampilkan input editable beserta penambahan Tujuan
        edit_produk = st.text_input("1. Produk/Jasa", value=st.session_state.jawaban.get("produk", ""))
        edit_poin = st.text_input("2. Poin Penting", value=st.session_state.jawaban.get("poin_penting", ""))
        edit_tujuan = st.text_input("3. Tujuan Naskah", value=st.session_state.jawaban.get("tujuan", ""))
        
        # Kolom durasi dengan proteksi real-time
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
            # Memunculkan notifikasi bantuan berdasarkan platform khusus
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
                    
                    # Logika Hard Cap & Format Khusus
                    instruksi_tambahan_platform = ""
                    if "Threads" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Karena platform mencakup Threads, PANJANG NASKAH FINAL DI DALAM KOTAK KODE TIDAK BOLEH LEBIH DARI 500 KARAKTER (termasuk spasi)!"
                    elif "Infografis" in st.session_state.jawaban['tujuan'] or "Infografis" in st.session_state.jawaban['konteks']:
                        instruksi_tambahan_platform = "\n[ATURAN MUTLAK] Ini adalah teks untuk INFOGRAFIS/PRESENTASI VISUAL. Buat naskah yang sangat terstruktur, gunakan BULLET POINTS atau penomoran slide (Slide 1, Slide 2, dst). Gunakan kalimat yang SUPER PADAT, JELAS, dan HINDARI paragraf panjang naratif. Fokus pada data dan *punchline*."

                    # Menyusun prompt yang lebih rapi ke Gemini beserta info tujuan
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
            # Menampilkan hasil
            st.markdown(st.session_state.hasil_naskah)

            st.divider()
            
            # Notifikasi yang lebih ramah dan menenangkan bagi orang awam
            st.info("💡 **Catatan:** Naskah di dalam kotak hitam di atas sudah dirancang khusus menggunakan susunan kata dan tanda baca (koma dan titik) agar dibaca secara natural oleh mesin. Sistem kami akan otomatis menarik naskah ini saat Anda menekan tombol pindah ke Studio Rekaman di bawah ini.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Buat Naskah Baru"):
                    st.session_state.hasil_naskah = ""
                    st.session_state.wizard_step = 1
                    st.rerun()
            with col2:
                if st.button("🚀 Pindah ke Studio Rekaman (VO)", use_container_width=True):
                    st.session_state.menu_aktif = "2. Studio Rekaman"
                    st.rerun()
