import streamlit as st
import re
import os
import json
import base64
import io
import google.generativeai as genai
from PIL import Image

# ==========================================
# 🧩 1. GOOGLE GEMINI (IMAGEN 3) IMAGE GENERATOR
# ==========================================
def generate_image_gemini(prompt, dimensi=""):
    """Menggunakan Google Imagen 3 untuk produksi gambar kualitas super."""
    try:
        aspect_ratio = "1:1"
        if "Portrait" in dimensi or "Vertical" in dimensi:
            aspect_ratio = "9:16"
        elif "Landscape" in dimensi:
            aspect_ratio = "16:9"

        imagen = genai.ImageGenerationModel("imagen-3.0-generate-001")
        result = imagen.generate_images(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio=aspect_ratio,
            output_mime_type="image/jpeg"
        )

        if not result.images:
            raise Exception("Gambar kosong dari server.")

        img_byte_arr = io.BytesIO()
        result.images[0].image.save(img_byte_arr, format='JPEG')
        encoded = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"

    except Exception as e:
        # Menangkap dan meneruskan pesan error asli dari Google ke sistem penanganan kita
        raise Exception(f"GEMINI_IMAGE_ERROR|{str(e)}")

# ==========================================
# 🧩 2. GOOGLE GEMINI (2.5 FLASH) JSON WRAPPER
# ==========================================
def generate_structured_text_gemini(prompt_text, opsi_slide, detail_topik, opsi_gaya):
    """Menghasilkan struktur JSON yang rapi untuk diolah ke HTML."""
    if "Realistik" in opsi_gaya:
        style_instruction = f"ultra-realistic photography, 8k resolution, cinematic lighting, conceptual aesthetic, completely textless, [KIASAN VISUAL UNTUK '{detail_topik}']"
    else:
        style_instruction = f"professional premium 2d vector illustration, modern colors, completely textless, [KIASAN VISUAL UNTUK '{detail_topik}']"

    slide_rule = ""
    if "1 Slide" in opsi_slide:
        slide_rule = "\n[ATURAN KHUSUS 1 SLIDE]: Rangkum menjadi SANGAT SINGKAT (Maks 4 poin utama)."

    system_prompt = f"""Kamu adalah Ahli Desain Visual Profesional.
TOPIK: {detail_topik}

Format output HARUS JSON valid dengan struktur:
{{
  "slides": [
    {{
      "slide_number": 1,
      "infographic_title": "Judul (Maks 6 Kata)",
      "image_prompt": "{style_instruction}",
      "items": [
        {{
          "icon_emoji": "💡",
          "title": "Sub Judul",
          "content": "Penjelasan maksimal 2 baris."
        }}
      ]
    }}
  ]
}}
ATURAN MUTLAK: 
1. Buat jumlah slide: {opsi_slide}.
2. image_prompt WAJIB berbahasa Inggris. {slide_rule}
3. DILARANG menyuruh AI menggambar teks/huruf pada image_prompt.
4. [SIASAT SENSOR GOOGLE SANGAT PENTING]: DILARANG KERAS menggunakan kata terkait manusia, organ tubuh, penyakit, obat, kesehatan, medis, darah, jarum, atau suplemen pada 'image_prompt'. Gunakan MURNI BENDA MATI ESTETIK (contoh: 'a glowing glass bottle on a marble table with soft studio lighting', 'a clean wooden desk with morning sunlight'). Ini agar gambar tidak diblokir sensor keamanan Google."""

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    try:
        model = genai.GenerativeModel(
            "gemini-2.5-flash",
            system_instruction=system_prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.4},
            safety_settings=safety_settings
        )
        response = model.generate_content(f"Teks Dasar:\n{prompt_text}")
        return json.loads(response.text)
    except Exception as e:
        raise Exception("FORMAT_JSON_RUSAK|Gagal memproses struktur visual.")

