import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURACIÓN CSS CORPORATIVA ---
st.set_page_config(page_title="QxMedic | Procesador", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; font-weight: bold; background-color: #0070c0; color: white; }
    .stButton>button:hover { background-color: #003260; }
    h1 { color: #003260; }
    </style>
    """, unsafe_allow_html=True)

# --- CONFIGURACIONES (Mismas funciones de lógica que ya tenías) ---
COLOR_FONDO, COLOR_TEXTO, COLOR_BORDE_AZUL = (255,255,255), (0,32,96), (0,112,192)
RUTA_FUENTE, RUTA_LOGO = "font.ttf", "logo.png"
TAMANO_FUENTE, ESPACIADO_INTERLINEADO = 24, 1.4

# [AQUÍ PEGA TUS FUNCIONES: get_text_lines, draw_justified_line, generar_imagen_qxmedic, procesar_df_csv]
# (Mantenlas igual que en tu código anterior para que no falle)

# --- INTERFAZ PROFESIONAL ---
with st.sidebar:
    st.image("https://via.placeholder.com/150", caption="QxMedic Tools") # Reemplaza con tu logo
    st.header("Configuración")
    uploaded_file = st.file_uploader("Cargar Excel/CSV", type=["xlsx", "csv"])
    ancho_px = st.number_input("Ancho de imagen (px)", value=800, step=50)
    st.divider()
    st.caption("Versión 1.0 - Procesador Médico")

st.title("Procesador de Preguntas QxMedic")
with st.expander("Ver recomendaciones de uso"):
    st.markdown("""
    * **Formato:** Asegúrate de no tener filas vacías al inicio.
    * **Estructura:** La última columna debe ser la respuesta (A, B, C, D).
    * **Imágenes:** El procesador detectará automáticamente las opciones correctas.
    """)

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=None) if not uploaded_file.name.endswith('.csv') else pd.read_csv(uploaded_file, header=None)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("1. Generar CSV")
        if st.button("Descargar CSV de Importación"):
            df_export = procesar_df_csv(df)
            csv = df_export.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Archivo", csv, "preguntas.csv", "text/csv")
            
    with col2:
        st.subheader("2. Generar Imágenes")
        if st.button("Generar Pack de Imágenes"):
            progress_bar = st.progress(0)
            zip_buffer = io.BytesIO()
            total = len(df)
            
            with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                for i, row in df.iterrows():
                    img = generar_imagen_qxmedic(str(row.iloc[0]), ancho_px)
                    img_io = io.BytesIO()
                    img.save(img_io, format='JPEG', quality=95)
                    zip_file.writestr(f"pregunta_{i+1}.jpg", img_io.getvalue())
                    progress_bar.progress((i + 1) / total)
            
            st.download_button("Descargar ZIP", zip_buffer.getvalue(), "preguntas_qxmedic.zip", "application/zip")
            st.success("¡Imágenes procesadas con éxito!")
else:
    st.info("Por favor, sube un archivo Excel para comenzar el procesamiento.")