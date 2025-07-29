import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.title("3 filas x 3 columnas con bordes color #0089f9")

# CSS para bordes con color personalizado
st.markdown("""
<style>
.column-border {
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

# FILA 1
cols = st.columns(3)
texts = ["Lorem ipsum " * 10, "Lorem ipsum " * 5, "Lorem ipsum "]
for col, text in zip(cols, texts):
    with col:
        st.markdown(f'<div class="column-border">{text}</div>', unsafe_allow_html=True)

# FILA 2
cols = st.columns(3)
for col in cols:
    with col:
        st.markdown('<div class="column-border">', unsafe_allow_html=True)
        st.image(create_random_image())
        st.markdown('</div>', unsafe_allow_html=True)

# FILA 3
cols = st.columns(3)
for col in cols:
    with col:
        st.markdown('<div class="column-border">', unsafe_allow_html=True)
        st.image(create_random_image())
        st.markdown('</div>', unsafe_allow_html=True)
