import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Configuración de la página
st.set_page_config(page_title="Procesador de Preguntas (QxMedic)", layout="centered")

st.title("Procesador de Preguntas (QxMedic)")
st.info("Recomendaciones:\n1. Quitar cabeceras\n2. Empezar desde A1\n3. No dejar espacio entre filas ni columnas\n4. Mantener la última columna como letra respuesta en mayúscula\n5. Tenerlo en la primera hoja")

# UI: Selección de formato (solo Excel habilitado)
st.radio("¿Qué tipo de documento deseas procesar?", ["Excel"], index=0, horizontal=True)

# Carga de archivo
uploaded_file = st.file_uploader("Subir documento", type=["xlsx", "xls"])

# Inputs
curso = st.text_input("Curso")
profesor = st.text_input("Profesor")
ancho_px = st.number_input("Ancho (px)", value=350)

# Función para generar imagen
def generar_imagen_pregunta(texto, ancho):
    # Configuración básica de imagen (altura dinámica)
    alto = 200 # Valor base
    img = Image.new('RGB', (ancho, alto), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Envolver texto
    lineas = textwrap.wrap(texto, width=30)
    y_text = 20
    for linea in lineas:
        d.text((10, y_text), linea, fill=(0, 0, 0))
        y_text += 20
        
    return img

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Botón Generar CSV
    if st.button("Generar CSV"):
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        st.download_button(
            label="Descargar CSV",
            data=csv_buffer.getvalue(),
            file_name="preguntas.csv",
            mime="text/csv"
        )

    # Botón Descargar Imágenes (ZIP)
    if st.button("Descargar Todas las Imágenes (ZIP)"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                # Asumiendo que la pregunta está en la columna 1 (índice 0)
                texto_pregunta = str(row.iloc[0])
                img = generar_imagen_pregunta(texto_pregunta, ancho_px)
                
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                zip_file.writestr(f"pregunta_{index+1}.jpg", img_byte_arr.getvalue())
        
        st.download_button(
            label="Descargar ZIP",
            data=zip_buffer.getvalue(),
            file_name="imagenes_preguntas.zip",
            mime="application/zip"
        )