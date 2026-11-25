import sys
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image, ImageOps

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.inferencia import analizar

FRUTAS = ["manzana", "banano", "guayaba", "limon", "naranja", "granada"]

st.set_page_config(page_title="Calidad de frutas", layout="centered")
st.title("Clasificación de calidad y tamaño de frutas")

fruta = st.selectbox("Fruta", FRUTAS)
origen = st.radio("Imagen", ["Cargar archivo", "Usar cámara"], horizontal=True)
archivo = st.file_uploader("Fotografía", type=["jpg", "jpeg", "png"]) if origen == "Cargar archivo" else st.camera_input("Cámara")

if archivo is not None:
    rgb = np.asarray(ImageOps.exif_transpose(Image.open(archivo)).convert("RGB"))
    resultado = analizar(rgb, fruta)

    izquierda, derecha = st.columns(2)
    izquierda.image(rgb, caption="Imagen original")
    derecha.image(resultado["recorte"], caption="Fruta segmentada" if resultado["segmentada"] else "No se segmentó: se usa la imagen completa")

    st.subheader(f"Calidad (CNN): {resultado['calidad_cnn']}")
    st.bar_chart(resultado["probabilidades"])
    st.write(f"Calidad (SVM): **{resultado['calidad_svm']}**")
    if resultado["tamano"]:
        st.write(f"Tamaño: **{resultado['tamano']}** (diámetro normalizado {resultado['diametro_normalizado']:.2f})")
    else:
        st.write("Tamaño: no se pudo estimar")

    st.caption(
        "Herramienta de apoyo, no sustituye la decisión humana. El desempeño es menor con fotografías "
        "distintas a las del entrenamiento (iluminación y fondo), y el tamaño es relativo al encuadre."
    )
