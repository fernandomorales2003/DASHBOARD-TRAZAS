import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ---------- ESTILO PERSONALIZADO ----------
st.markdown("""
    <style>
        body {
            background-color: #0f256e;
            color: #f0f0f0;
        }
        .stApp {
            background-color: #0f256e;
        }
        .css-1d391kg {  /* Títulos grandes */
            color: #ffffff;
        }
        .css-10trblm, .css-1v3fvcr {  /* Subtítulos y texto normal */
            color: #f0f0f0;
        }
        .css-1x8cf1d {  /* Caja de sliders y selects */
            background-color: #1e3c8a;
            border-radius: 10px;
        }
        .stSlider > div > div {
            background-color: #1e3c8a;
        }
        .stCheckbox > label {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- CONFIGURACIÓN DE PÁGINA ----------
st.set_page_config(layout="wide")
st.title("📡 Simulador de Medición OTDR - Fibra Óptica")

# ---------- PARÁMETROS ----------
distancia = st.slider("📏 Distancia del tramo (km)", 1.0, 80.0, 50.0, step=1.0)

# ---------- GENERACIÓN DE CURVAS OTDR ----------
x = np.linspace(0, distancia, 1000)
curva_2024 = -0.21 * x  # atenuación 0.21 dB/km
ruido_2024 = np.random.normal(0, 0.02, len(x))
curva_2024 += ruido_2024

curva_2025 = curva_2024.copy()
eventos_adicionales = 8
posiciones = np.random.choice(len(x), eventos_adicionales, replace=False)
curva_2025[posiciones] -= np.random.uniform(0.1, 0.5, eventos_adicionales)

# ---------- VISUALIZACIÓN DE CURVAS ----------
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(x, curva_2024, label="Curva OTDR - 2024", color="cyan")
ax.plot(x, curva_2025, label="Curva OTDR - 2025", color="yellow")
ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_facecolor("#0f256e")
fig.patch.set_facecolor('#0f256e')
ax.legend()
ax.grid(True, color='#444444')

st.pyplot(fig)

# ---------- CHECKBOX PARA MOSTRAR TABLAS ----------
col1, col2 = st.columns(2)

with col1:
    if st.checkbox("📋 Mostrar eventos 2024"):
        eventos_2024 = pd.DataFrame({
            "Tipo": ["Empalme", "Conector", "Empalme"],
            "Distancia (km)": [5, 20, 35],
            "Pérdida (dB)": [0.1, 0.3, 0.15]
        })
        eventos_2024["Acumulado (dB)"] = eventos_2024["Pérdida (dB)"].cumsum()
        st.write("### Tabla de Eventos 2024")
        st.dataframe(eventos_2024)

with col2:
    if st.checkbox("📋 Mostrar eventos 2025"):
        eventos_2025 = pd.DataFrame({
            "Tipo": ["Empalme", "Conector", "Empalme", "Empalme", "Conector", "Empalme", "Empalme", "Empalme", "Conector", "Empalme", "Empalme"],
            "Distancia (km)": sorted(np.random.choice(np.arange(1, distancia), 11, replace=False)),
            "Pérdida (dB)": np.round(np.random.uniform(0.1, 0.5, 11), 2)
        })
        eventos_2025["Acumulado (dB)"] = eventos_2025["Pérdida (dB)"].cumsum()
        st.write("### Tabla de Eventos 2025")
        st.dataframe(eventos_2025)

# ---------- ANÁLISIS DEL ENLACE ----------
st.subheader("📊 ANÁLISIS ENLACE MZA-NORTE")

atenuacion_total_2024 = 0.21 * distancia + eventos_2024["Pérdida (dB)"].sum()
atenuacion_total_2025 = 0.21 * distancia + eventos_2025["Pérdida (dB)"].sum()
porcentaje_aumento = (atenuacion_total_2025 - atenuacion_total_2024) / atenuacion_total_2024 * 100
eventos_mantenimiento = len(eventos_2025) - len(eventos_2024)

col1, col2, col3 = st.columns(3)
col1.metric("📉 Atenuación Total 2024", f"{atenuacion_total_2024:.2f} dB")
col2.metric("📈 Atenuación Total 2025", f"{atenuacion_total_2025:.2f} dB", f"{porcentaje_aumento:.1f}%")
col3.metric("🔧 Cant. de Eventos Mantenimiento", f"{eventos_mantenimiento}")

# ---------- VALORES DE ATENUACIÓN TOTAL ----------
st.write("#### 📌 Valores Finales de Atenuación Total:")
st.markdown(f"- ✅ **Atenuación Total 2024:** {atenuacion_total_2024:.2f} dB")
st.markdown(f"- ✅ **Atenuación Total 2025:** {atenuacion_total_2025:.2f} dB")

