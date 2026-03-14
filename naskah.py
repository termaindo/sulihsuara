import streamlit as st
import google.generativeai as genai
import os

def run():
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

    # --- PROMPT DIREKTUR KREATIF (VERSI SSML ADVANCED) ---
    DIREKTUR_PROMPT = """
[PERAN]
Kamu adalah Direktur Kreatif Script Alih Suara. Kamu ahli dalam menyusun naskah yang menggunakan SSML (Speech Synthesis Markup Language) agar suara AI Google Wavenet terdengar natural, berjiwa, dan tidak kaku.

[ALUR KERJA]
Berdasarkan data wawancara, susunlah output sebagai berikut:

1. 💡 Alasan Kreatif:
Jelaskan dengan bahasa ramah kenapa naskah ini dibuat seperti ini.

2. 🎛️ Arahan Rekaman:
Berikan panduan tone dan suasana.

3. 🎙️ Naskah Final (Format SSML):
Kamu WAJIB membungkus naskah di dalam kotak kode (markdown code block).
Gunakan tag SSML untuk mengatur ritme. Contoh penggunaan yang harus kamu ikuti:
- Gunakan <break time="400ms"/> untuk jeda napas antar kalimat.
- Gunakan <prosody pitch="+2st" rate="1.1">teks</prosody> untuk kalimat yang antusias/promo.
- Gunakan <prosody pitch="-1st" rate="0.9">teks</prosody> untuk kalimat yang serius/berwibawa.
- Seluruh naskah harus diawali dengan <speak> dan diakhiri dengan </speak>.

PENTING: Pastikan teks di dalam SSML tetap bersih dan enak didengar.
    """

    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("📝 Ruang 1: Rapat Naskah Direktur Kreatif")

    if "wizard_step" not in st.session_state:
        st.session_state.wizard_step = 1
        st.session_state.jawaban = {"produk": "", "poin_penting": "", "durasi": "", "audiens": "", "vibe": "", "konteks": "", "tambahan": ""}
        st.session_state.hasil_naskah = ""

    # --- WIZARD STEPS (Sama seperti sebelumnya namun dengan pengumpulan data yang lebih ketat) ---
    if st.session_state.wizard_step == 1:
        st.subheader("Langkah 1 dari 6: Produk atau Jasa")
        pilihan = st.selectbox("Apa produk atau jasa yang ingin Anda buatkan narasinya?",
                               ["Pilih...", "Produk Kesehatan", "Makanan & Minuman", "Layanan Jasa", "Lainnya (Isi Sendiri)"])
        jawaban = st.text_input("Detail Produk:") if pilihan == "Lainnya (Isi Sendiri)" else pilihan
        if st.button("Selanjutnya ➡️") and jawaban != "Pilih...":
            st.session_state.jawaban["produk"] = jawaban
            st.session_state.wizard_step = 2
            st.rerun()

    elif st.session_state.wizard_step == 2:
        st.subheader("Langkah 2 dari 6: Keunggulan Utama")
        jawaban = st.text_area("Apa pesan kunci yang ingin ditonjolkan?")
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Kembali"): st.session_state.wizard_step = 1; st.rerun()
        if col2.button("Selanjutnya ➡️") and jawaban:
            st.session_state.jawaban["poin_penting"] = jawaban
            st.session_state.wizard_step = 3
            st.rerun()

    elif st.session_state.wizard_step == 3:
        st.subheader("Langkah 3 dari 6: Target Durasi")
        jawaban = st.selectbox("Durasi:", ["15 detik", "30 detik", "60 detik"])
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Kembali"): st.session_state.wizard_step = 2; st.rerun()
        if col2.button("Selanjutnya ➡️"):
            st.session_state.jawaban["durasi"] = jawaban
            st.session_state.wizard_step = 4
            st.rerun()

    elif st.session_state.wizard_step == 4:
        st.subheader("Langkah 4 dari 6: Target Audiens & Vibe")
        audiens = st.selectbox("Audiens:", ["Pensiunan/Lansia", "Profesional", "Gen Z", "Ibu Rumah Tangga"])
        vibe = st.selectbox("Vibe:", ["Tenang/Meyakinkan", "Energetik/Promo", "Hangat/Akrab"])
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Kembali"): st.session_state.wizard_step = 3; st.rerun()
        if col2.button("Selanjutnya ➡️"):
            st.session_state.jawaban["audiens"] = audiens
            st.session_state.jawaban["vibe"] = vibe
            st.session_state.wizard_step = 5
            st.rerun()

    elif st.session_state.wizard_step == 5:
        st.subheader("Langkah 5 dari 6: Rangkuman Akhir")
        st.write(st.session_state.jawaban)
        tambahan = st.text_input("Catatan Tambahan (Opsional):")
        col1, col2 = st.columns(2)
        if col1.button("⬅️ Kembali"): st.session_state.wizard_step = 4; st.rerun()
        if col2.button("✨ Hasilkan Naskah Berjiwa", type="primary"):
            st.session_state.jawaban["tambahan"] = tambahan
            st.session_state.wizard_step = 6
            st.rerun()

    elif st.session_state.wizard_step == 6:
        st.subheader("🎬 Hasil Penulisan Naskah Pro")
        if not st.session_state.hasil_naskah:
            with st.spinner("Direktur sedang menyusun naskah kreatif untuk Anda..."):
                model = genai.GenerativeModel("gemini-2.5-flash", system_instruction=DIREKTUR_PROMPT)
                prompt = f"Buat naskah kreatif untuk: {st.session_state.jawaban}"
                response = model.generate_content(prompt)
                st.session_state.hasil_naskah = response.text
                st.rerun()
        else:
            st.markdown(st.session_state.hasil_naskah)
            if st.button("🚀 Pindah ke Studio Rekaman"):
                st.session_state.menu_aktif = "2. Studio Rekaman"
                st.rerun()
