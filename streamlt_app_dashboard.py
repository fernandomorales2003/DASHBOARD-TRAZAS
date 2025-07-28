import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")
st.title("📡 Simulación OTDR - MENDOZANORTE 2024 vs 2025")

# --- CURVA 2024 ---
st.header("🔹 Curva OTDR: MENDOZANORTE-2024-06")

DISTANCIA_TOTAL = 40.0
PUNTOS_EVENTO_2024 = [i for i in range(4, int(DISTANCIA_TOTAL)+1, 4)]
ATENUACION_EVENTO_2024 = 0.15

# Construcción de la curva
x_2024 = [0.0]
y_2024 = [0.0]
at_2024 = 0.21

atenuacion_acumulada_2024 = 0

for punto in np.linspace(0, DISTANCIA_TOTAL, 1000):
    if any(abs(punto - e) < 0.02 for e in PUNTOS_EVENTO_2024):
        atenuacion_acumulada_2024 += ATENUACION_EVENTO_2024
    y_2024.append(-at_2024 * punto - atenuacion_acumulada_2024)
    x_2024.append(punto)

fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(x_2024, y_2024, label="MENDOZANORTE-2024-06", color="blue")
ax1.set_xlabel("Distancia (km)")
ax1.set_ylabel("Potencia (dB)")
ax1.set_title("Curva OTDR - 2024")
ax1.grid(True)
ax1.legend()
st.pyplot(fig1)

# Tabla de eventos 2024
df_eventos_2024 = pd.DataFrame({
    "Distancia (km)": PUNTOS_EVENTO_2024,
    "Atenuación (dB)": [ATENUACION_EVENTO_2024]*len(PUNTOS_EVENTO_2024)
})
at_total_2024 = round(sum(df_eventos_2024["Atenuación (dB)"]), 2)

st.dataframe(df_eventos_2024)
st.markdown(f"**Atenuación total 2024:** `{at_total_2024} dB`")

# --- CURVA 2025 ---
st.header("🔹 Curva OTDR: MENDOZANORTE-2025-07")

np.random.seed(42)
eventos_adicionales = np.sort(np.random.uniform(0, DISTANCIA_TOTAL, 8))
atenuaciones_adicionales = np.round(np.random.uniform(0.10, 0.75, 8), 2)

# Base: eventos 2024 + nuevos
todos_los_eventos_2025 = list(PUNTOS_EVENTO_2024) + list(eventos_adicionales)
atenuaciones_2025 = [ATENUACION_EVENTO_2024]*len(PUNTOS_EVENTO_2024) + list(atenuaciones_adicionales)

# Construcción curva 2025
x_2025 = [0.0]
y_2025 = [0.0]
atenuacion_acumulada_2025 = 0

for punto in np.linspace(0, DISTANCIA_TOTAL, 1000):
    for e, a in zip(todos_los_eventos_2025, atenuaciones_2025):
        if abs(punto - e) < 0.02:
            atenuacion_acumulada_2025 += a
    y_2025.append(-at_2024 * punto - atenuacion_acumulada_2025)
    x_2025.append(punto)

fig2, ax2 = plt.subplots(figsize=(10, 4))
ax2.plot(x_2025, y_2025, label="MENDOZANORTE-2025-07", color="green")
ax2.set_xlabel("Distancia (km)")
ax2.set_ylabel("Potencia (dB)")
ax2.set_title("Curva OTDR - 2025")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)

# Tabla de eventos 2025
df_eventos_2025 = pd.DataFrame({
    "Distancia (km)": np.round(todos_los_eventos_2025, 2),
    "Atenuación (dB)": np.round(atenuaciones_2025, 2)
})
at_total_2025 = round(sum(df_eventos_2025["Atenuación (dB)"]), 2)

st.dataframe(df_eventos_2025)
st.markdown(f"**Atenuación total 2025:** `{at_total_2025} dB`")

