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
RUTA_FUENTE = "font.ttf" # Asegúrate de que esté en tu repo
RUTA_LOGO = "logo.png"   # Asegúrate de que esté en tu repo
TAMANO_FUENTE = 24
ESPACIADO_INTERLINEADO = 1.4

def get_text_lines(text, font, max_width):
    """Divide el texto en líneas basándose en el ancho en píxeles."""
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
    """Dibuja una línea justificada."""
    words = line.split()
    if len(words) == 1:
        draw.text((x, y), words[0], fill=fill, font=font)
        return

    # Calcular espacio extra
    total_word_width = sum([font.getlength(w) for w in words])
    total_space_width = max_width - total_word_width
    space_gap = total_space_width / (len(words) - 1)
    
    curr_x = x
    for word in words:
        draw.text((curr_x, y), word, fill=fill, font=font)
        curr_x += font.getlength(word) + space_gap

def generar_imagen_qxmedic(texto, ancho):
    # 1. Cargar Fuente
    try:
        font = ImageFont.truetype(RUTA_FUENTE, TAMANO_FUENTE)
    except:
        font = ImageFont.load_default()

    # 2. Configurar medidas
    margen_x = 70
    margen_y = 60
    max_text_width = ancho - (margen_x * 2)
    
    # 3. Procesar líneas
    lines = get_text_lines(texto, font, max_text_width)
    line_height = TAMANO_FUENTE * ESPACIADO_INTERLINEADO
    
    # Altura auto-acoplada
    height = int((len(lines) * line_height) + (margen_y * 2))
    
    # 4. Dibujar
    img = Image.new('RGB', (ancho, height), color=COLOR_FONDO)
    d = ImageDraw.Draw(img)
    
    # Borde lateral
    d.rectangle([(0, 0), (15, height)], fill=COLOR_BORDE_AZUL)
    
    # Dibujar texto justificado
    y_text = margen_y
    for i, line in enumerate(lines):
        # La última línea no se justifica (se deja a la izquierda)
        if i == len(lines) - 1:
            d.text((margen_x, y_text), line, fill=COLOR_TEXTO, font=font)
        else:
            draw_justified_line(d, line, font, margen_x, y_text, max_text_width, COLOR_TEXTO)
        y_text += int(line_height)
        
    # 5. Logo
    if os.path.exists(RUTA_LOGO):
        logo = Image.open(RUTA_LOGO)
        logo.thumbnail((100, 50))
        img.paste(logo, (ancho - logo.width - 20, height - logo.height - 20), logo)
        
    return img

# --- RESTO DEL CÓDIGO (Streamlit UI igual que antes) ---
# ... (el resto de tu lógica de procesar_df y los botones de descarga sigue igual)