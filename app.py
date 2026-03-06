import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

# ==============================================================================
# 1. CONFIGURACIÓN VISUAL (ESTILO QXMEDIC)
# ==============================================================================
# Colores (R, G, B)
COLOR_FONDO = (255, 255, 255)       # Blanco
COLOR_TEXTO = (0, 32, 96)          # Azul Marino QxMedic
COLOR_BORDE_AZUL = (0, 112, 192)    # Azul Brillante Borde

# Fuentes y Tamaños (Requiere archivos locales)
# Asegúrate de subir 'font.ttf' y 'logo.png' a tu repo de GitHub
RUTA_FUENTE = "font.ttf"  # Sube tu archivo de fuente .ttf
RUTA_LOGO = "logo.png"    # Sube tu logo .png transparente
TAMANO_FUENTE = 28
ESPACIADO_INTERLINEADO = 1.3

# Márgenes y Dimensiones
MARGEN_IZQUIERDO_TEXTO = 60  # Espacio para el borde azul
MARGEN_SUPERIOR_TEXTO = 50
ANCHO_BORDE_AZUL = 15
# ==============================================================================

# Configuración de página
st.set_page_config(page_title="Procesador de Preguntas (QxMedic)", layout="centered")

st.title("Procesador de Preguntas (QxMedic)")
st.info("Recomendaciones:\n1. Quitar cabeceras\n2. Empezar desde A1\n3. No dejar espacio entre filas ni columnas\n4. Mantener la última columna como letra respuesta en mayúscula\n5. Tenerlo en la primera hoja")

# Carga de archivo
uploaded_file = st.file_uploader("Subir documento Excel", type=["xlsx", "csv"])

# Inputs adicionales
ancho_px = st.number_input("Ancho de imagen (px)", value=900)

def procesar_df(df):
    """
    Transforma el df de entrada al formato CSV requerido para Poll.
    """
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

def generar_imagen_qxmedic(texto, ancho):
    """
    Genera una imagen profesional con el estilo visual de QxMedic.
    """
    # 1. Intentar cargar fuente y logo
    try:
        fuente = ImageFont.truetype(RUTA_FUENTE, TAMANO_FUENTE)
    except IOError:
        st.warning(f"No se encontró '{RUTA_FUENTE}'. Usando fuente básica (el diseño se verá diferente).")
        fuente = ImageFont.load_default()

    # 2. Envolver texto para calcular altura dinámica
    # Ajusta el width según el ancho de imagen y tamaño de fuente
    ancho_texto_disponible = ancho - MARGEN_IZQUIERDO_TEXTO - 40
    lineas = textwrap.wrap(texto, width=50) # Ajuste manual del width de wrap
    
    # Calcular altura dinámica
    # Esto es una estimación; para precisión real se requiere font.getsize()
    altura_texto = (len(lineas) * TAMANO_FUENTE * ESPACIADO_INTERLINEADO)
    altura_final = int(altura_texto + (MARGEN_SUPERIOR_TEXTO * 2))

    # 3. Crear lienzo base
    img = Image.new('RGB', (ancho, altura_final), color=COLOR_FONDO)
    d = ImageDraw.Draw(img)

    # 4. Dibujar Borde Lateral Azul QxMedic
    d.rectangle([(0, 0), (ANCHO_BORDE_AZUL, altura_final)], fill=COLOR_BORDE_AZUL)

    # 5. Dibujar Texto
    y_text = MARGEN_SUPERIOR_TEXTO
    for linea in lineas:
        d.text((MARGEN_IZQUIERDO_TEXTO, y_text), linea, fill=COLOR_TEXTO, font=fuente)
        y_text += int(TAMANO_FUENTE * ESPACIADO_INTERLINEADO)

    # 6. Añadir Logo (Si existe)
    if os.path.exists(RUTA_LOGO):
        try:
            logo = Image.open(RUTA_LOGO)
            # Redimensionar logo manteniendo proporción (ej. altura 60px)
            ancho_logo, alto_logo = logo.size
            nueva_altura_logo = 60
            nueva_anchura_logo = int((nueva_altura_logo * ancho_logo) / alto_logo)
            logo_res = logo.resize((nueva_anchura_logo, nueva_altura_logo), Image.ANTIALIAS)
            
            # Pegar logo en la esquina inferior derecha (con margen)
            pos_x = ancho - nueva_anchura_logo - 20
            pos_y = altura_final - nueva_altura_logo - 20
            img.paste(logo_res, (pos_x, pos_y), logo_res) # Tercer arg es la máscara alpha
        except Exception as e:
            st.error(f"Error cargando el logo: {e}")

    return img

if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        df = pd.read_excel(uploaded_file, header=None)
    
    st.write("Vista previa de los datos de entrada (Excel):")
    st.dataframe(df.head())
    
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generar CSV para Poll"):
            df_export = procesar_df(df)
            csv_buffer = io.BytesIO()
            df_export.to_csv(csv_buffer, index=False, encoding='utf-8')
            st.download_button("Descargar CSV Formateado", csv_buffer.getvalue(), "preguntas_poll.csv", "text/csv")

    with col2:
        if st.button("Descargar Imágenes Estilo QxMedic (ZIP)"):
            with st.spinner("Generando imágenes profesionales..."):
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                    for i, row in df.iterrows():
                        # Usar la nueva función de generación visual
                        img = generar_imagen_qxmedic(str(row.iloc[0]), ancho_px)
                        img_io = io.BytesIO()
                        img.save(img_io, format='JPEG', quality=95) # Calidad alta
                        zip_file.writestr(f"pregunta_{i+1}.jpg", img_io.getvalue())
                
                st.download_button("Descargar ZIP Imágenes", zip_buffer.getvalue(), "preguntas_imagenes_qxmedic.zip", "application/zip")