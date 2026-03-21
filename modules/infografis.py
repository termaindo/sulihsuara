import streamlit as st
import re
import os
import json
import requests
import base64
import time

# ==========================================
# 🧩 1. HUGGING FACE IMAGE GENERATOR (MULTI-MODEL FALLBACK)
# ==========================================
def generate_image_with_retry(prompt, dimensi=""):
    """Menggunakan model FLUX.1. Jika gagal/sibuk, fallback ke SDXL."""
    hf_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not hf_key:
        return None
        
    headers = {"Authorization": f"Bearer {hf_key}"}
    
    # Resolusi disesuaikan dengan proporsi poster
    w, h = 1024, 1024 
    if "Portrait" in dimensi or "Vertical" in dimensi:
        w, h = 896, 1152 
    elif "Landscape" in dimensi:
        w, h = 1152, 896

    payload = {
        "inputs": prompt,
        "parameters": {
            "width": w,
            "height": h
        }
    }
    
    # Daftar mesin dari yang paling bagus ke mesin cadangan
    models_to_try = [
        "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell",
        "https://router.huggingface.co/hf-inference/models/stabilityai/stable-diffusion-xl-base-1.0"
    ]
    
    last_error = ""
    for api_url in models_to_try:
        for attempt in range(2):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=40)
                if response.status_code == 200:
                    encoded = base64.b64encode(response.content).decode('utf-8')
                    return f"data:image/png;base64,{encoded}"
                elif response.status_code == 503:
                    time.sleep(5) 
                    continue
                else:
                    last_error = response.text
                    break # Gagal di model ini, pindah ke model cadangan
            except Exception as e:
                time.sleep(3)
                continue
                
    st.error(f"Mesin Pelukis AI Server Publik sedang penuh/habis kuota. Detail: {last_error}")
    return None

