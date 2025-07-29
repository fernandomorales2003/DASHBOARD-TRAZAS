import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")
st.title("📊 Grilla de 4 Filas x 3 Columnas con Gráficos")

def random_plot():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x + np.random.rand())
    ax.plot(x, y)
    return fig

# === FILA 1 === (30% - 50% - 20%)
cols1 = st.columns([0.3, 0.5, 0.2])
for i, col in enumerate(cols1):
    with col.container():
        st.subheader(f"Fila 1 - Columna {i+1}")
        st.pyplot(random_plot())

# === FILA 2 === (30% - 50% - 20%)
cols2 = st.columns([0.3, 0.5, 0.2])
for i, col in enumerate(cols2):
    with col.container():
        st.subheader(f"Fila 2 - Columna {i+1}")
        st.pyplot(random_plot())

# === FILA 3 === (30% - 50% - 20%)
cols3 = st.columns([0.3, 0.5, 0.2])
for i, col in enumerate(cols3):
    with col.container():
        st.subheader(f"Fila 3 - Columna {i+1}")
        st.pyplot(random_plot())

# === FILA 4 (OCUPA TODO EL ANCHO) ===
with st.container():
    st.subheader("Fila 4 - Columna Única (100% ancho)")
    st.pyplot(random_plot())

