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

# Funciones de lógica (Justificación y Procesamiento)
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
        
    if os.path.exists(RUTA_LOGO):
        try:
            logo = Image.open(RUTA_LOGO)
            logo.thumbnail((100, 50))
            img.paste(logo, (ancho - logo.width - 20, height - logo.height - 20), logo)
        except:
            pass
    return img

def procesar_df_csv(df):
    new_df = pd.DataFrame()
    new_df['Poll'] = ['Poll'] * len(df)
    new_df['Multiple choice'] = ['Multiple choice'] * len(df)
    new_df['Pregunta'] = [f'Pregunta {i+1}' for i in range(len(df))]
    letra_a_col = {'A': 2, 'B': 3, 'C': 4, 'D': 5}
    
    for i, row in df.iterrows():
        resp = str(row.iloc[6]).strip().upper()
        for col_idx in [2, 3, 4, 5]:
            val = str(row.iloc[col_idx])
            if (col_idx == letra_a_col.get(resp)):
                val = f"***{val}"
            new_df.loc[i, f'Option_{col_idx}'] = val
    return new_df

# --- INTERFAZ ---
st.set_page_config(page_title="QxMedic - Generador", layout="centered")
st.title("Procesador de Preguntas (QxMedic)")
uploaded_file = st.file_uploader("Subir archivo", type=["xlsx", "csv"])
ancho_px = st.number_input("Ancho de imagen (px)", value=800)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, header=None) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, header=None)
    st.write("Datos cargados. ¿Qué deseas hacer?")
    
    if st.button("Generar CSV"):
        df_export = procesar_df_csv(df)
        csv_buffer = io.BytesIO()
        df_export.to_csv(csv_buffer, index=False, encoding='utf-8')
        st.download_button("Descargar CSV", csv_buffer.getvalue(), "preguntas.csv", "text/csv")
        st.success("CSV listo para descargar.")

    if st.button("Generar Imágenes"):
        with st.spinner("Generando imágenes..."):
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for i, row in df.iterrows():
                    img = generar_imagen_qxmedic(str(row.iloc[0]), ancho_px)
                    img_io = io.BytesIO()
                    img.save(img_io, format='JPEG', quality=95)
                    zip_file.writestr(f"pregunta_{i+1}.jpg", img_io.getvalue())
            st.download_button("Descargar ZIP Imágenes", zip_buffer.getvalue(), "preguntas.zip", "application/zip")
            st.success("Imágenes listas.")