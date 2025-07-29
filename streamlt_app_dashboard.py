import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    html, body, [data-testid="stApp"] {
        height: 100vh;
        margin: 0;
        padding: 0;
        overflow: hidden;
    }
    .fila {
        display: flex;
        width: 100%;
        margin: 0;
        padding: 0;
    }
    .fila1 { height: 30vh; }
    .fila2 { height: 50vh; }
    .fila3 { height: 20vh; }
    .columna {
        flex: 1;
        padding: 0;
        margin: 0;
    }
    .block-container {
        padding: 0 !important;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)

def random_plot():
    fig, ax = plt.subplots(figsize=(4, 2.5))  # Tamaño compacto
    x = np.linspace(0, 10, 100)
    y = np.sin(x + np.random.rand())
    ax.plot(x, y)
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout(pad=0)  # Eliminar relleno extra
    return fig

# === FILA 1 ===
st.markdown('<div class="fila fila1">', unsafe_allow_html=True)
cols = st.columns(3, gap="small")
for col in cols:
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

# === FILA 2 ===
st.markdown('<div class="fila fila2">', unsafe_allow_html=True)
cols = st.columns(3, gap="small")
for col in cols:
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

# === FILA 3 ===
st.markdown('<div class="fila fila3">', unsafe_allow_html=True)
cols = st.columns(3, gap="small")
for col in cols:
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

