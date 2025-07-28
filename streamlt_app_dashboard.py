import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Datos simulados de ejemplo
distancia_km = np.linspace(0, 50, 500)
atenuacion_2024 = -0.22 * distancia_km + np.random.normal(0, 0.05, 500)
atenuacion_2025 = -0.22 * distancia_km + np.random.normal(0, 0.05, 500)
atenuacion_2025[300] -= 0.5  # Evento significativo

# Título principal
st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center;'>📡 Dashboard de Medición OTDR</h1>", unsafe_allow_html=True)

# Fila superior (30% de altura) con 3 columnas
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown("### 🔌 TRONCAL MZA-NORTE")

    # Checkboxes
    mostrar_2024 = st.checkbox("Mostrar curva 2024/06", value=True)
    mostrar_2025 = st.checkbox("Mostrar curva 2025/06", value=True)

    # Gráfico de comparación
    fig, ax = plt.subplots(figsize=(6, 3))
    if mostrar_2024:
        ax.plot(distancia_km, atenuacion_2024, label="TRONCAL MZA-NORTE-2024/06", color='blue')
    if mostrar_2025:
        ax.plot(distancia_km, atenuacion_2025, label="TRONCAL MZA-NORTE-2025/06", color='red')

        # Marcar eventos > 0.30 dB
        diffs = np.abs(np.diff(atenuacion_2025))
        indices_eventos = np.where(diffs > 0.3)[0]
        for i in indices_eventos:
            ax.plot(distancia_km[i], atenuacion_2025[i], 'o', color='black', label='Evento > 0.30 dB' if i == indices_eventos[0] else "")

    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Atenuación (dB)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

# Columnas 2 y 3 vacías (se pueden usar después)
with col2:
    st.markdown("")

with col3:
    st.markdown("")
