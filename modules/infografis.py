import streamlit as st
import re
import os
import json
import requests
import base64
import time

# ==========================================
# 🧩 1. HUGGING FACE IMAGE GENERATOR (FLUX)
# ==========================================
def generate_image_with_retry(prompt, dimensi=""):
    """Menggunakan model FLUX.1 dengan URL Router Hugging Face terbaru."""
    hf_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not hf_key:
        st.warning("⚠️ Kunci HUGGINGFACE_API_KEY tidak ditemukan!")
        return None
        
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
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
    
    for attempt in range(3):
        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=40)
            if response.status_code == 200:
                encoded = base64.b64encode(response.content).decode('utf-8')
                return f"data:image/png;base64,{encoded}"
            elif response.status_code == 503:
                time.sleep(5) 
                continue
            else:
                return None
        except Exception as e:
            time.sleep(3)
            continue
            
    return None

# ==========================================
# 🧩 2. GROQ Llama 3.3 70B WRAPPER
# ==========================================
def generate_structured_text_groq(prompt_text, opsi_slide, detail_topik, opsi_gaya):
    """
    Menggunakan Groq untuk memproduksi Multi-Slide Array,
    dengan instruksi Dinamis (Realistik/Lukisan & Kepadatan Teks).
    """
    groq_key = st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY tidak ditemukan di st.secrets!")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    # Penentuan Gaya Gambar
    if "Realistik" in opsi_gaya:
        style_instruction = f"ultra-realistic product photography, 8k resolution, photorealistic, cinematic lighting, [DESKRIPSI FISIK BENDA NYATA DARI PRODUK '{detail_topik}'], clean minimalist studio background"
        style_rule = f"2. Isian 'image_prompt' WAJIB FOTOGRAFI REALISTIK (BUKAN LUKISAN) dan FOKUS pada Produk Utama ({detail_topik})."
    else:
        style_instruction = f"professional 2d vector illustration, flat design, clean lines, vibrant colors, minimalist infographic style, [DESKRIPSI VISUAL ILUSTRASI DARI PRODUK '{detail_topik}']"
        style_rule = f"2. Isian 'image_prompt' WAJIB GAYA LUKISAN/VEKTOR ILUSTRASI dan FOKUS pada Produk Utama ({detail_topik})."

    # Penentuan Kepadatan Teks Khusus 1 Slide
    slide_rule = ""
    if "1 Slide" in opsi_slide:
        slide_rule = "\n[ATURAN KHUSUS 1 SLIDE]: Pengguna meminta 1 Halaman Penuh. Kamu WAJIB merangkum teks menjadi SANGAT SINGKAT dan PADAT (Maksimal 4-5 poin utama). JANGAN gunakan kalimat panjang agar tata letak poster tidak sesak/penuh!"

    system_prompt = f"""Kamu adalah Ahli Desain Visual dan Prompt Engineer Profesional.
FOKUS UTAMA PRODUK: {detail_topik}

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
          "icon_emoji": "💧",
          "title": "Sub Judul",
          "content": "Penjelasan singkat maks 2 baris."
        }}
      ]
    }}
  ]
}}
ATURAN MUTLAK KUALITAS: 
1. Buat jumlah slide di dalam array "slides" TEPAT sesuai permintaan: {opsi_slide}.
{style_rule}
3. Gunakan Emoji yang relevan di tiap "icon_emoji".{slide_rule}"""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Teks Dasar yang harus diproses:\n{prompt_text}"}
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
    """
    Merender HTML dengan ukuran piksel absolut (Misal: 1080px) dan proteksi Overflow Teks.
    Ditambah Footer Stamp Website.
    """
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
        
        # Merakit HTML Per Poster dengan tambahan Website di Footer
        all_posters_html += f"""
        <div class="slide-wrapper">
            <div id="{poster_id}" class="poster-container">
                <div class="slide-badge">SLIDE {slide_num}</div>
                <h1 class="header-title">{slide.get("infographic_title", f"Slide {slide_num}")}</h1>
                
                {layout_html}
                
                <div class="footer-note">
                    <div>STUDIO KREATIF PRO • KTB UKM JATIM</div>
                    <div class="footer-url">https://ktbukm-jatim.store</div>
                </div>
            </div>
            <button id="{btn_id}" class="download-btn" onclick="downloadPoster('{poster_id}', '{btn_id}', {slide_num})">
                <span>⬇️</span> Download Slide {slide_num} (100% Resolusi Tinggi)
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
            
            body {{
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #eef2f5;
            }}
            
            .slide-wrapper {{
                margin-bottom: 60px;
                display: flex;
                flex-direction: column;
                align-items: center;
                width: 100%;
                overflow-x: auto; 
            }}
            
            .poster-container {{
                background: linear-gradient(135deg, #f0fbff 0%, #c4f0f6 100%);
                width: {w_px}px; 
                min-height: {h_px}px;
                padding: 60px 80px;
                box-sizing: border-box;
                font-family: 'Nunito', sans-serif;
                position: relative;
                display: flex;
                flex-direction: column;
            }}
            
            .slide-badge {{
                position: absolute;
                top: 20px;
                left: 20px;
                background-color: #ff5722;
                color: white;
                padding: 10px 25px;
                border-radius: 30px;
                font-family: 'Montserrat', sans-serif;
                font-size: 18px;
                font-weight: 800;
            }}
            
            .header-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 55px;
                color: #004d40;
                text-align: center;
                margin-top: 20px;
                margin-bottom: 50px;
                line-height: 1.2;
                text-transform: uppercase;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.05);
            }}
            
            .hero-image {{
                width: 100%;
                height: 550px;
                object-fit: cover;
                border-radius: 40px;
                margin: 0 auto 50px auto;
                display: block;
                box-shadow: 0 15px 30px rgba(0,0,0,0.15);
                border: 10px solid white;
            }}
            
            .cards-wrapper {{
                display: flex;
                flex-direction: column;
                gap: 25px;
                flex: 1;
            }}
            
            .card {{
                background-color: white;
                border-radius: 25px;
                padding: 30px 40px;
                display: flex;
                align-items: flex-start;
                box-shadow: 0 8px 20px rgba(0,0,0,0.05);
                border-left: 15px solid #00acc1;
                height: auto;
            }}
            
            .card-icon {{
                font-size: 65px;
                margin-right: 30px;
                line-height: 1;
            }}
            
            .card-text {{
                flex: 1;
                min-width: 0; 
            }}
            
            .card-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 28px;
                color: #00838f;
                margin-bottom: 10px;
                font-weight: 800;
                word-wrap: break-word;
                overflow-wrap: break-word;
                white-space: normal;
                line-height: 1.3;
            }}
            
            .card-desc {{
                font-size: 22px;
                color: #455a64;
                line-height: 1.5;
                margin: 0;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }}
            
            .footer-note {{
                margin-top: auto; 
                padding-top: 50px;
                text-align: center;
                color: #00838f;
                font-weight: 800;
                font-size: 22px;
                letter-spacing: 2px;
                font-family: 'Montserrat', sans-serif;
            }}
            
            /* Penambahan style khusus URL */
            .footer-url {{
                font-size: 18px;
                font-weight: 500;
                margin-top: 8px;
                letter-spacing: 1px;
                color: #00acc1;
            }}

            .download-btn {{
                margin-top: 25px;
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 20px 40px;
                font-size: 20px;
                font-family: 'Montserrat', sans-serif;
                border-radius: 40px;
                cursor: pointer;
                box-shadow: 0 8px 20px rgba(255, 87, 34, 0.4);
                transition: background 0.3s;
                font-weight: bold;
            }}
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
                
                btn.innerHTML = '⏳ Sedang Memproses Resolusi Tinggi...';
                btn.style.backgroundColor = '#757575';
                
                html2canvas(poster, {{ scale: 1, useCORS: true, backgroundColor: null }}).then(canvas => {{
                    if(badge) badge.style.display = 'block'; 
                    
                    btn.innerHTML = '<span>⬇️</span> Download Slide ' + slideNum + ' (100% Resolusi Tinggi)';
                    btn.style.backgroundColor = '#ff5722';
                    
                    let link = document.createElement('a');
                    link.download = 'Infografis_Kreatif_' + slideNum + '.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    if(badge) badge.style.display = 'block';
                    console.error("Gagal mendownload:", err);
                    alert("Terjadi kesalahan sistem saat memproses gambar.");
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
    st.info("💡 **Ditenagai Groq Llama 3.3 70B & Hugging Face:** Desain kini dibekali **Pilihan Gaya Visual** dan pengaturan pemadatan teks otomatis untuk hasil profesional yang lebih memukau.")

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
                "📸 Gaya Foto Realistik (Nyata & Profesional)",
                "🎨 Gaya Lukisan (Vektor / Ilustrasi Digital)"
            ], index=0
        )
        
    with col2:
        opsi_slide = st.selectbox(
            "3. Mode Format Poster:", 
            [
                "1 Slide (1 Poster Panjang, Teks Sangat Padat)", 
                "2 Slide (Carousel Pendek)",
                "3 Slide (Carousel Menengah)",
                "5 Slide (Carousel Panjang)",
                "Isi sendiri..."
            ], index=0
        )
        
        jawaban_slide = opsi_slide
        if opsi_slide == "Isi sendiri...":
            jawaban_slide = st.text_input("Instruksi spesifik (contoh: 4 slide):", placeholder="Contoh: 4 slide")

    user_input = st.text_area("Draft Naskah Dasar:", value=naskah_final, height=150)

    if st.button("✨ Hasilkan Poster Berkualitas", use_container_width=True, type="primary"):
        if not jawaban_slide.strip():
            st.warning("⚠️ Mohon lengkapi Mode Format terlebih dahulu!")
            return
            
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Groq Llama 3.3 sedang menstrukturkan desain presentasi..."):
            try:
                # Menarik konteks produk
                produk_name = st.session_state.jawaban.get("produk", "Produk Utama")
                merk_name = st.session_state.jawaban.get("merk", "")
                detail_topik = f"{merk_name} {produk_name}".strip()
                
                # 1. Analisis Naskah dengan Groq (JSON Setup dengan Mode Gaya & 1 Slide Padat)
                structured_data = generate_structured_text_groq(user_input, jawaban_slide, detail_topik, opsi_gaya)
                slides = structured_data.get("slides", [])
                total_slides = len(slides)
                
                b64_images = []
                
                # 2. Looping Gambar AI
                for idx, slide in enumerate(slides):
                    slide_num = slide.get("slide_number", idx + 1)
                    
                    # Fallback jika image_prompt kosong
                    img_prompt = slide.get("image_prompt", f"ultra-realistic product photography of {detail_topik}")
                    
                    with st.spinner(f"📸 Pelukis AI FLUX.1 sedang memproduksi visual untuk Slide {slide_num} dari {total_slides} (Harap tunggu)..."):
                        b64_img = generate_image_with_retry(img_prompt, opsi_dimensi)
                        b64_images.append(b64_img)
                
                with st.spinner("📐 Web Layout Engine sedang merakit Poster Resolusi Tinggi..."):
                    # 3. Merakit HTML/CSS Kualitas Tinggi
                    final_html = render_beautiful_html_poster(structured_data, b64_images, opsi_dimensi)
                    
                    st.success(f"🎉 {total_slides} Poster Infografis berhasil dirender dengan desain luar biasa!")
                    
                    # 4. Tampilkan HTML Interaktif
                    h_px = 1920 if "Vertical" in opsi_dimensi else (1080 if "Square" in opsi_dimensi else 1080)
                    iframe_height = total_slides * (h_px + 200)
                    
                    st.components.v1.html(final_html, height=iframe_height, scrolling=True)
                    
                    with st.expander("🛠️ Lihat Data Struktur Poin (JSON)"):
                        st.json(structured_data)

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
