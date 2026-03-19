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
        
    # PERBAIKAN: Menggunakan URL router terbaru sesuai instruksi error
    API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_key}"}
    
    # Resolusi default untuk ilustrasi tengah
    w, h = 1024, 1024 
    if "Portrait" in dimensi or "Vertical" in dimensi:
        w, h = 896, 1152 # Proporsi vertikal agar serasi

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
                st.warning(f"⚠️ Pelukis AI Error: {response.text}")
                return None
        except Exception as e:
            time.sleep(3)
            continue
            
    return None

# ==========================================
# 🧩 2. GROQ Llama 3.3 70B WRAPPER
# ==========================================
def generate_structured_text_groq(prompt_text, opsi_slide):
    """
    Menggunakan Groq untuk menstrukturkan data dengan penambahan 'icon_emoji' 
    agar desain visualnya menyerupai poster Canva (berikon).
    """
    groq_key = st.secrets.get("GROQ_API_KEY")
    if not groq_key:
        raise Exception("GROQ_API_KEY tidak ditemukan di st.secrets!")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_key}",
        "Content-Type": "application/json"
    }

    system_prompt = f"""Kamu adalah Ahli Desain Visual dan Copywriter Profesional.
Tugasmu merangkum teks menjadi format infografis padat bergaya modern.
Format output HARUS JSON valid dengan struktur berikut:
{{
  "infographic_title": "Judul Utama Poster",
  "image_prompt": "professional poster illustration, clean vector, minimalist, highly detailed, [objek utama]...",
  "items": [
    {{
      "icon_emoji": "🌍",
      "title": "Sub Judul Poin 1",
      "content": "Penjelasan sangat singkat, maksimal 2 baris."
    }},
    {{
      "icon_emoji": "🛡️",
      "title": "Sub Judul Poin 2",
      "content": "Penjelasan sangat singkat, maksimal 2 baris."
    }}
  ]
}}
ATURAN MUTLAK: Buat jumlah item dalam array 'items' sesuai dengan permintaan: {opsi_slide}. Pilih satu emoji (icon_emoji) yang paling merepresentasikan setiap poin."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Teks Dasar yang harus dirangkum menjadi Poin-Poin:\n{prompt_text}"}
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
# 🧩 3. WEB-BASED LAYOUT ENGINE (HTML2CANVAS)
# ==========================================
def render_beautiful_html_poster(data_json, b64_img, opsi_dimensi):
    """
    Membuat layout menggunakan HTML/CSS modern yang sangat estetik (berbayang, lengkung, ikon).
    Disematkan script html2canvas untuk langsung mendownloadnya sebagai PNG.
    """
    # Mengatur lebar kontainer utama
    max_width = "800px" if "Square" in opsi_dimensi else "650px"
    
    # 1. Menyiapkan Gambar Utama
    img_element = ""
    if b64_img:
        img_element = f'<img src="{b64_img}" class="hero-image" alt="Ilustrasi Utama">'
        
    # 2. Menyiapkan Item/Poin
    items_html = ""
    for item in data_json.get("items", []):
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
        
    # 3. Merakit HTML Keseluruhan dengan CSS Premium
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Nunito:wght@400;600;700&display=swap');
            
            body {{
                margin: 0;
                padding: 20px;
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #f0f2f5;
            }}
            
            /* Kontainer Utama Poster */
            #poster-container {{
                background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
                width: 100%;
                max-width: {max_width};
                padding: 40px;
                border-radius: 25px;
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                font-family: 'Nunito', sans-serif;
                position: relative;
                box-sizing: border-box;
            }}
            
            .header-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 32px;
                color: #006064;
                text-align: center;
                margin-top: 0;
                margin-bottom: 30px;
                line-height: 1.3;
                text-transform: uppercase;
                text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
            }}
            
            .hero-image {{
                width: 100%;
                max-width: 450px;
                height: auto;
                border-radius: 20px;
                margin: 0 auto 40px auto;
                display: block;
                box-shadow: 0 10px 25px rgba(0,0,0,0.15);
                border: 4px solid white;
            }}
            
            .cards-wrapper {{
                display: flex;
                flex-direction: column;
                gap: 15px;
            }}
            
            .card {{
                background-color: white;
                border-radius: 15px;
                padding: 20px;
                display: flex;
                align-items: center;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                border-left: 8px solid #00acc1;
                transition: transform 0.2s;
            }}
            
            .card-icon {{
                font-size: 45px;
                margin-right: 20px;
                min-width: 60px;
                text-align: center;
                filter: drop-shadow(2px 4px 6px rgba(0,0,0,0.1));
            }}
            
            .card-title {{
                font-family: 'Montserrat', sans-serif;
                font-size: 18px;
                color: #00838f;
                margin-bottom: 6px;
                font-weight: 700;
            }}
            
            .card-desc {{
                font-size: 15px;
                color: #455a64;
                line-height: 1.5;
            }}
            
            /* Tombol Download */
            .download-btn {{
                margin-top: 30px;
                background-color: #ff5722;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                font-family: 'Montserrat', sans-serif;
                border-radius: 30px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(255, 87, 34, 0.4);
                transition: background 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                width: 100%;
                max-width: {max_width};
            }}
            .download-btn:hover {{
                background-color: #e64a19;
            }}
            
            .footer-note {{
                text-align: center;
                margin-top: 30px;
                color: #00838f;
                font-weight: 600;
                font-size: 14px;
                letter-spacing: 1px;
            }}
        </style>
    </head>
    <body>

        <!-- Area Poster yang akan di-capture -->
        <div id="poster-container">
            <h1 class="header-title">{data_json.get("infographic_title", "Infografis Modern")}</h1>
            
            {img_element}
            
            <div class="cards-wrapper">
                {items_html}
            </div>
            
            <div class="footer-note">STUDIO KREATIF PRO • KTB UKM JATIM</div>
        </div>

        <!-- Tombol Pemicu Download -->
        <button class="download-btn" onclick="downloadPoster()">
            <span>⬇️</span> Download Poster Kualitas Tinggi (PNG)
        </button>

        <script>
            function downloadPoster() {{
                const poster = document.getElementById('poster-container');
                const btn = document.querySelector('.download-btn');
                
                // Ubah teks tombol saat loading
                btn.innerHTML = '⏳ Sedang Memproses Gambar...';
                btn.style.backgroundColor = '#757575';
                
                // Menggunakan html2canvas untuk memotret div
                html2canvas(poster, {{ scale: 2, useCORS: true }}).then(canvas => {{
                    // Kembalikan tombol
                    btn.innerHTML = '<span>⬇️</span> Download Poster Kualitas Tinggi (PNG)';
                    btn.style.backgroundColor = '#ff5722';
                    
                    // Trigger download
                    let link = document.createElement('a');
                    link.download = 'Infografis_Kreatif.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }}).catch(err => {{
                    console.error("Gagal mendownload:", err);
                    alert("Terjadi kesalahan saat memproses gambar.");
                    btn.innerHTML = '<span>⬇️</span> Download Poster Kualitas Tinggi (PNG)';
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
    st.info("💡 **Arsitektur Baru (Web Layout Engine):** Sistem kini menyatukan teks, ikon organik, dan lukisan AI menjadi layout estetik menyerupai poster desain profesional.")

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
                "Pilih...",
                "1080 x 1920 px (Vertical / IG Story / TikTok) - DIREKOMENDASIKAN",
                "1080 x 1080 px (Square / IG Feed)"
            ], index=1
        )
        
    with col2:
        opsi_slide = st.selectbox(
            "2. Mode Format Poster:", 
            [
                "Pilih...", 
                "1 Slide (Satu Halaman Penuh, Teks Menyatu)", 
                "Isi sendiri..."
            ], index=1
        )
        
        jawaban_slide = opsi_slide
        if opsi_slide == "Isi sendiri...":
            jawaban_slide = st.text_input("Instruksi spesifik (contoh: Buat jadi 5 poin utama):", placeholder="Contoh: 5 poin")

    user_input = st.text_area("Draft Naskah Dasar:", value=naskah_final, height=150)

    if st.button("✨ Hasilkan Infografis Cerdas", use_container_width=True, type="primary"):
        if opsi_dimensi == "Pilih..." or jawaban_slide == "Pilih..." or not jawaban_slide.strip():
            st.warning("⚠️ Mohon lengkapi pilihan Ukuran Poster dan Mode Format terlebih dahulu!")
            return
            
        if not user_input.strip():
            st.warning("⚠️ Draft naskah tidak boleh kosong!")
            return
            
        with st.spinner("🤖 Groq Llama 3.3 sedang merangkum naskah dan memilih Ikon yang tepat..."):
            try:
                # 1. Analisis Naskah dengan Groq (JSON Setup)
                structured_data = generate_structured_text_groq(user_input, jawaban_slide)
                
                with st.spinner("🎨 AI Pelukis FLUX.1 sedang menggambar ilustrasi utama (Harap tunggu, mesin pemanasan sekitar 15-30 detik)..."):
                    # 2. Gambar ilustrasi via Hugging Face Router terbaru
                    img_prompt = structured_data.get("image_prompt", "Professional vector infographic illustration")
                    b64_illustration = generate_image_with_retry(img_prompt, opsi_dimensi)
                    
                    with st.spinner("📐 Layout Web Engine sedang menata letak elemen..."):
                        # 3. Merakit HTML/CSS Kualitas Tinggi
                        final_html = render_beautiful_html_poster(structured_data, b64_illustration, opsi_dimensi)
                        
                        st.success("🎉 Infografis berhasil dirender dengan desain memukau!")
                        
                        # 4. Tampilkan HTML yang interaktif langsung ke dalam iframe Streamlit
                        # Kita beri height tinggi agar tombol download di bawahnya tidak terpotong
                        st.components.v1.html(final_html, height=1200, scrolling=True)
                        
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
