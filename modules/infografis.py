import streamlit as st
import google.generativeai as genai
import json
import random
import base64
import re
from io import BytesIO
from PIL import Image
# PENTING: import rembg DIHAPUS dari sini untuk mencegah aplikasi stuck di awal (Lazy Loading)
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
# FUNGSI: PEMROSESAN GAMBAR (RESIZE & REMBG)
# ==========================================
def process_product_image(uploaded_file):
    """
    Mengubah ukuran gambar maksimal 800x800px lalu menghapus background.
    Mengembalikan string base64 untuk dirender di HTML.
    """
    try:
        # [SOLUSI STUCK]: Lazy Loading import rembg
        # rembg hanya dipanggil saat fungsi ini benar-benar dijalankan oleh tombol
        from rembg import remove 

        # Buka gambar menggunakan Pillow
        image = Image.open(uploaded_file)
        
        # [CRITICAL] Resize gambar untuk menyelamatkan RAM Server Streamlit
        image.thumbnail((800, 800))
        
        # Konversi ke format byte
        buf = BytesIO()
        image.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        # Hapus background menggunakan rembg
        with st.spinner("✨ Sedang memotong background gambar secara otomatis (Mungkin butuh waktu beberapa detik pada proses pertama)..."):
            output_bytes = remove(byte_im)
            
        # Ubah ke base64 agar bisa disematkan langsung ke dalam HTML tag <img>
        base64_img = base64.b64encode(output_bytes).decode('utf-8')
        return f"data:image/png;base64,{base64_img}"
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses gambar: {e}")
        return None

