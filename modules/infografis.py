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
        # Menjaga RAM server dengan resize maksimal 800x800px
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
    Anda adalah Direktur Kreatif. Ubah naskah promosi berikut menjadi struktur JSON murni.
    Jika naskah panjang, buatkan menjadi maksimal 3 slide/halaman.
    
    Format wajib (JSON Array):
    [
        {{
            "slide_number": 1,
            "infographic_title": "Judul Singkat",
            "items": ["Poin 1", "Poin 2", "Poin 3"]
        }}
    ]
    
    Naskah: {naskah}
    """
    try:
        response = model.generate_content(prompt)
        match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return json.loads(response.text)
    except Exception:
        return {"error": "429"}

# ==========================================
# ENGINE TEMA & CSS (LEGABILITAS TINGGI)
# ==========================================
def get_theme_css(theme_name, layout_type, mode_foto):
    # Penentuan Rasio Dimensi
    if layout_type == "Portrait (9:16)":
        aspect_ratio, max_width = "9 / 16", "350px"
    elif layout_type == "Square (1:1)":
        aspect_ratio, max_width = "1 / 1", "450px"
    else:
        aspect_ratio, max_width = "16 / 9", "700px"

    # Palet Warna Kontras Tinggi
    themes = {
        "minimalist": {"bg": "#ffffff", "text": "#212121", "accent": "#f5f5f5", "font": "sans-serif"},
        "elegant_dark": {"bg": "#1a1a2e", "text": "#ffffff", "accent": "#16213e", "font": "serif"},
        "modern_gradient": {"bg": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)", "text": "#1a1a2e", "accent": "rgba(255,255,255,0.3)", "font": "sans-serif"},
        "earthy_nature": {"bg": "#f4f1ea", "text": "#2d3e2d", "accent": "#dce2d7", "font": "sans-serif"},
        "vibrant_pop": {"bg": "#FFEB3B", "text": "#212121", "accent": "#ffffff", "font": "Impact, sans-serif"}
    }
    
    t = themes.get(theme_name, themes["minimalist"])
    
    if mode_foto == "Foto Studio (Latar Putih)":
        img_style = "mix-blend-mode: multiply; filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.1));"
    else:
        img_style = "border-radius: 12px; border: 4px solid white; box-shadow: 0 12px 25px rgba(0,0,0,0.15);"

    css = f"""
    <style>
        .poster-container {{
            width: 100%; max-width: {max_width}; aspect-ratio: {aspect_ratio};
            background: {t['bg']}; color: {t['text']}; font-family: {t['font']};
            margin: 0 auto 30px auto; display: flex; flex-direction: column;
            justify-content: space-between; border-radius: 20px;
            padding: 35px; box-sizing: border-box; box-shadow: 0 20px 45px rgba(0,0,0,0.15);
        }}
        .poster-header {{ 
            text-align: center; font-size: 1.4em; font-weight: 600; 
            text-transform: uppercase; margin-bottom: 25px; 
            line-height: 1.4; letter-spacing: 0.8px;
        }}
        .poster-content {{ 
            display: flex; flex-direction: column; align-items: center; 
            justify-content: center; flex-grow: 1; gap: 30px; 
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
            line-height: 1.6; border-left: 6px solid {t['text']};
            box-sizing: border-box;
        }}
        .poster-footer {{ 
            text-align: center; font-size: 0.75em; border-top: 1px solid rgba(0,0,0,0.1); 
            padding-top: 15px; margin-top: 25px; font-weight: 600; opacity: 0.8;
        }}
    </style>
    """
    return css

def render_html_poster(json_slide, base64_img, layout_type, theme_name, mode_foto):
    css = get_theme_css(theme_name, layout_type, mode_foto)
    items_html = "".join([f"<div class='item-box'>✓ {i}</div>" for i in json_slide.get("items", [])])
    
    html = f"""
    {css}
    <div class="poster-container">
        <div class="poster-header">{json_slide.get('infographic_title', 'Visual Produk')}</div>
        <div class="poster-content">
            <div class="poster-image-wrap"><img src="{base64_img}"></div>
            <div class="items-container">{items_html}</div>
        </div>
        <div class="poster-footer">
            <div>Studio Kreatif Pro - KTB UKM JATIM</div>
            <div>📸 @ktbukm.jatim | 🌐 https://ktbukm-jatim.store</div>
        </div>
    </div>
    """
    return html

# ==========================================
# FUNGSI: PANDUAN 2 LANGKAH MANUAL
# ==========================================
def create_manual_guide(naskah):
    guide = f"""
