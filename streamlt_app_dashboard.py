import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    .fila {
        display: flex;
        width: 100%;
        margin-bottom: 20px;
    }
    .fila1 { height: 30vh; }
    .fila2 { height: 50vh; }
    .fila3 { height: 20vh; }
    .fila4 { height: auto; }
    .columna {
        flex: 1;
        padding: 10px;
    }
    .grafico {
        height: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def random_plot():
    fig, ax = plt.subplots()
    x = np.linspace(0, 10, 100)
    y = np.sin(x + np.random.rand())
    ax.plot(x, y)
    return fig

# === FILA 1 (30% ALTO) ===
st.markdown('<div class="fila fila1">', unsafe_allow_html=True)
cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

# === FILA 2 (50% ALTO) ===
st.markdown('<div class="fila fila2">', unsafe_allow_html=True)
cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

# === FILA 3 (20% ALTO) ===
st.markdown('<div class="fila fila3">', unsafe_allow_html=True)
cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        st.pyplot(random_plot())
st.markdown('</div>', unsafe_allow_html=True)

# === FILA 4 (100% ancho) ===
st.markdown("### Fila 4 - Columna única (gráfico grande)")
st.pyplot(random_plot())


