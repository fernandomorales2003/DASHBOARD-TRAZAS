import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Simulador de Curvas OTDR - MENDOZANORTE")

# Parámetros generales
distancia_total = 40  # km
atenuacion_fusion_2024 = 0.15  # dB
atenuacion_por_km = 0.21  # dB/km
n_eventos_2024 = distancia_total // 4

# Curva base 2024
x_2024 = [0]
y_2024 = [0]
eventos_2024 = [(0, 0)]
for i in range(1, int(n_eventos_2024)+1):
    x_2024.append(i * 4)
    perdida_total = y_2024[-1] + atenuacion_fusion_2024
    y_2024.append(perdida_total)
    eventos_2024.append((i * 4, atenuacion_fusion_2024))

# Atenuación por distancia
atenuacion_distancia = distancia_total * atenuacion_por_km
atenuacion_total_2024 = y_2024[-1] + atenuacion_distancia

# Mostrar curva 2024
st.subheader("🔹 Curva OTDR - MENDOZANORTE-2024-06")
fig, ax = plt.subplots()
ax.plot(x_2024, y_2024, label="MENDOZANORTE-2024-06", color='blue', marker='o')
ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Pérdida (dB)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# Tabla de eventos 2024
df_2024 = pd.DataFrame(eventos_2024, columns=["Distancia (km)", "Pérdida en evento (dB)"])
df_2024.loc[len(df_2024)] = ["TOTAL", f"{atenuacion_total_2024:.2f} dB"]
st.dataframe(df_2024)

# Curva modificada 2025
np.random.seed(42)  # Para reproducibilidad
x_2025 = x_2024.copy()
y_2025 = y_2024.copy()
eventos_2025 = eventos_2024.copy()

# Generar 8 eventos aleatorios
eventos_extra = 8
posiciones_random = sorted(np.random.uniform(1, distancia_total - 1, eventos_extra))
atenuaciones_random = np.random.uniform(0.10, 0.75, eventos_extra)

for pos, att in zip(posiciones_random, atenuaciones_random):
    # Insertar el evento manteniendo el orden
    insert_idx = np.searchsorted(x_2025, pos)
    x_2025.insert(insert_idx, pos)
    y_prev = y_2025[insert_idx - 1] if insert_idx > 0 else 0
    y_2025.insert(insert_idx, y_prev + att)
    eventos_2025.insert(insert_idx, (round(pos, 2), round(att, 2)))

# Ajustar los siguientes valores en y_2025
for i in range(insert_idx + 1, len(y_2025)):
    y_2025[i] += att

atenuacion_total_2025 = y_2025[-1] + atenuacion_distancia

# Mostrar curva 2025
st.subheader("🔸 Curva OTDR - MENDOZANORTE-2025-07")
fig2, ax2 = plt.subplots()
ax2.plot(x_2025, y_2025, label="MENDOZANORTE-2025-07", color='orange', marker='o')
ax2.set_xlabel("Distancia (km)")
ax2.set_ylabel("Pérdida (dB)")
ax2.grid(True)
ax2.legend()
st.pyplot(fig2)

# Tabla de eventos 2025
df_2025 = pd.DataFrame(eventos_2025, columns=["Distancia (km)", "Pérdida en evento (dB)"])
df_2025.loc[len(df_2025)] = ["TOTAL", f"{atenuacion_total_2025:.2f} dB"]
st.dataframe(df_2025)

# Nota
st.markdown(f"📌 Se considera una atenuación por distancia de **{atenuacion_por_km} dB/km** para ambos casos (longitud de onda 1550 nm).")


