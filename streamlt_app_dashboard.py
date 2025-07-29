import streamlit as st
from PIL import Image, ImageDraw
import numpy as np

st.title("Ejemplo: 3 filas x 3 columnas con border=True")

# Función para crear imagen random simple
def create_random_image():
    img = Image.new('RGB', (100, 100), color=(np.random.randint(255), np.random.randint(255), np.random.randint(255)))
    draw = ImageDraw.Draw(img)
    draw.text((10,40), "Img", fill=(255,255,255))
    return img

# --- FILA 1 ---
left, middle, right = st.columns(3, border=True)
left.markdown("Lorem ipsum " * 10)
middle.markdown("Lorem ipsum " * 5)
right.markdown("Lorem ipsum ")

# --- FILA 2 ---
left, middle, right = st.columns(3, border=True)
left.image(create_random_image())
middle.image(create_random_image())
right.image(create_random_image())

# --- FILA 3 ---
left, middle, right = st.columns(3, border=True)
left.image(create_random_image())
middle.image(create_random_image())
right.image(create_random_image())
