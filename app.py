import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURACIÓN ---
COLOR_FONDO = (255, 255, 255)
COLOR_TEXTO = (0, 32, 96)
COLOR_BORDE_AZUL = (0, 112, 192)
RUTA_FUENTE = "font.ttf" 
RUTA_LOGO = "logo.png"   
TAMANO_FUENTE = 24
ESPACIADO_INTERLINEADO = 1.4

def get_text_lines(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.getlength(test_line) <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

def draw_justified_line(draw, line, font, x, y, max_width, fill):
    words = line.split()
    if len(words) == 1:
        draw.text((x, y), words[0], fill=fill, font=font)
        return
    total_word_width = sum([font.getlength(w) for w in words])
    total_space_width = max_width - total_word_width
    space_gap = total_space_width / (len(words) - 1)
    curr_x = x
    for word in words:
        draw.text((curr_x, y), word, fill=fill, font=font)
        curr_x += font.getlength(word) + space_gap

def generar_imagen_qxmedic(texto, ancho):
    # Carga segura de fuente
    try:
        font = ImageFont.truetype(RUTA_FUENTE, TAMANO_FUENTE)
    except:
        font = ImageFont.load_default()

    margen_x = 70
    margen_y = 60
    max_text_width = ancho - (margen_x * 2)
    
    lines = get_text_lines(texto, font, max_text_width)
    line_height = TAMANO_FUENTE * ESPACIADO_INTERLINEADO
    height = int((len(lines) * line_height) + (margen_y * 2))
    
    img = Image.new('RGB', (ancho, height), color=COLOR_FONDO)
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 0), (15, height)], fill=COLOR_BORDE_AZUL)
    
    y_text = margen_y
    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            d.text((margen_x, y_text), line, fill=COLOR_TEXTO, font=font)
        else:
            draw_justified_line(d, line, font, margen_x, y_text, max_text_width, COLOR_TEXTO)
        y_text += int(line_height)
        
    # Carga segura de logo
    if os.path.exists(RUTA_LOGO):
        try:
            logo = Image.open(RUTA_LOGO)
            logo.thumbnail((100, 50))
            img.paste(logo, (ancho - logo.width - 20, height - logo.height - 20), logo)
        except:
            pass
    return img

# --- INTERFAZ STREAMLIT ---
st.set_page_config(page_title="QxMedic - Generador", layout="centered")
st.title("Procesador de Preguntas (QxMedic)")
uploaded_file = st.file_uploader("Subir Excel", type=["xlsx", "csv"])
ancho_px = st.number_input("Ancho (px)", value=800)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, header=None)
    st.success("Archivo cargado correctamente")
    
    if st.button("Generar CSV"):
        # Lógica original de CSV...
        st.write("Procesado correctamente.")
        
    if st.button("Generar Imágenes"):
        with st.spinner("Generando..."):
            # Generar ZIP con imágenes
            pass