# ==========================================
# FUNGSI: EKSTRAKSI NASKAH KE JSON (GEMINI)
# ==========================================
def generate_json_structure(naskah):
    """
    Mengubah naskah mentah menjadi struktur JSON menggunakan Gemini 2.5 Flash.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"""
    Anda adalah asisten desainer grafis. Ubah naskah promosi berikut menjadi struktur data JSON murni untuk keperluan desain infografis/poster.
    Jangan tambahkan markdown ```json atau teks lain, cukup outputkan JSON valid.

    Format wajib JSON:
    {{
        "slide_number": 1,
        "infographic_title": "Judul Singkat Menarik",
        "items": ["Keunggulan 1", "Keunggulan 2", "Call to action"]
    }}

    Naskah Mentah:
    {naskah}
    """
    
    try:
        response = model.generate_content(prompt)
        # Ekstrak JSON menggunakan regex untuk mengantisipasi jika Gemini masih mengembalikan markdown
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
        else:
            # Fallback jika tidak ada bracket JSON
            return json.loads(response.text)
            
    except ResourceExhausted:
        # Tangkap error 429 Quota Exceeded
        return {"error": "429"}
    except Exception as e:
        if "429" in str(e):
             return {"error": "429"}
        return {"error": str(e)}

# ==========================================
# FUNGSI: ENGINE TEMA CSS & LAYOUTING
# ==========================================
def get_theme_css(theme_name, layout_type):
    """
    Menyediakan 5 tema acak dan mengatur responsivitas layout.
    """
    # Pengaturan Layout Dimensi
    if layout_type == "Square (1:1)":
        aspect_ratio = "1 / 1"
        max_width = "500px"
    elif layout_type == "Portrait (3:4)":
        aspect_ratio = "3 / 4"
        max_width = "400px"
    else: # Landscape (16:9)
        aspect_ratio = "16 / 9"
        max_width = "700px"

    # Palet Tema
    themes = {
        "minimalist": {
            "bg": "#ffffff", "text": "#333333", "accent": "#f0f0f0", "font": "Arial, sans-serif"
        },
        "elegant_dark": {
            "bg": "#1a1a2e", "text": "#e94560", "accent": "#16213e", "font": "'Georgia', serif", "text_white": "#ffffff"
        },
        "modern_gradient": {
            "bg": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)", "text": "#ffffff", "accent": "rgba(255,255,255,0.2)", "font": "'Helvetica Neue', sans-serif"
        },
        "earthy_nature": {
            "bg": "#e9e5cd", "text": "#4b6542", "accent": "#d4cda3", "font": "'Trebuchet MS', sans-serif"
        },
        "vibrant_pop": {
            "bg": "#ffdf00", "text": "#ff007f", "accent": "#00d2ff", "font": "'Impact', sans-serif", "text_dark": "#111111"
        }
    }
    
    t = themes.get(theme_name, themes["minimalist"])
    
    # Warna teks sekunder (handling untuk tema gelap/terang)
    color_main = t.get("text_white", t["text"]) if theme_name in ["modern_gradient"] else t["text"]
    color_item = t.get("text_dark", color_main)
    
    css = f"""
    <style>
        .poster-container {{
            width: 100%;
            max-width: {max_width};
            aspect-ratio: {aspect_ratio};
            background: {t['bg']};
            color: {color_main};
            font-family: {t['font']};
            margin: 0 auto;
            position: relative;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            padding: 30px;
            box-sizing: border-box;
        }}
        .poster-header {{
            text-align: center;
            font-size: 1.8em;
            font-weight: bold;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
            z-index: 2;
        }}
        .poster-content {{
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: center;
            flex-grow: 1;
            gap: 20px;
            z-index: 2;
        }}
        .poster-image {{
            flex: 1;
            display: flex;
            justify-content: center;
        }}
        .poster-image img {{
            max-width: 100%;
            max-height: 250px;
            object-fit: contain;
            /* [CRITICAL] Efek 3D Melayang sesuai request */
            filter: drop-shadow(0px 25px 35px rgba(0,0,0,0.25));
        }}
        .poster-items {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .item-box {{
            background: {t['accent']};
            color: {color_item};
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.9em;
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        .poster-footer {{
            text-align: center;
            font-size: 0.75em;
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid rgba(128,128,128,0.3);
            z-index: 2;
            font-weight: bold;
        }}
        .poster-footer div {{
            margin-bottom: 4px;
        }}
    </style>
    """
    return css

def render_html_poster(json_data, base64_img, layout_type, theme_name):
    """
    Menggabungkan CSS, Data JSON, dan Gambar ke dalam satu komponen HTML.
    """
    css = get_theme_css(theme_name, layout_type)
    
    title = json_data.get("infographic_title", "Visual Produk")
    items = json_data.get("items", [])
    
    items_html = ""
    for item in items:
        items_html += f"<div class='item-box'>✓ {item}</div>"

    html = f"""
    {css}
    <div class="poster-container">
        <div class="poster-header">{title}</div>
        
        <div class="poster-content">
            <div class="poster-items">
                {items_html}
            </div>
            <div class="poster-image">
                <img src="{base64_img}" alt="Product Image">
            </div>
        </div>
        
        <div class="poster-footer">
            <div>Studio Kreatif Pro - KTB UKM JATIM</div>
            <div>📸 @ktbukm.jatim | 🌐 [https://ktbukm-jatim.store](https://ktbukm-jatim.store)</div>
        </div>
    </div>
    """
    return html

# ==========================================
# FUNGSI: BACKUP PROMPT MANUAL
# ==========================================
def create_manual_prompt(naskah):
    """
    Mencetak instruksi copas untuk pengguna yang ingin menggenerate gambar di platform luar.
    """
    prompt = f"""
    *Salin teks di bawah ini dan tempel di ChatGPT atau Gemini Web:*

    "Buatkan saya ide desain infografis atau poster untuk mempromosikan produk saya. 
    Gunakan elemen visual yang menarik dan layout yang profesional.
    
    Berikut adalah naskah dasar yang ingin saya sampaikan:
    {naskah}
    
    Tolong berikan rekomendasi warna, tata letak teks, dan konsep gambar yang cocok."
    """
    return prompt

# ==========================================
# MODUL UTAMA RUN()
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak / Visual")
    st.markdown("Buat visual promosi produk UMKM Anda dengan cepat, elegan, dan tanpa ribet.")
    
    setup_gemini()

    # Ambil naskah dari Ruang sebelumnya (st.session_state)
    naskah_mentah = st.session_state.get("hasil_naskah", "")
    
    if not naskah_mentah:
        st.info("ℹ️ Anda belum memiliki naskah. Silakan buat naskah di Ruang Copywriting terlebih dahulu.")
        naskah_mentah = "Ini adalah contoh naskah default karena belum ada naskah dari sesi sebelumnya. Produk berkualitas tinggi, harga terjangkau, dan ramah lingkungan."
    else:
        with st.expander("📄 Lihat Naskah Aktif Anda"):
            st.write(naskah_mentah)

    st.markdown("---")
    st.markdown("### 1. Unggah Foto Produk (Wajib)")
    st.caption("Unggah foto produk Anda. Sistem akan otomatis memotong background dan memberikan efek 3D.")
    
    uploaded_file = st.file_uploader("Pilih foto produk (JPG/PNG)", type=['jpg', 'jpeg', 'png'])
    
    col1, col2 = st.columns(2)
    with col1:
        layout_choice = st.selectbox("Pilih Dimensi Visual:", ["Square (1:1)", "Portrait (3:4)", "Landscape (16:9)"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Logika jika tombol ditekan
    if st.button("🚀 Buat Desain Visual Sekarang!", type="primary"):
        
        if not uploaded_file:
            # SYARAT WAJIB: Jika tidak ada gambar, munculkan peringatan & hentikan render HTML
            st.warning("⚠️ Halo Kak! Anda belum mengunggah foto produk. Untuk hasil desain yang maksimal, mohon unggah foto produknya dulu ya di atas.")
            
            # Tetap tampilkan Prompt Manual di bawah peringatan
            st.markdown("### Instruksi Praktis Prompt Manual")
            st.info("Jika Anda ingin membuat desain secara manual di platform lain (seperti Canva/ChatGPT), Anda bisa menyalin panduan berikut:")
            st.code(create_manual_prompt(naskah_mentah), language="text")
            
        else:
            # PROSES JIKA GAMBAR ADA
            # 1. Proses Gambar (Resize & Rembg)
            base64_img = process_product_image(uploaded_file)
            
            if base64_img:
                # 2. Proses Teks ke JSON
                with st.spinner("🤖 Mengonversi naskah menjadi struktur infografis..."):
                    json_data = generate_json_structure(naskah_mentah)
                
                # Handling Error Limit Kuota Gemini
                if isinstance(json_data, dict) and json_data.get("error") == "429":
                    st.error("⏳ Server Google sedang mendinginkan mesin. Tunggu 1 menit lalu tekan tombol lagi.")
                elif isinstance(json_data, dict) and "error" in json_data:
                    st.error(f"Gagal memproses teks: {json_data['error']}")
                else:
                    st.success("Visual berhasil dibuat!")
                    
                    # 3. Pilih Tema Acak
                    themes_list = ["minimalist", "elegant_dark", "modern_gradient", "earthy_nature", "vibrant_pop"]
                    chosen_theme = random.choice(themes_list)
                    st.caption(f"🎨 Tema Terpilih: **{chosen_theme.replace('_', ' ').title()}**")
                    
                    # 4. Render HTML
                    html_poster = render_html_poster(json_data, base64_img, layout_choice, chosen_theme)
                    st.components.v1.html(html_poster, height=600, scrolling=True)
                    
            # Tampilkan Backup Prompt Manual di akhir sukses
            st.markdown("---")
            st.markdown("### 💡 Instruksi Praktis Prompt Manual")
            st.code(create_manual_prompt(naskah_mentah), language="text")
