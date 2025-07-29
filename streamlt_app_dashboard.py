import streamlit as st

# Forzar modo wide
st.set_page_config(layout="wide")

st.title("3 filas x 3 columnas con border=True")

# FILA 1
left, middle, right = st.columns(3, border=True)
left.markdown("Lorem ipsum " * 10)
middle.markdown("Lorem ipsum " * 5)
right.markdown("Lorem ipsum ")

# FILA 2
left, middle, right = st.columns(3, border=True)
left.markdown("Fila 2 - Col 1")
middle.markdown("Fila 2 - Col 2")
right.markdown("Fila 2 - Col 3")

# FILA 3
left, middle, right = st.columns(3, border=True)
left.markdown("Fila 3 - Col 1")
middle.markdown("Fila 3 - Col 2")
right.markdown("Fila 3 - Col 3")