### 💡 Panduan Produksi Mandiri (2 Langkah)

Jika Anda ingin hasil yang lebih bervariasi menggunakan ChatGPT atau Gemini Web, silakan ikuti langkah berikut:

**Langkah 1: Membuat Konsep Konten (Copywriting)**
*Salin teks ini dan tempel ke AI:*
"Saya memiliki naskah produk: '{naskah}'. Tolong bedah naskah ini menjadi konsep konten infografis yang menarik. Jika naskahnya panjang, buatkan menjadi urutan 3-5 slide (carousel). Tentukan judul yang memikat, poin-poin manfaat, dan ajakan bertindak (CTA) untuk setiap slidenya."

**Langkah 2: Membuat Prompt Gambar (Visual Design)**
*Gunakan hasil dari Langkah 1, lalu tempel perintah ini:*
"Berdasarkan konsep konten slide tersebut, buatkan saya 'Image Prompt' yang sangat detil untuk saya masukkan ke mesin AI Image Generator (seperti Midjourney atau DALL-E). Pastikan prompt tersebut menjelaskan gaya pencahayaan, komposisi produk, warna latar belakang yang estetik, dan suasana profesional untuk katalog produk UMKM."
    """
    return guide

# ==========================================
# MODUL UTAMA RUN() - ONE PAGE NAVIGATION
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak / Visual")
    setup_gemini()

    naskah_mentah = st.session_state.get("hasil_naskah", "")
    if not naskah_mentah:
        st.info("ℹ️ Silakan buat naskah di Ruang 1 terlebih dahulu.")
        naskah_mentah = "Produk Unggulan UMKM Jawa Timur."

    st.markdown("---")
    st.warning("📸 **Panduan Foto:** Gunakan latar belakang putih polos untuk mode 'Studio' agar produk menyatu sempurna dengan desain.")
    
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
            with st.spinner("⚙️ Direktur kreatif sedang memproduksi visual cetakan..."):
                base64_img = process_product_image(uploaded_file)
                json_data = generate_json_structure(naskah_mentah)
                
                if isinstance(json_data, dict) and json_data.get("error") == "429":
                    st.error("⏳ Server sedang padat. Tunggu 1 menit ya.")
                else:
                    st.success("✨ Visual Berhasil Dicetak!")
                    theme = random.choice(["minimalist", "elegant_dark", "modern_gradient", "earthy_nature", "vibrant_pop"])
                    
                    # Gabungkan semua slide ke dalam satu string HTML
                    all_slides_html = ""
                    for slide in json_data:
                        all_slides_html += render_html_poster(slide, base64_img, layout_choice, theme, mode_foto)
                    
                    st.session_state.last_full_html = all_slides_html
                    
    # Area Output (Main Page)
    if "last_full_html" in st.session_state:
        st.components.v1.html(st.session_state.last_full_html, height=850, scrolling=True)
        
        # Tombol Download Bersih
        st.download_button(
            label="📥 Unduh Hasil Desain",
            data=f"<html><body style='margin:0; background:#f0f2f6; display:flex; flex-direction:column; align-items:center; padding:40px;'>{st.session_state.last_full_html}</body></html>",
            file_name="desain_studio_kreatif.html",
            mime="text/html",
            use_container_width=True
        )

    # Panduan Manual 2 Langkah & Multi-slide
    st.markdown("---")
    st.markdown(create_manual_guide(naskah_mentah))
