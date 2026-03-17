import streamlit as st
import re
import google.generativeai as genai
import os
import requests
import base64

def run():
    # --- 1. KARANTINA MEMORI SISTEM & SETUP GEMINI ---
    os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
    try:
        gemini_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=gemini_key)
    except Exception as e:
        st.error(f"Kredensial Gemini bermasalah: {e}")
        st.stop()

    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Informasi:** Studio ini memakai bantuan AI untuk memecah naskah Anda menjadi lembar kerja visual (*blueprint* desain). Ini akan memudahkan Anda menyalin-tempel (*copy-paste*) teks ke aplikasi desain seperti Canva, Photoshop, atau Illustrator.")

    # Inisialisasi State untuk Hasil Blueprint
    if "blueprint_infografis" not in st.session_state:
        st.session_state.blueprint_infografis = ""

    # --- 2. TARIK NASKAH DARI STATE ---
    raw_text = st.session_state.get("hasil_naskah", "")
    
    if not raw_text:
        st.warning("Belum ada naskah yang ditarik. Silakan buat naskah terlebih dahulu di Ruang 1 (Rapat Naskah).")
        return

    # --- 3. EKSTRAKSI TEKS DARI KOTAK MARKDOWN ---
    naskah_final = raw_text
    bt = "```" 
    pattern = rf"{bt}(?:text|markdown|xml)?\n(.*?)({bt})"
    match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_naskah:
        naskah_final = match_naskah.group(1).strip()
        st.success("✅ Naskah dasar berhasil ditarik dari Ruang 1!")
    else:
        st.info("💡 Naskah ditarik tanpa filter blok kode.")

    # --- 4. FILTER DROPDOWN PENGATURAN DESAIN ---
    st.markdown("### 🎛️ Pengaturan Format Desain")
    col1, col2 = st.columns(2)
    with col1:
        opsi_slide = st.selectbox(
            "1. Jumlah Slide / Tampilan:", 
            [
                "Pilih...",
                "Otomatis (Sesuai panjang teks)",
                "1 Halaman Penuh (Poster/Infografis Panjang)",
                "3 Slide (Carousel Singkat)",
                "5 Slide (Carousel Standar)",
                "7 Slide (Carousel Edukasi)",
                "10 Slide (Carousel Maksimal Instagram)"
            ]
        )
    with col2:
        opsi_dimensi = st.selectbox(
            "2. Ukuran Dimensi:", 
            [
                "Pilih...",
                "1080 x 1080 px (Square / IG Feed)",
                "1080 x 1350 px (Portrait / IG Feed)",
                "1080 x 1920 px (Vertical / IG Story / TikTok)",
                "1920 x 1080 px (Landscape / Presentasi PPT / YouTube)"
            ]
        )

    st.divider()

    # --- 5. RANGKUMAN POIN PENTING (KOTAK KERJA) ---
    st.markdown("### 📝 Rangkuman Poin Penting (Draft)")
    st.write("Berikut adalah naskah mentah Anda. Anda bisa mengedit atau menambahkan catatan khusus di sini sebelum AI mengubahnya menjadi format *slide*.")
    
    user_input = st.text_area(
        "Kotak Kerja Draft Naskah:", 
        value=naskah_final, 
        height=200,
        help="Edit poin-poin penting di sini sebelum menekan tombol pembuatan."
    )

    # --- 6. PROSES PEMBUATAN INFOGRAFIS OLEH AI ---
    if st.button("✨ Buat Blueprint Infografis Sekarang", use_container_width=True, type="primary"):
        if opsi_slide == "Pilih..." or opsi_dimensi == "Pilih...":
            st.warning("⚠️ Mohon pilih jumlah slide dan ukuran dimensi terlebih dahulu!")
        elif not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
        else:
            with st.spinner("Desainer AI sedang memecah teks dan menyusun tata letak (layout)..."):
                try:
                    # Instruksi khusus untuk AI Desainer (Telah dioptimasi agar mematuhi jumlah slide dan format teks)
                    PROMPT_DESAINER = f"""
                    Kamu adalah Ahli Desain Visual dan Copywriter Media Sosial profesional.
                    Tugasmu adalah mengubah teks/draft mentah menjadi blueprint (panduan desain) yang siap di-copy-paste ke Canva/Photoshop.

                    PANDUAN STRUKTUR DESAIN:
                    - Target Jumlah Slide: {opsi_slide} (ATURAN MUTLAK: Kamu WAJIB mematuhi instruksi jumlah slide ini. Jika pengguna memilih "1 Halaman Penuh", kamu HANYA BOLEH merangkum semuanya ke dalam 1 Slide/Halaman saja).
                    - Dimensi Desain: {opsi_dimensi}
                    
                    ATURAN MUTLAK FORMAT OUTPUT:
                    1. Pecah teks mentah ke dalam bagian yang sesuai dengan target jumlah slide (Slide 1, Slide 2, dst).
                    2. JANGAN menggunakan terlalu banyak cetak tebal (bold/markdown **). Gunakan huruf normal biasa untuk Teks Utama agar rapi saat disalin.
                    3. Untuk setiap Slide/Halaman, WAJIB memiliki format baku seperti ini:
                       
                       ### 🖼️ Slide [Nomor]
                       **Judul Besar:** [Headline singkat yang memancing mata]
                       **Teks Utama:** [Isi konten berupa paragraf singkat atau poin-poin dengan huruf normal (tanpa cetak tebal)]
                       **Saran Visual:** [Saran singkat ikon, gambar latar, atau warna yang cocok]
                       ---
                       
                    4. Pastikan teks sangat *to-the-point*, hapus kata-kata berbunga-bunga yang tidak cocok untuk format gambar visual. Tuliskan dalam bahasa Indonesia yang memikat.
                    """

                    model_desainer = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        system_instruction=PROMPT_DESAINER
                    )
                    
                    response = model_desainer.generate_content(f"Draft Naskah:\n{user_input}")
                    st.session_state.blueprint_infografis = response.text
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyusun infografis: {e}")

    # --- 7. TAMPILAN HASIL AKHIR & CETAK GAMBAR ---
    if st.session_state.blueprint_infografis:
        st.success("🎉 Blueprint Infografis berhasil dibuat!")
        
        # Menampilkan dalam wadah dengan latar belakang yang jelas
        with st.container(border=True):
            st.markdown(st.session_state.blueprint_infografis)
            
        st.info("💡 **Tips:** Anda sekarang bisa memblok (highlight) teks di masing-masing slide di atas, lalu menyalinnya (Copy) ke dalam template presentasi atau desain media sosial Anda.")
        
        st.divider()
        st.markdown("### 🖼️ Cetak Gambar Otomatis (AI Image Generation)")
        st.write("Berdasarkan blueprint di atas, AI dapat mencoba melukiskan ilustrasi desain (poster tunggal) secara langsung untuk Anda.")
        
        if st.button("🖼️ Cetak Gambar Infografis Sekarang", use_container_width=True):
            with st.spinner("Mesin AI sedang melukis gambar Anda... (Ini memakan waktu beberapa detik)"):
                try:
                    # 1. Terjemahkan blueprint menjadi prompt bahasa inggris yang kuat untuk Image Generator
                    model_prompt = genai.GenerativeModel("gemini-2.5-flash")
                    prompt_en = model_prompt.generate_content(
                        f"Create a highly detailed image generation prompt in English for an infographic poster based on this text. Make it visually appealing, modern, clean, with appropriate colors and layout. Include dummy text elements. Limit to 1 paragraph. Text:\n{st.session_state.blueprint_infografis}"
                    ).text

                    # 2. Panggil API Image Generation Google (URL telah dibersihkan secara total)
                    api_key = st.secrets["GEMINI_API_KEY"]
                    url = f"[https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=](https://generativelanguage.googleapis.com/v1beta/models/imagen-4.0-generate-001:predict?key=){api_key}"
                    headers = {'Content-Type': 'application/json'}
                    payload = {
                        "instances": [{"prompt": prompt_en}],
                        "parameters": {"sampleCount": 1}
                    }
                    
                    response = requests.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    
                    # 3. Ekstrak base64 gambar dan konversi
                    result = response.json()
                    b64_img = result['predictions'][0]['bytesBase64Encoded']
                    img_bytes = base64.b64decode(b64_img)
                    
                    st.success("✅ Gambar berhasil dicetak!")
                    st.image(img_bytes, caption="Hasil Cetak Infografis AI (Ilustrasi Visual)")
                    
                    # Tombol Download Gambar
                    st.download_button(
                        label="⬇️ Download Gambar (PNG)",
                        data=img_bytes,
                        file_name="infografis_ai.png",
                        mime="image/png",
                        use_container_width=True,
                        type="primary"
                    )
                    
                except Exception as e:
                    st.error(f"Gagal mencetak gambar: {e}")
