import streamlit as st
import pandas as pd
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Configuración de página
st.set_page_config(page_title="Procesador de Preguntas (QxMedic)", layout="centered")

st.title("Procesador de Preguntas (QxMedic)")
st.info("Recomendaciones:\n1. Quitar cabeceras\n2. Empezar desde A1\n3. No dejar espacio entre filas ni columnas\n4. Mantener la última columna como letra respuesta en mayúscula\n5. Tenerlo en la primera hoja")

# Carga de archivo
uploaded_file = st.file_uploader("Subir documento Excel", type=["xlsx", "csv"])

# Inputs adicionales
ancho_px = st.number_input("Ancho de imagen (px)", value=800)

def procesar_df(df):
    """
    Transforma el df de entrada al formato CSV requerido.
    Asume: Col0=Pregunta, Col1=NaN, Col2=A, Col3=B, Col4=C, Col5=D, Col6=Respuesta
    """
    # Crear nuevo df para exportación
    new_df = pd.DataFrame()
    new_df['Poll'] = ['Poll'] * len(df)
    new_df['Multiple choice'] = ['Multiple choice'] * len(df)
    new_df['Pregunta'] = [f'Pregunta {i+1}' for i in range(len(df))]
    
    # Mapeo de columnas a letras
    letra_a_col = {'A': 2, 'B': 3, 'C': 4, 'D': 5}
    
    for i, row in df.iterrows():
        resp = str(row.iloc[6]).strip().upper()
        # Limpiar opciones
        for col_idx in [2, 3, 4, 5]:
            val = str(row.iloc[col_idx])
            # Si esta columna corresponde a la respuesta, añadir ***
            if (col_idx == letra_a_col.get(resp)):
                val = f"***{val}"
            new_df.loc[i, f'Option_{col_idx}'] = val
            
    return new_df

def generar_imagen(texto, ancho):
    # Ajuste dinámico de altura (simple)
    lineas = textwrap.wrap(texto, width=50)
    altura = (len(lineas) * 30) + 40
    img = Image.new('RGB', (ancho, altura), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    y = 20
    for linea in lineas:
        d.text((20, y), linea, fill=(0, 0, 0))
        y += 30
    return img

if uploaded_file is not None:
    # Cargar archivo (detectar si es csv o excel)
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None)
    else:
        df = pd.read_excel(uploaded_file, header=None)
    
    # Mostrar vista previa
    st.write("Vista previa de los datos:")
    st.dataframe(df.head())
    
    if st.button("Generar CSV"):
        df_export = procesar_df(df)
        csv_buffer = io.BytesIO()
        df_export.to_csv(csv_buffer, index=False, encoding='utf-8')
        st.download_button("Descargar CSV Formateado", csv_buffer.getvalue(), "preguntas_procesadas.csv", "text/csv")

    if st.button("Descargar Todas las Imágenes (ZIP)"):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for i, row in df.iterrows():
                img = generar_imagen(str(row.iloc[0]), ancho_px)
                img_io = io.BytesIO()
                img.save(img_io, format='JPEG')
                zip_file.writestr(f"pregunta_{i+1}.jpg", img_io.getvalue())
        
        st.download_button("Descargar ZIP Imágenes", zip_buffer.getvalue(), "preguntas_imagenes.zip", "application/zip")