# ==========================================
# 🧩 3. WEB-BASED LAYOUT ENGINE (HTML/CSS MINIMALIS)
# ==========================================
def render_beautiful_html_poster(data_json, b64_images, opsi_dimensi):
    w_px, h_px = 1080, 1920
    if "Square" in opsi_dimensi:
        w_px, h_px = 1080, 1080
    elif "Landscape" in opsi_dimensi:
        w_px, h_px = 1920, 1080

    slides = data_json.get("slides", [])
    all_posters_html = ""
    
    for idx, slide in enumerate(slides):
        slide_num = slide.get("slide_number", idx + 1)
        b64_img = b64_images[idx] if idx < len(b64_images) else ""
        
        img_element = f'<img src="{b64_img}" class="hero-image" alt="Visual">' if b64_img else ""
            
        items_html = ""
        for item in slide.get("items", []):
            icon = item.get("icon_emoji", "✨")
            title = item.get("title", "Judul Poin")
            content = item.get("content", "Deskripsi poin.")
            items_html += f"""
            <div class="minimalist-item">
                <div class="item-icon">{icon}</div>
                <div class="item-text">
                    <div class="item-title">{title}</div>
                    <div class="item-desc">{content}</div>
                </div>
            </div>
            """
            
        poster_id = f"poster-container-{slide_num}"
        btn_id = f"btn-{slide_num}"
        
        if w_px > h_px:
            layout_html = f"""
            <div class="content-row">
                <div class="image-col">{img_element}</div>
                <div class="text-col">{items_html}</div>
            </div>
            """
        else:
            layout_html = f"""
            {img_element}
            <div class="text-col-vertical">{items_html}</div>
            """
        
        all_posters_html += f"""
        <div class="slide-wrapper">
            <div id="{poster_id}" class="poster-container">
                <div class="poster-body">
                    <div class="slide-indicator">SLIDE {slide_num}</div>
                    <h1 class="main-title">{slide.get("infographic_title", f"Slide {slide_num}")}</h1>
                    {layout_html}
                </div>
                
                <!-- STEMPEL PATEN 2 BARIS (Kontras, Font Sama Besar) -->
                <div class="stamp-footer">
                    <div class="stamp-line">Studio Kreatif Pro - KTB UKM JATIM</div>
                    <div class="stamp-line">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="stamp-icon"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                        @ktbukm.jatim
                        <span class="stamp-spacer">&nbsp;&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;&nbsp;</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="stamp-icon"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                        https://ktbukm-jatim.store
                    </div>
                </div>
            </div>
            <button id="{btn_id}" class="download-btn" onclick="downloadPoster('{poster_id}', '{btn_id}', {slide_num})">
                <span>⬇️</span> Download Slide {slide_num} (Kualitas Tinggi)
            </button>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; background-color: #f4f6f8; font-family: 'Plus Jakarta Sans', sans-serif; }}
            .slide-wrapper {{ margin-bottom: 50px; display: flex; flex-direction: column; align-items: center; width: 100%; }}
            .poster-container {{ background-color: #ffffff; width: {w_px}px; min-height: {h_px}px; display: flex; flex-direction: column; box-shadow: 0 20px 40px rgba(0,0,0,0.08); overflow: hidden; position: relative; }}
            .poster-body {{ padding: 60px; flex: 1; display: flex; flex-direction: column; }}
            .slide-indicator {{ color: #64748b; font-weight: 800; font-size: 20px; letter-spacing: 2px; margin-bottom: 15px; text-transform: uppercase; }}
            .main-title {{ color: #0f172a; font-size: 54px; font-weight: 800; line-height: 1.2; margin: 0 0 40px 0; letter-spacing: -1px; }}
            .content-row {{ display: flex; gap: 60px; align-items: center; flex: 1; }}
            .image-col {{ flex: 1; }}
            .text-col {{ flex: 1.2; display: flex; flex-direction: column; gap: 30px; }}
            .text-col-vertical {{ display: flex; flex-direction: column; gap: 30px; margin-top: 20px; }}
            .hero-image {{ width: 100%; height: auto; max-height: 800px; object-fit: contain; border-radius: 24px; }}
            .minimalist-item {{ display: flex; align-items: flex-start; gap: 20px; }}
            .item-icon {{ font-size: 45px; line-height: 1; }}
            .item-title {{ font-size: 28px; font-weight: 800; color: #1e293b; margin-bottom: 8px; }}
            .item-desc {{ font-size: 22px; font-weight: 500; color: #475569; line-height: 1.6; }}
            
            /* PENGATURAN STEMPEL MUTLAK SESUAI INSTRUKSI */
            .stamp-footer {{ background-color: #0f172a; width: 100%; padding: 30px 0; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; margin-top: auto; }}
            .stamp-line {{ color: #ffffff; font-size: 24px; font-weight: 700; display: flex; align-items: center; justify-content: center; }}
            .stamp-icon {{ margin-right: 8px; }}
            .stamp-spacer {{ color: #475569; }}
            
            .download-btn {{ margin-top: 25px; background-color: #0f172a; color: #ffffff; border: none; padding: 18px 35px; font-size: 18px; font-weight: 700; font-family: 'Plus Jakarta Sans', sans-serif; border-radius: 50px; cursor: pointer; transition: 0.2s; }}
            .download-btn:hover {{ background-color: #334155; transform: translateY(-2px); }}
        </style>
    </head>
    <body>
        {all_posters_html}
        <script>
            function downloadPoster(posterId, btnId, slideNum) {{
                const poster = document.getElementById(posterId);
                const btn = document.getElementById(btnId);
                btn.innerHTML = '⏳ Sedang Memproses...';
                
                html2canvas(poster, {{ scale: 1.5, useCORS: true, backgroundColor: "#ffffff" }}).then(canvas => {{
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum + ' (Kualitas Tinggi)';
                    let link = document.createElement('a');
                    link.download = 'Infografis_Kreatif_' + slideNum + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum;
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_template

# ==========================================
# 🧩 4. GENERATOR PROMPT MANUAL (COPTER UNTUK GEMINI PRIBADI)
# ==========================================
def create_manual_prompt(structured_data, topik, opsi_slide):
    """Menghasilkan prompt cerdas untuk di-copy paste ke Gemini oleh user gaptek."""
    slides = structured_data.get("slides", [])
    jumlah_slide = len(slides)
    
    prompt = "🌟 **LANGKAH 1: Berikan instruksi ini ke Gemini Anda:**\n\n"
    prompt += "```text\n"
    prompt += f"Halo Gemini, saya ingin membuat infografis tentang {topik}.\n"
    prompt += "Saya punya materi strukturnya. Tolong pahami dulu teks di bawah ini, tapi JANGAN buatkan gambarnya dulu. Cukup jawab 'Paham' jika kamu sudah membacanya.\n\n"
    
    for slide in slides:
        prompt += f"[SLIDE {slide.get('slide_number', '')}]\n"
        prompt += f"Judul Utama: {slide.get('infographic_title', '')}\n"
        for item in slide.get("items", []):
            prompt += f"• {item.get('title', '')}: {item.get('content', '')}\n"
        
        prompt += "\n"
        prompt += "Wajib ada teks stempel persis 2 baris ini di bagian paling bawah desain (font seragam, warna kontras):\n"
        prompt += "Baris 1: Studio Kreatif Pro - KTB UKM Jatim\n"
        prompt += "Baris 2: [Ikon IG] @ktbukm.jatim   [Ikon Website] [https://ktbukm-jatim.store](https://ktbukm-jatim.store)\n"
        prompt += "------------------------\n"
    prompt += "```\n\n"
    
    prompt += "🎨 **LANGKAH 2: Eksekusi Gambar (Penting!)**\n"
    prompt += "Setelah Gemini menjawab paham, masukkan instruksi pembuatan gambar ini "
    if jumlah_slide > 1:
        prompt += "**SATU PER SATU** (Jangan borongan agar hasilnya detail dan tidak buram):\n\n"
        for slide in slides:
            no = slide.get('slide_number', '')
            prompt += f"- Ketik ini untuk Slide {no}: `Tolong buatkan gambar infografisnya untuk SLIDE {no} saja sekarang, pastikan teks dan stempel bawahnya ditulis dengan rapi.`\n"
    else:
        prompt += "sekarang:\n\n"
        prompt += "- Ketik ini: `Tolong buatkan gambar infografisnya sekarang berdasarkan materi di atas. Pastikan teks dan stempel bawahnya ditulis dengan rapi.`\n"

    return prompt

# ==========================================
# 🚀 MAIN APP RUNNER
# ==========================================
def run():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error("Kredensial Gemini API Key bermasalah.")
        st.stop()

    st.title("🎨 Ruang 3: Studio Kreasi Cetak / Visual")
    st.info("💡 **Informasi:** Studio ini ditenagai oleh Kecerdasan Buatan (AI) Desain Visual Profesional tingkat lanjut untuk merangkai tata letak dan gambar berkualitas tinggi secara otomatis.")

    raw_text = st.session_state.get("hasil_naskah", "")
    if not raw_text:
        st.warning("Belum ada naskah yang ditarik. Silakan buat naskah terlebih dahulu di Ruang 1 (Studio Kreasi Naskah).")
        return

    naskah_final = raw_text
    bt = chr(96) * 3 
    pattern = rf"{bt}(?:text|markdown|xml)?\n(.*?)({bt})"
    match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_naskah:
        naskah_final = match_naskah.group(1).strip()
        st.success("✅ Naskah dasar berhasil ditarik otomatis dari Studio Kreasi Naskah!")

    st.markdown("### 🎛️ Pengaturan Sistem & Desain")
    
    col1, col2 = st.columns(2)
    with col1:
        opsi_dimensi = st.selectbox(
            "1. Ukuran Poster / Platform:", 
            [
                "1080 x 1920 px (Vertical / IG Story / TikTok) - DIREKOMENDASIKAN",
                "1080 x 1080 px (Square / IG Feed)",
                "1920 x 1080 px (Landscape / Presentasi PPT / YouTube)"
            ], index=0
        )
        opsi_gaya = st.selectbox(
            "2. Gaya Visual / Ilustrasi:",
            [
                "📸 Gaya Foto Realistik (Nyata, Konseptual & Profesional)",
                "🎨 Gaya Lukisan (Vektor / Ilustrasi Digital Cerdas)"
            ], index=0
        )
        
    with col2:
        opsi_slide = st.selectbox(
            "3. Mode Format Poster:", 
            [
                "1 Slide (1 Poster Panjang, Teks Sangat Padat)", 
                "2 Slide (Carousel Pendek)",
                "3 Slide (Carousel Menengah)",
                "5 Slide (Carousel Panjang)"
            ], index=0
        )

    st.divider()
    
    st.markdown("### 📸 Upload Gambar Produk (SANGAT DISARANKAN)")
    st.info("💡 **Tips Anti Gagal:** Jika Anda sudah memiliki foto produk sendiri, mengunggahnya di sini akan **menjamin 100% desain jadi seketika** dengan tata letak minimalis premium, tanpa harus memanggil AI pelukis.")
    
    uploaded_file = st.file_uploader("Upload Foto Asli Anda di sini (Format: PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

    st.divider()
    st.markdown("### 📝 Naskah Dasar")
    user_input = st.text_area("Draft Naskah yang akan diproses AI:", value=naskah_final, height=150)

    if st.button("✨ Hasilkan Poster Berkualitas", use_container_width=True, type="primary"):
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Art Director AI sedang merancang tata letak..."):
            try:
                produk_name = st.session_state.jawaban.get("produk", "Produk Utama")
                merk_name = st.session_state.jawaban.get("merk", "")
                detail_topik = f"{merk_name} {produk_name}".strip()
                
                structured_data = generate_structured_text_gemini(user_input, opsi_slide, detail_topik, opsi_gaya)
                manual_prompt_text = create_manual_prompt(structured_data, detail_topik, opsi_slide)
                
                slides = structured_data.get("slides", [])
                total_slides = len(slides)
                b64_images = []
                
                user_b64_img = ""
                if uploaded_file is not None:
                    img_bytes = uploaded_file.getvalue()
                    b64_encoded = base64.b64encode(img_bytes).decode('utf-8')
                    user_b64_img = f"data:{uploaded_file.type};base64,{b64_encoded}"

                try:
                    for idx, slide in enumerate(slides):
                        slide_num = slide.get("slide_number", idx + 1)
                        if user_b64_img:
                            b64_images.append(user_b64_img)
                        else:
                            base_prompt = slide.get("image_prompt", f"ultra-realistic photography for {detail_topik}")
                            safe_prompt = f"{base_prompt}, clean background"
                            with st.spinner(f"📸 Pelukis AI Google sedang memproduksi visual Slide {slide_num}/{total_slides}..."):
                                b64_img = generate_image_gemini(safe_prompt, opsi_dimensi)
                                b64_images.append(b64_img)
                                
                    with st.spinner("📐 Web Layout Engine sedang merakit Poster Minimalis Elegan..."):
                        final_html = render_beautiful_html_poster(structured_data, b64_images, opsi_dimensi)
                        if user_b64_img:
                            st.success(f"🎉 {total_slides} Poster berhasil dirender menggunakan FOTO ASLI ANDA!")
                        else:
                            st.success(f"🎉 {total_slides} Poster berhasil dirender dengan Mesin Google Imagen!")
                        
                        h_px = 1920 if "Vertical" in opsi_dimensi else (1080 if "Square" in opsi_dimensi else 1080)
                        iframe_height = total_slides * (h_px + 100)
                        st.components.v1.html(final_html, height=iframe_height, scrolling=True)
                        
                except Exception as img_err:
                    error_msg = str(img_err).lower()
                    
                    if "403" in error_msg or "permission" in error_msg or "unsupported" in error_msg:
                        pesan_awam = "Google membatasi akses fitur pembuat gambar (Imagen 3) untuk versi akun API gratis Anda di wilayah ini."
                    elif "429" in error_msg or "quota" in error_msg or "exhausted" in error_msg:
                        pesan_awam = "Kuota gratis harian Anda untuk membuat gambar dari server Google sudah habis hari ini."
                    elif "safety" in error_msg or "blocked" in error_msg or "content" in error_msg:
                        pesan_awam = "Filter keamanan ketat Google menolak instruksi gambar karena dianggap mengandung kata sensitif/medis."
                    else:
                        pesan_awam = "Server penggambar Google sedang mengalami gangguan teknis atau terlalu sibuk."

                    st.error(f"⏳ **Mesin Gambar Google Terkendala!**\n\n**Penyebab:** {pesan_awam}")
                    
                    st.info("💡 **SOLUSI INSTAN:** Jangan khawatir! Anda tetap bisa membuat desain 100% utuh detik ini juga dengan cara menggunakan fitur **'Upload Gambar Produk'** di bagian atas (menggunakan foto Anda sendiri), ATAU menyalin instruksi praktis di bawah ini ke ChatGPT / Gemini pribadi Anda.")

                # 4. TAMPILAN PROMPT MANUAL
                st.divider()
                st.markdown("### 🤖 Instruksi Praktis (Copas ke Gemini Pribadi Anda)")
                st.info("Jika Anda tidak punya foto sendiri untuk di-upload, Anda bisa memerintahkan aplikasi Gemini biasa di HP/Laptop Anda untuk membuatkannya. Cukup **Salin (Copy)** teks di bawah ini dan **Tempel (Paste)** bertahap sesuai petunjuk:")
                st.markdown(manual_prompt_text) 

            except Exception as e:
                gemini_err_msg = str(e)
                if "FORMAT_JSON_RUSAK" in gemini_err_msg:
                    st.error("⏳ **Mesin AI Teks Sedang Memproses Ulang:** Gagal merapikan tata letak naskah Anda. Silakan klik tombol **Hasilkan Poster Berkualitas** sekali lagi.")
                else:
                    st.error("❌ **Terjadi Gangguan Komunikasi dengan Server AI Google.** Silakan periksa koneksi internet atau coba kembali dalam beberapa saat.")

    st.divider()
    st.markdown("### 🚀 Lanjut Produksi Karya Lain")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🎙️ Ke Studio Kreasi Suara / Audio", use_container_width=True):
            st.session_state.menu_aktif = "2. Studio Kreasi Suara / Audio"
            st.rerun()
    with col_nav2:
        if st.button("📝 Kembali ke Studio Kreasi Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Studio Kreasi Naskah"
            st.rerun()