# ==========================================
# 🧩 2. GROQ Llama 3.3 70B WRAPPER
# ==========================================
def generate_structured_text_groq(prompt_text, opsi_slide, detail_topik, opsi_gaya):
    """Menggunakan Groq untuk memproduksi Multi-Slide Array."""
    groq_key = st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY tidak ditemukan di st.secrets!")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    if "Realistik" in opsi_gaya:
        style_instruction = f"ultra-realistic photography, 8k resolution, cinematic lighting, highly conceptual aesthetic, [DESKRIPSI VISUAL KREATIF UNTUK '{detail_topik}'], completely textless"
        style_rule = f"2. 'image_prompt' WAJIB FOTO REALISTIK PREMIUM. Baca isi naskah dan buat gambaran KONSEPTUAL!\n- Jika topiknya Aplikasi: Gambarkan model profesional menatap tersenyum ke smartphone (layar tidak terlihat).\n- Jika topiknya Konsep: Gunakan metafora visual premium."
    else:
        style_instruction = f"professional premium 2d vector illustration, clean lines, modern colors, highly conceptual metaphor, [DESKRIPSI VISUAL KREATIF UNTUK '{detail_topik}'], completely textless"
        style_rule = f"2. 'image_prompt' WAJIB LUKISAN VEKTOR PREMIUM. Baca naskah dan buat gambaran KONSEPTUAL!"

    slide_rule = ""
    if "1 Slide" in opsi_slide:
        slide_rule = "\n[ATURAN KHUSUS 1 SLIDE]: Kamu WAJIB merangkum teks menjadi SANGAT SINGKAT dan PADAT (Maksimal 4-5 poin utama)."

    system_prompt = f"""Kamu adalah Ahli Desain Visual dan Prompt Engineer Profesional.
FOKUS UTAMA MATERI: {detail_topik}

Tugasmu memecah teks menjadi FORMAT MULTI-SLIDE infografis padat.
Format output HARUS JSON valid dengan struktur array 'slides' berikut:
{{
  "slides": [
    {{
      "slide_number": 1,
      "infographic_title": "Judul Utama (Maks 6 Kata)",
      "image_prompt": "{style_instruction}",
      "items": [
        {{
          "icon_emoji": "💡",
          "title": "Sub Judul",
          "content": "Penjelasan singkat maks 2 baris."
        }}
      ]
    }}
  ]
}}
ATURAN MUTLAK KUALITAS VISUAL PREMIUM: 
1. Buat jumlah slide TEPAT sesuai permintaan: {opsi_slide}.
{style_rule}
3. Gunakan Emoji yang sangat relevan di tiap "icon_emoji".{slide_rule}
4. DILARANG KERAS menyuruh AI menggambar kata, huruf, UI aplikasi, atau papan tulis.
5. Akhiri image_prompt dengan kata: "completely textless, clean blank surface"."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Teks Dasar:\n{prompt_text}"}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.5
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        content_str = result["choices"][0]["message"]["content"]
        return json.loads(content_str)
    else:
        raise Exception(f"Gagal menghubungi Groq: {response.text}")

# ==========================================
# 🧩 3. WEB-BASED LAYOUT ENGINE (DISIPLIN PIKSEL)
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
            <div class="card">
                <div class="card-icon">{icon}</div>
                <div class="card-text">
                    <div class="card-title">{title}</div>
                    <div class="card-desc">{content}</div>
                </div>
            </div>
            """
            
        poster_id = f"poster-container-{slide_num}"
        btn_id = f"btn-{slide_num}"
        
        if w_px > h_px:
            layout_html = f"""
            <div style="display: flex; gap: 50px; align-items: center; flex: 1;">
                <div style="flex: 1;">{img_element}</div>
                <div style="flex: 1.2;" class="cards-wrapper">{items_html}</div>
            </div>
            """
        else:
            layout_html = f"""
            {img_element}
            <div class="cards-wrapper">{items_html}</div>
            """
        
        all_posters_html += f"""
        <div class="slide-wrapper">
            <div id="{poster_id}" class="poster-container">
                <div class="slide-badge">SLIDE {slide_num}</div>
                <h1 class="header-title">{slide.get("infographic_title", f"Slide {slide_num}")}</h1>
                
                {layout_html}
                
                <div class="footer-note">
                    <div>STUDIO KREATIF PRO • KTB UKM JATIM</div>
                    <div class="footer-social">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="social-icon"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                        <span>@ktbukm.jatim</span>
                        <span class="social-divider">•</span>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="social-icon"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                        <span>https://ktbukm-jatim.store</span>
                    </div>
                </div>
            </div>
            <button id="{btn_id}" class="download-btn" onclick="downloadPoster('{poster_id}', '{btn_id}', {slide_num})">
                <span>⬇️</span> Download Slide {slide_num} (Resolusi Tinggi)
            </button>
        </div>
        """

    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;800&family=Nunito:wght@500;700&display=swap');
            body {{ margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; background-color: #eef2f5; }}
            .slide-wrapper {{ margin-bottom: 60px; display: flex; flex-direction: column; align-items: center; width: 100%; overflow-x: auto; }}
            .poster-container {{ background: linear-gradient(135deg, #f0fbff 0%, #c4f0f6 100%); width: {w_px}px; min-height: {h_px}px; padding: 60px 80px; box-sizing: border-box; font-family: 'Nunito', sans-serif; position: relative; display: flex; flex-direction: column; }}
            .slide-badge {{ position: absolute; top: 20px; left: 20px; background-color: #ff5722; color: white; padding: 10px 25px; border-radius: 30px; font-family: 'Montserrat', sans-serif; font-size: 18px; font-weight: 800; }}
            .header-title {{ font-family: 'Montserrat', sans-serif; font-size: 55px; color: #004d40; text-align: center; margin-top: 20px; margin-bottom: 50px; line-height: 1.2; text-transform: uppercase; text-shadow: 2px 2px 4px rgba(0,0,0,0.05); }}
            .hero-image {{ width: 100%; height: 550px; object-fit: cover; border-radius: 40px; margin: 0 auto 50px auto; display: block; box-shadow: 0 15px 30px rgba(0,0,0,0.15); border: 10px solid white; background-color: white; }}
            .cards-wrapper {{ display: flex; flex-direction: column; gap: 25px; flex: 1; }}
            .card {{ background-color: white; border-radius: 25px; padding: 30px 40px; display: flex; align-items: flex-start; box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-left: 15px solid #00acc1; height: auto; }}
            .card-icon {{ font-size: 65px; margin-right: 30px; line-height: 1; }}
            .card-text {{ flex: 1; min-width: 0; }}
            .card-title {{ font-family: 'Montserrat', sans-serif; font-size: 28px; color: #00838f; margin-bottom: 10px; font-weight: 800; word-wrap: break-word; overflow-wrap: break-word; white-space: normal; line-height: 1.3; }}
            .card-desc {{ font-size: 22px; color: #455a64; line-height: 1.5; margin: 0; word-wrap: break-word; overflow-wrap: break-word; }}
            .footer-note {{ margin-top: auto; padding-top: 50px; text-align: center; color: #00838f; font-weight: 800; font-size: 22px; letter-spacing: 2px; font-family: 'Montserrat', sans-serif; }}
            .footer-social {{ display: flex; justify-content: center; align-items: center; margin-top: 10px; font-size: 22px; font-weight: 800; letter-spacing: 1px; color: #00838f; }}
            .social-icon {{ margin-right: 6px; }}
            .social-divider {{ margin: 0 15px; color: #00838f; }}
            .download-btn {{ margin-top: 25px; background-color: #ff5722; color: white; border: none; padding: 20px 40px; font-size: 20px; font-family: 'Montserrat', sans-serif; border-radius: 40px; cursor: pointer; box-shadow: 0 8px 20px rgba(255, 87, 34, 0.4); font-weight: bold; }}
            .download-btn:hover {{ background-color: #e64a19; }}
        </style>
    </head>
    <body>
        {all_posters_html}
        <script>
            function downloadPoster(posterId, btnId, slideNum) {{
                const poster = document.getElementById(posterId);
                const btn = document.getElementById(btnId);
                const badge = poster.querySelector('.slide-badge');
                if(badge) badge.style.display = 'none';
                
                btn.innerHTML = '⏳ Memproses Resolusi Tinggi...';
                btn.style.backgroundColor = '#757575';
                
                html2canvas(poster, {{ scale: 1, useCORS: true, backgroundColor: null }}).then(canvas => {{
                    if(badge) badge.style.display = 'block'; 
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum;
                    btn.style.backgroundColor = '#ff5722';
                    
                    let link = document.createElement('a');
                    link.download = 'Infografis_Kreatif_' + slideNum + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    if(badge) badge.style.display = 'block';
                    alert("Gagal memproses gambar.");
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum;
                    btn.style.backgroundColor = '#ff5722';
                }});
            }}
        </script>
    </body>
    </html>
    """
    return html_template

# ==========================================
# 🚀 MAIN APP RUNNER
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Ditenagai Groq Llama 3.3 70B & Hugging Face.**")

    raw_text = st.session_state.get("hasil_naskah", "")
    if not raw_text:
        st.warning("Belum ada naskah yang ditarik. Silakan buat naskah terlebih dahulu di Ruang 1 (Rapat Naskah).")
        return

    naskah_final = raw_text
    bt = chr(96) * 3 
    pattern = rf"{bt}(?:text|markdown|xml)?\n(.*?)({bt})"
    match_naskah = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
    
    if match_naskah:
        naskah_final = match_naskah.group(1).strip()
        st.success("✅ Naskah dasar berhasil ditarik otomatis dari Ruang 1!")

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
    
    # === FITUR UPLOAD GAMBAR DENGAN TAMPILAN JELAS DAN BESAR ===
    st.markdown("### 📸 Upload Gambar Produk (SANGAT DISARANKAN)")
    st.info("💡 **Tips Anti Gagal:** Mengunggah foto produk atau screenshot aplikasi Anda sendiri di sini akan **menjamin 100% desain jadi tanpa error/kosong**. Server lukis publik sering kali penuh atau kehabisan kuota!")
    
    uploaded_file = st.file_uploader("Upload Foto Asli Anda di sini (Format: PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])

    st.divider()
    st.markdown("### 📝 Naskah Dasar")
    user_input = st.text_area("Draft Naskah yang akan diproses AI:", value=naskah_final, height=150)

    # === TOMBOL EKSEKUSI ===
    if st.button("✨ Hasilkan Poster Berkualitas", use_container_width=True, type="primary"):
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Art Director AI sedang merancang tata letak..."):
            try:
                # 0. Proses Gambar Upload Manual
                user_b64_img = ""
                if uploaded_file is not None:
                    img_bytes = uploaded_file.getvalue()
                    b64_encoded = base64.b64encode(img_bytes).decode('utf-8')
                    user_b64_img = f"data:{uploaded_file.type};base64,{b64_encoded}"

                # Menarik konteks produk
                produk_name = st.session_state.jawaban.get("produk", "Produk Utama")
                merk_name = st.session_state.jawaban.get("merk", "")
                detail_topik = f"{merk_name} {produk_name}".strip()
                
                # 1. Analisis Naskah dengan Groq
                structured_data = generate_structured_text_groq(user_input, opsi_slide, detail_topik, opsi_gaya)
                slides = structured_data.get("slides", [])
                total_slides = len(slides)
                
                b64_images = []
                
                # 2. Logika Gambar: Pakai Upload Manual ATAU Lukis Pakai AI
                for idx, slide in enumerate(slides):
                    slide_num = slide.get("slide_number", idx + 1)
                    
                    if user_b64_img:
                        # Langsung gunakan gambar dari user (Dijamin 100% Cepat & Berhasil)
                        b64_images.append(user_b64_img)
                    else:
                        base_prompt = slide.get("image_prompt", f"ultra-realistic photography for {detail_topik}")
                        safe_prompt = f"{base_prompt}, completely textless, no letters, no words, clean surface"
                        
                        with st.spinner(f"📸 Pelukis AI sedang memproduksi visual Slide {slide_num}/{total_slides}..."):
                            b64_img = generate_image_with_retry(safe_prompt, opsi_dimensi)
                            
                            # Jika AI gagal/sibuk dan user TIDAK upload foto, hentikan proses agar tidak muncul poster kosong
                            if not b64_img:
                                st.warning(f"⚠️ Server AI Pelukis gagal memuat gambar untuk Slide {slide_num}.")
                                st.error("💡 Solusi Tercepat: Silakan UPLOAD FOTO PRODUK Anda secara manual di menu kotak 'Upload Gambar Produk' di atas, lalu klik tombol Hasilkan Poster lagi.")
                                st.stop()
                                
                            b64_images.append(b64_img)
                
                with st.spinner("📐 Web Layout Engine sedang merakit Poster Resolusi Tinggi..."):
                    # 3. Merakit HTML/CSS Kualitas Tinggi
                    final_html = render_beautiful_html_poster(structured_data, b64_images, opsi_dimensi)
                    
                    if user_b64_img:
                        st.success(f"🎉 {total_slides} Poster berhasil dirender menggunakan FOTO ASLI ANDA!")
                    else:
                        st.success(f"🎉 {total_slides} Poster berhasil dirender dengan AI!")
                    
                    # 4. Tampilkan HTML Interaktif
                    h_px = 1920 if "Vertical" in opsi_dimensi else (1080 if "Square" in opsi_dimensi else 1080)
                    iframe_height = total_slides * (h_px + 200)
                    
                    st.components.v1.html(final_html, height=iframe_height, scrolling=True)

            except Exception as e:
                st.error(f"❌ Terjadi kesalahan pada proses generasi: {str(e)}")

    st.divider()
    st.markdown("### 🚀 Lanjut Produksi Karya Lain")
    
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        if st.button("🎙️ Ke Studio Rekaman (VO)", use_container_width=True):
            st.session_state.menu_aktif = "2. Studio Rekaman"
            st.rerun()
    with col_nav2:
        if st.button("📝 Kembali ke Ruang Naskah", use_container_width=True):
            st.session_state.menu_aktif = "1. Ruang Naskah"
            st.rerun()
