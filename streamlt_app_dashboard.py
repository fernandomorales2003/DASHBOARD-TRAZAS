import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.title("3 filas x 3 columnas con borde color #0089f9 aplicado a columnas")

# CSS para aplicar borde a cada columna (contenedor completo)
st.markdown("""
<style>
div[data-testid="column"] {
    border: 2px solid #0089f9;
    padding: 10px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

def create_random_image():
    img = Image.new('RGB', (100, 100), color=(np.random.randint(255), np.random.randint(255), np.random.randint(255)))
    draw = ImageDraw.Draw(img)
    draw.text((10,40), "Img", fill=(255,255,255))
    return img

# FILA 1 (Texto)
cols = st.columns(3)
texts = ["Lorem ipsum " * 10, "Lorem ipsum " * 5, "Lorem ipsum "]
for col, text in zip(cols, texts):
    with col:
        st.markdown(text)

# FILA 2 (
