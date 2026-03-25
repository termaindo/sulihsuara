import streamlit as st
import google.generativeai as genai
import json
import random
import base64
import re
from io import BytesIO
from PIL import Image
from google.api_core.exceptions import ResourceExhausted

# ==========================================
# KONFIGURASI API GEMINI
# ==========================================
def setup_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception:
        st.error("🔑 Kunci API Gemini belum dikonfigurasi di st.secrets.")

# ==========================================
# FUNGSI: PEMROSESAN GAMBAR (RESIZE 800px)
# ==========================================
def process_product_image(uploaded_file):
    try:
        image = Image.open(uploaded_file)
        # Menjaga RAM server tetap aman
        image.thumbnail((800, 800))
        
        buf = BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        base64_img = base64.b64encode(byte_im).decode('utf-8')
        return f"data:image/png;base64,{base64_img}"
    except Exception as e:
        st.error(f"Gagal memproses gambar: {e}")
        return None

# ==========================================
# FUNGSI: ANALISIS TEKS (GEMINI 2.5 FLASH)
# ==========================================
def generate_json_structure(naskah):
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Ubah naskah promosi berikut menjadi struktur JSON murni.
    Jika naskah panjang, buatkan menjadi urutan slide (carousel) maksimal 3 slide.
    
    Format wajib (JSON Array):
    [
        {{
            "slide_number": 1,
            "infographic_title": "Judul Singkat",
            "items": ["Poin 1", "Poin 2"]
        }}
    ]
    Naskah: {naskah}
    """
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            # Pastikan selalu mengembalikan format list (array)
            data = json.loads(match.group(0))
            return data if isinstance(data, list) else [data]
        
        data = json.loads(response.text)
        return data if isinstance(data, list) else [data]
    except Exception as e:
        if "429" in str(e): return {"error": "429"}
        return {"error": "FORMAT_JSON_RUSAK"}

# ==========================================
# ENGINE TEMA & CSS (SLIDE INDIVIDUAL)
# ==========================================
def get_theme_css(theme_name, layout_type, mode_foto):
    # Dimensi menggunakan min-height agar proporsional
    if layout_type == "Portrait (9:16)":
        max_width, min_height = "380px", "675px"
    elif layout_type == "Square (1:1)":
        max_width, min_height = "450px", "450px"
    else:
        max_width, min_height = "700px", "393px"

    themes = {
        "minimalist": {"bg": "#ffffff", "text": "#212121", "accent": "#f5f5f5", "font": "sans-serif"},
        "elegant_dark": {"bg": "#1a1a2e", "text": "#ffffff", "accent": "#16213e", "font": "serif"},
        "modern_gradient": {"bg": "linear-gradient(135deg, #667eea, #764ba2)", "text": "#ffffff", "accent": "rgba(255,255,255,0.15)", "font": "sans-serif"},
        "earthy_nature": {"bg": "#f4f1ea", "text": "#2d3e2d", "accent": "#dce2d7", "font": "sans-serif"},
        "vibrant_pop": {"bg": "#FFEB3B", "text": "#212121", "accent": "#ffffff", "font": "Impact, sans-serif"}
    }
    
    t = themes.get(theme_name, themes["minimalist"])
    
    if mode_foto == "Foto Studio (Latar Putih)":
        img_style = "mix-blend-mode: multiply; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.1));"
    else:
        img_style = "border-radius: 12px; border: 3px solid white; box-shadow: 0 12px 25px rgba(0,0,0,0.15);"

    css = f"""
    <style>
        .poster-container {{
            width: 100%; max-width: {max_width}; min-height: {min_height};
            background: {t['bg']}; color: {t['text']}; font-family: {t['font']};
            display: flex; flex-direction: column; justify-content: space-between; 
            border-radius: 20px; padding: 35px; box-sizing: border-box; 
            box-shadow: 0 20px 45px rgba(0,0,0,0.15); margin: 0 auto;
        }}
        .poster-header {{ 
            text-align: center; font-size: 1.4em; font-weight: 600; 
            text-transform: uppercase; margin-bottom: 25px; 
            line-height: 1.4; letter-spacing: 0.8px;
        }}
        .poster-content {{ 
            display: flex; flex-direction: column; align-items: center; 
            flex-grow: 1; gap: 30px; margin-bottom: 20px;
        }}
        .poster-image-wrap {{ width: 100%; display: flex; justify-content: center; }}
        .poster-image-wrap img {{
            max-width: 95%; max-height: 250px; object-fit: contain;
            {img_style}
        }}
        .items-container {{ width: 100%; display: flex; flex-direction: column; gap: 15px; }}
        .item-box {{ 
            background: {t['accent']}; padding: 15px 20px; border-radius: 10px; 
            font-size: 0.95em; width: 100%; font-weight: 500; 
            line-height: 1.5; border-left: 6px solid {t['text']}; box-sizing: border-box;
        }}
        .poster-footer {{ 
            text-align: center; font-size: 0.72em; border-top: 1px solid rgba(128,128,128,0.3); 
            padding-top: 15px; font-weight: 600; line-height: 1.6;
        }}
        .footer-line-1 {{ margin-bottom: 6px; letter-spacing: 0.5px; text-transform: uppercase; }}
        .footer-line-2 {{ 
            display: flex; align-items: center; justify-content: center; 
            gap: 8px; opacity: 0.9; font-weight: 500;
        }}
        .icon-svg {{ width: 14px; height: 14px; fill: currentColor; vertical-align: middle; }}
    </style>
    """
    return css

def render_single_slide_html(json_slide, base64_img, layout_type, theme_name, mode_foto):
    css = get_theme_css(theme_name, layout_type, mode_foto)
    
    icon_ig = '<svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>'
    icon_web = '<svg class="icon-svg" viewBox="0 0 24 24"><path d="M12 0c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm-1.001 19.923c-3.324-.431-5.992-2.793-6.817-6.002h2.298c.241 1.488.666 2.822 1.233 3.885-.888-.637-1.646-1.41-2.233-2.283.587.873 1.345 1.646 2.233 2.283.398.745.857 1.405 1.373 1.956-.036.053-.071.104-.107.161zm1.001-1.006c-.846 0-1.637-.621-2.277-1.657-.591-.958-1.026-2.228-1.223-3.66h7c-.197 1.432-.632 2.702-1.223 3.66-.64 1.036-1.431 1.657-2.277 1.657zm8.818-7.002h-2.298c-.241 1.488-.666 2.822-1.233 3.885.888-.637 1.646-1.41 2.233-2.283-.587.873-1.345 1.646-2.233 2.283-.398.745-.857 1.405-1.373 1.956.036.053.071.104.107.161 3.324-.431 5.992-2.793 6.817-6.002zm-10.819-10.923c3.324.431 5.992 2.793 6.817 6.002h-2.298c-.241-1.488-.666-2.822-1.233-3.885.888.637 1.646 1.41 2.233 2.283-.587-.873-1.345-1.646-2.233-2.283-.398-.745-.857-1.405-1.373-1.956.036-.053.071-.104.107-.161zm1.001 1.006c.846 0 1.637.621 2.277 1.657.591.958 1.026 2.228 1.223 3.66h-7c.197-1.432.632-2.702 1.223-3.66.64-1.036 1.431-1.657 2.277-1.657zm-8.818 7.002h2.298c.241-1.488.666-2.822 1.233-3.885-.888.637-1.646 1.41-2.233 2.283.587-.873 1.345-1.646 2.233-2.283.398-.745.857-1.405 1.373-1.956-.036-.053-.071-.104-.107-.161-3.324.431-5.992 2.793-6.817 6.002z"/></svg>'

    items_html = "".join([f"<div class='item-box'>✓ {i}</div>" for i in json_slide.get("items", [])])
    
    html = f"""
    {css}
    <div class="poster-container" id="capture-area">
        <div class="poster-header">{json_slide.get('infographic_title', 'Visual Produk')}</div>
        <div class="poster-content">
            <div class="poster-image-wrap"><img src="{base64_img}"></div>
            <div class="items-container">{items_html}</div>
        </div>
        <div class="poster-footer">
            <div class="footer-line-1">Studio Kreatif Pro - KTB UKM Jatim</div>
            <div class="footer-line-2">
                {icon_ig} @ktbukm.jatim &nbsp; | &nbsp; {icon_web} https://ktbukm-jatim.store
            </div>
        </div>
    </div>
    """
    return html

# ==========================================
# MODUL UTAMA RUN()
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak / Visual")
    setup_gemini()

    naskah_mentah = st.session_state.get("hasil_naskah", "")
    if not naskah_mentah:
        st.info("ℹ️ Silakan buat naskah di Ruang 1 terlebih dahulu.")
        naskah_mentah = "Produk Unggulan UMKM Jawa Timur."

    st.markdown("---")
    st.warning("📸 **Panduan Foto:** Gunakan latar belakang putih polos untuk hasil transparan instan pada mode 'Studio'.")
    
    st.markdown("### 1. Pengaturan Produksi")
    mode_foto = st.radio(
        "Jenis Foto Produk:", ["Foto Studio (Latar Putih)", "Foto Estetik / Sudah Ada Latar"],
        horizontal=True
    )

    uploaded_file = st.file_uploader("Unggah foto produk (JPG/PNG):", type=['jpg', 'jpeg', 'png'])
    
    col1, col2 = st.columns(2)
    with col1:
        layout_choice = st.selectbox("Dimensi Poster:", ["Portrait (9:16)", "Square (1:1)", "Landscape (16:9)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Buat Desain Visual Sekarang!", type="primary"):
        if not uploaded_file:
            st.warning("⚠️ Unggah foto produk terlebih dahulu.")
        else:
            try:
                with st.spinner("⚙️ Direktur kreatif sedang memproduksi visual cetakan..."):
                    base64_img = process_product_image(uploaded_file)
                    json_data = generate_json_structure(naskah_mentah)
                    
                    if isinstance(json_data, dict) and json_data.get("error") == "429":
                        st.error("⏳ **Server Google sedang mendinginkan mesin, mohon tunggu 1 menit lalu tekan tombolnya lagi.**")
                    elif isinstance(json_data, dict) and json_data.get("error") == "FORMAT_JSON_RUSAK":
                        st.error("⏳ **Mesin AI Sedang Memproses Ulang:** Gagal merapikan tata letak naskah. Silakan klik tombol sekali lagi.")
                    else:
                        st.success("✨ Visual Berhasil Dicetak!")
                        
                        # Pilih satu tema acak yang sama untuk semua slide agar seragam
                        theme = random.choice(["minimalist", "elegant_dark", "modern_gradient", "earthy_nature", "vibrant_pop"])
                        
                        # Simpan hasil render HTML per slide ke dalam sebuah list
                        list_html_slides = []
                        for slide in json_data:
                            slide_html = render_single_slide_html(slide, base64_img, layout_choice, theme, mode_foto)
                            list_html_slides.append(slide_html)
                        
                        st.session_state.infografis_output_list = list_html_slides
            except Exception:
                st.error("❌ Terjadi gangguan komunikasi dengan Server AI Google.")

    # --- TAMPILAN OUTPUT & DOWNLOAD PER SLIDE (PNG SCRIPT) ---
    if "infografis_output_list" in st.session_state:
        st.markdown("### 🖼️ Hasil Produksi Desain")
        st.info("💡 Berikut adalah desain Anda. Jika naskah panjang, kami membaginya ke beberapa slide. Unduh satu per satu menggunakan tombol di bawah masing-masing gambar.")
        
        # Loop untuk menampilkan slide satu per satu dengan tombol unduh masing-masing
        for idx, slide_html in enumerate(st.session_state.infografis_output_list):
            st.markdown(f"**📄 Slide {idx + 1}**")
            
            html_with_download = f"""
            <html>
            <head>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                <style>
                    body {{ margin:0; background:#f0f2f6; display:flex; flex-direction:column; align-items:center; font-family: sans-serif; padding-top: 10px; }}
                    .download-btn {{
                        background-color: #ff4b4b; color: white; border: none; padding: 12px 24px;
                        font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer;
                        margin-bottom: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                        transition: 0.3s; width: 300px;
                    }}
                    .download-btn:hover {{ background-color: #ff3333; box-shadow: 0 6px 12px rgba(0,0,0,0.2); }}
                    #wrapper {{ width: 100%; display: flex; justify-content: center; }}
                </style>
            </head>
            <body>
                <button class="download-btn" onclick="downloadImage()">📥 Unduh Slide {idx + 1} (PNG)</button>
                <div id="wrapper">
                    {slide_html}
                </div>
                
                <script>
                    function downloadImage() {{
                        const btn = document.querySelector('.download-btn');
                        const originalText = btn.innerText;
                        btn.innerText = "⏳ Sedang Memproses Gambar...";
                        
                        html2canvas(document.getElementById("capture-area"), {{
                            scale: 2, 
                            useCORS: true,
                            backgroundColor: null /* Agar background radius tetap rapi */
                        }}).then(canvas => {{
                            let link = document.createElement('a');
                            link.download = 'Slide_{idx + 1}_Studio_Kreatif.png';
                            link.href = canvas.toDataURL('image/png');
                            link.click();
                            btn.innerText = originalText;
                        }}).catch(err => {{
                            console.error("Error: ", err);
                            btn.innerText = "❌ Gagal Mengunduh";
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            # Tinggi diset 850px agar tombol dan satu slide bisa tampil pas tanpa terpotong
            st.components.v1.html(html_with_download, height=850, scrolling=True)
            st.markdown("<br>", unsafe_allow_html=True) # Jarak antar frame slide

    # --- PANDUAN 2 LANGKAH MANUAL ---
    st.divider()
    st.markdown("### 🤖 Instruksi Praktis (Copas ke Gemini Pribadi Anda)")
    st.info("Jika Anda tidak punya foto sendiri, gunakan panduan langkah demi langkah di bawah ini:")

    st.markdown("**Langkah 1: Membuat Konsep Konten (Copywriting) Salin teks ini, dengan cara klik icon tumpukan dokumen di sebelah kanan atas kotak di bawah ini dan tempel ke AI**")
    
    # REVISI PROMPT: Menggunakan perintah langsung, memisahkan bahan baku (naskah) di akhir.
    prompt_copywriting = f"""Tolong bedah teks promosi di bawah ini menjadi konsep konten infografis yang menarik. Jika teksnya panjang, buatkan menjadi urutan 3-5 slide (carousel). Tentukan judul yang memikat, poin-poin manfaat, dan ajakan bertindak (CTA) untuk setiap slidenya. Pastikan di bagian bawah setiap slide memuat stempel paten 2 baris:
Baris 1: Studio Kreatif Pro - KTB UKM Jatim
Baris 2: Instagram: @ktbukm.jatim | Website: https://ktbukm-jatim.store

Berikut teks promosinya:
{naskah_mentah}"""
    
    st.code(prompt_copywriting, language="text")

    st.markdown("**Langkah 2: Membuat Prompt Gambar (Visual Design)**")
    prompt_visual = "Berdasarkan konsep konten slide tersebut, buatkan saya 'Image Prompt' yang sangat detil untuk saya masukkan ke mesin AI Image Generator (seperti Midjourney atau DALL-E). Pastikan prompt tersebut menjelaskan gaya pencahayaan, komposisi produk, warna latar belakang yang estetik, dan suasana profesional untuk katalog produk UMKM."
    st.code(prompt_visual, language="text")

    # --- NAVIGASI STUDIO ---
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
