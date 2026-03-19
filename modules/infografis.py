import streamlit as st
import re
import json
import requests
import base64
import time
import textwrap
import urllib.request
from io import BytesIO

# Memasukkan library pengolah gambar bawaan Python (Pillow)
from PIL import Image, ImageDraw, ImageFont

# ==========================================
# 🧩 1. HUGGING FACE IMAGE GENERATOR (FLUX)
# ==========================================
def generate_image_with_retry(prompt, dimensi=""):
    """Menggunakan model FLUX.1 yang lebih modern dan anti-error di Hugging Face."""
    hf_key = st.secrets.get("HUGGINGFACE_API_KEY")
    if not hf_key:
        st.warning("⚠️ Kunci HUGGINGFACE_API_KEY tidak ditemukan!")
        return None
        
    # Menggunakan FLUX.1-schnell (Sangat cepat dan realistis)
    API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
    headers = {"Authorization": f"Bearer {hf_key}"}
    
    # Resolusi default untuk ilustrasi tengah (Kita pakai square agar mudah di-layout)
    w, h = 1024, 1024 

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
                time.sleep(5) # Tunggu mesin pemanasan
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
    Menggunakan Groq untuk menstrukturkan data menjadi format Judul, Gambar, dan Poin-poin.
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
Tugasmu merangkum teks menjadi format infografis padat.
Format output HARUS JSON valid dengan struktur berikut:
{{
  "infographic_title": "Judul Utama Poster",
  "image_prompt": "professional illustration, clean vector, minimalist, highly detailed, [objek utama]...",
  "items": [
    {{
      "title": "Sub Judul Poin 1",
      "content": "Penjelasan sangat singkat, maksimal 2 baris."
    }},
    {{
      "title": "Sub Judul Poin 2",
      "content": "Penjelasan sangat singkat, maksimal 2 baris."
    }}
  ]
}}
ATURAN MUTLAK: Buat jumlah item dalam array 'items' sesuai dengan permintaan pengguna berikut: {opsi_slide}. Jika diminta '1 Slide', buatlah 4-5 poin utama agar pas di dalam satu halaman poster."""

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
# 🧩 3. AUTO-LAYOUT ENGINE (PILLOW POSTER MAKER)
# ==========================================
def get_text_dimensions(draw, text, font):
    """Fungsi pembantu dimensi font agar kompatibel dengan berbagai versi server"""
    if hasattr(draw, 'textbbox'):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    else:
        return draw.textsize(text, font=font)

@st.cache_resource
def load_fonts():
    """Mengunduh font standar industri (Roboto) untuk layout"""
    try:
        url_bold = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        url_reg = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
        
        bold_bytes = BytesIO(urllib.request.urlopen(url_bold).read())
        reg_bytes = BytesIO(urllib.request.urlopen(url_reg).read())
        
        return {
            "title": ImageFont.truetype(bold_bytes, 60),
            "subtitle": ImageFont.truetype(bold_bytes, 40),
            "body": ImageFont.truetype(reg_bytes, 32)
        }
    except:
        default = ImageFont.load_default()
        return {"title": default, "subtitle": default, "body": default}

def create_infographic_poster(data_json, b64_img, opsi_dimensi):
    """Menggabungkan Ilustrasi AI dan Teks ke dalam SATU Gambar PNG."""
    fonts = load_fonts()
    
    # 1. Tentukan Lebar Kanvas berdasarkan Dimensi
    canvas_w = 1080
    if "Landscape" in opsi_dimensi:
        canvas_w = 1920
        
    # Warna Tema (Desain Modern Bersih)
    bg_color = (235, 245, 250) # Light blueish gray
    card_color = (255, 255, 255)
    text_dark = (30, 50, 70)
    text_gray = (90, 100, 110)
    primary_color = (20, 120, 100) # Dark Cyan
    
    # Kita buat kanvas super tinggi sementara, nanti di-crop sesuai isi
    img = Image.new('RGB', (canvas_w, 4000), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    current_y = 80
    
    # 2. Cetak Judul Utama (Rata Tengah)
    title = data_json.get("infographic_title", "Infografis Modern")
    # Wrap teks agar tidak tumpah ke luar batas
    wrap_width = 30 if canvas_w == 1080 else 55
    wrapped_title = textwrap.wrap(title.upper(), width=wrap_width)
    
    for line in wrapped_title:
        tw, th = get_text_dimensions(draw, line, fonts["title"])
        x_pos = (canvas_w - tw) // 2
        draw.text((x_pos, current_y), line, font=fonts["title"], fill=primary_color)
        current_y += th + 15
    current_y += 50
    
    # 3. Cetak dan Tempel Ilustrasi dari Hugging Face
    if b64_img:
        try:
            img_data = base64.b64decode(b64_img.split(",")[1])
            hf_image = Image.open(BytesIO(img_data)).convert("RGBA")
            
            # Hitung skala ukuran gambar (Lebar max 800px)
            target_w = 800 if canvas_w == 1080 else 1000
            ratio = target_w / hf_image.width
            target_h = int(hf_image.height * ratio)
            hf_image = hf_image.resize((target_w, target_h), Image.Resampling.LANCZOS)
            
            # Buat sudut melengkung pada ilustrasi
            mask = Image.new('L', (target_w, target_h), 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle((0, 0, target_w, target_h), radius=40, fill=255)
            
            img.paste(hf_image, ((canvas_w - target_w) // 2, current_y), mask)
            current_y += target_h + 80
        except Exception as e:
            print(f"Error pasting image: {e}")
            
    # 4. Cetak Kartu-Kartu Poin (Teks Keterangan)
    items = data_json.get("items", [])
    box_x = 80 if canvas_w == 1080 else 200
    box_w = canvas_w - (box_x * 2)
    
    for idx, item in enumerate(items):
        item_title = f"{idx+1}. {item.get('title', '')}"
        item_content = item.get('content', '')
        
        wrap_tw = 40 if canvas_w == 1080 else 80
        wrap_cw = 50 if canvas_w == 1080 else 100
        
        wrapped_ititle = textwrap.wrap(item_title, width=wrap_tw)
        wrapped_icontent = textwrap.wrap(item_content, width=wrap_cw)
        
        # Hitung tinggi kotak
        box_h = 40
        for line in wrapped_ititle:
            tw, th = get_text_dimensions(draw, line, fonts["subtitle"])
            box_h += th + 10
        for line in wrapped_icontent:
            tw, th = get_text_dimensions(draw, line, fonts["body"])
            box_h += th + 10
            
        # Gambar kotak putih membulat
        draw.rounded_rectangle([box_x, current_y, box_x + box_w, current_y + box_h], 
                               radius=25, fill=card_color, outline=(200, 220, 230), width=4)
        
        # Cetak Teks di dalam kotak
        text_y = current_y + 25
        for line in wrapped_ititle:
            draw.text((box_x + 40, text_y), line, font=fonts["subtitle"], fill=text_dark)
            tw, th = get_text_dimensions(draw, line, fonts["subtitle"])
            text_y += th + 10
            
        text_y += 10
        for line in wrapped_icontent:
            draw.text((box_x + 40, text_y), line, font=fonts["body"], fill=text_gray)
            tw, th = get_text_dimensions(draw, line, fonts["body"])
            text_y += th + 10
            
        current_y += box_h + 40 # Jarak antar kotak
        
    # 5. Potong kanvas memanjang agar pas (Crop)
    final_h = current_y + 60
    img = img.crop((0, 0, canvas_w, final_h))
    
    # 6. Ekspor menjadi Base64 dan Bytes
    output = BytesIO()
    img.save(output, format="PNG")
    img_bytes = output.getvalue()
    
    encoded = base64.b64encode(img_bytes).decode('utf-8')
    return f"data:image/png;base64,{encoded}", img_bytes


# ==========================================
# 🚀 MAIN APP RUNNER
# ==========================================
def run():
    st.title("🎨 Ruang 3: Studio Cetak (Visual & Infografis)")
    st.info("💡 **Ditenagai Groq Llama & Layout Engine Khusus:** Sistem akan menyusun teks dan menggambar ilustrasi menjadi **SATU file poster PNG** utuh yang siap Anda unduh.")

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
                "1080 x 1080 px (Square / IG Feed)",
                "1920 x 1080 px (Landscape / Presentasi PPT / YouTube)"
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
            
        with st.spinner("🤖 Groq Llama 3.3 sedang membaca naskah dan merangkum poin-poin..."):
            try:
                # 1. Analisis Naskah dengan Groq
                structured_data = generate_structured_text_groq(user_input, jawaban_slide)
                
                with st.spinner("🎨 AI Pelukis sedang menggambar ilustrasi utama (sekitar 15-30 detik)..."):
                    # 2. Gambar ilustrasi
                    img_prompt = structured_data.get("image_prompt", "Professional vector infographic illustration")
                    b64_illustration = generate_image_with_retry(img_prompt, opsi_dimensi)
                    
                    with st.spinner("📐 Layout Engine sedang menata letak teks dan gambar menjadi Poster PNG..."):
                        # 3. Tata letak (Typesetting) menggunakan Python Pillow
                        final_b64, final_bytes = create_infographic_poster(structured_data, b64_illustration, opsi_dimensi)
                        
                        st.success("🎉 Infografis berhasil dirender secara utuh!")
                        
                        # 4. Tampilkan Gambar Final dan Tombol Download
                        st.image(final_bytes, caption="Hasil Cetak Infografis (Teks & Gambar Menyatu)", use_container_width=True)
                        
                        st.download_button(
                            label="⬇️ Download Poster Infografis (PNG)",
                            data=final_bytes,
                            file_name="infografis_final.png",
                            mime="image/png",
                            use_container_width=True,
                            type="primary"
                        )
                        
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
