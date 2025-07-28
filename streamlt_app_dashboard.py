import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

st.set_page_config(layout="wide")
st.title("📡 Comparador de Curvas OTDR - Enlace MZA-NORTE")

# Parámetros del enlace
distancia = 50.0  # fijo para MZA-NORTE
atenuacion_por_km = 0.21  # para 1550 nm

# Generar eventos patrón cada 4 km
eventos_patron = {round((i+1)*4, 2): 0.15 for i in range(int(distancia // 4))}

# Generar eventos adicionales aleatorios para curva 2025
puntos_disponibles = np.round(np.linspace(1, distancia - 1, int(distancia - 1)), 2)
puntos_nuevos = random.sample(list(set(puntos_disponibles) - set(eventos_patron.keys())), 8)
eventos_extra = {round(p, 2): round(random.uniform(0.15, 0.75), 2) for p in puntos_nuevos}
eventos_2025 = dict(sorted({**eventos_patron, **eventos_extra}.items()))

# Función para generar curva
def generar_curva(at_km, eventos):
    x_ini = np.array([0.0, 0.005, 0.075])
    y_ini = np.array([0.0, 0.8, -0.25])

    x_fibra = np.linspace(0.075, distancia - 0.075, 1000)
    y_fibra = -at_km * x_fibra + y_ini[-1]
    for punto, perdida in eventos.items():
        idx = np.searchsorted(x_fibra, punto)
        y_fibra[idx:] -= perdida

    y_fin_base = y_fibra[-1]
    x_fin = np.array([distancia - 0.075 + 0.005, distancia - 0.075 + 0.010, distancia])
    y_fin = np.array([y_fin_base, y_fin_base + 0.8, y_fin_base - 0.5])

    x_total = np.concatenate([x_ini, x_fibra, x_fin])
    y_total = np.concatenate([y_ini, y_fibra, y_fin])
    return x_total, y_total

# Cálculo de atenuación total
at_total_2024 = round(atenuacion_por_km * distancia + sum(eventos_patron.values()), 2)
at_total_2025 = round(atenuacion_por_km * distancia + sum(eventos_2025.values()), 2)

# Mostrar resumen
st.markdown("### 🧪 Enlace simulado: `MZA-NORTE`")
st.markdown(f"- Atenuación total `MZA-NORTE-2024-06`: **{at_total_2024:.2f} dB**")
st.markdown(f"- Atenuación total `MZA-NORTE-2025-06`: **{at_total_2025:.2f} dB**")

# Gráfico
st.subheader("📈 Curvas OTDR Comparativas")
fig, ax = plt.subplots(figsize=(12, 6))

x_2024, y_2024 = generar_curva(atenuacion_por_km, eventos_patron)
x_2025, y_2025 = generar_curva(atenuacion_por_km, eventos_2025)

ax.plot(x_2024, y_2024, label="MZA-NORTE-2024-06", color="blue")
ax.plot(x_2025, y_2025, label="MZA-NORTE-2025-06", color="green")

# Marcar eventos adicionales 2025
for punto in eventos_extra.keys():
    y_val = -atenuacion_por_km * punto - sum(v for k, v in eventos_2025.items() if k <= punto)
    ax.plot(punto, y_val, 'ro', label='_nolegend_')

ax.set_xlabel("Distancia (km)")
ax.set_ylabel("Potencia (dB)")
ax.set_title("Comparación de Curvas OTDR")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# --- NUEVOS INDICADORES ---

st.subheader("📊 Indicadores del Enlace 2025")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="🔦 Atenuación Total", value=f"{at_total_2025:.2f} dB")

evento_max = max(eventos_2025.items(), key=lambda x: x[1])
with col2:
    st.metric(label="🚨 Mayor Evento", value=f"{evento_max[1]:.2f} dB", help=f"Ocurre en el km {evento_max[0]}")

with col3:
    densidad = len(eventos_2025) / distancia
    st.metric(label="📍 Densidad de Eventos", value=f"{densidad:.2f} eventos/km")

# Checkbox para seleccionar tabla
st.subheader("📋 Mostrar tabla de eventos")
col1, col2 = st.columns(2)
with col1:
    tabla_2024 = st.checkbox("Ver eventos 2024", value=False)
with col2:
    tabla_2025 = st.checkbox("Ver eventos 2025", value=False)

# Mostrar tabla correspondiente
if tabla_2024 and tabla_2025:
    st.warning("Selecciona solo una tabla a la vez.")
elif tabla_2024:
    acumulado = 0
    tabla = []
    for i, (dist, att) in enumerate(sorted(eventos_patron.items()), start=1):
        acumulado += att
        total = atenuacion_por_km * dist + acumulado
        tabla.append({
            "Nro Evento": i,
            "Distancia (km)": dist,
            "Pérdida (dB)": att,
            "Atenuación acumulada (dB)": round(total, 2)
        })
    tabla.append({
        "Nro Evento": "—",
        "Distancia (km)": distancia,
        "Pérdida (dB)": 0.0,
        "Atenuación acumulada (dB)": at_total_2024
    })
    df_tabla = pd.DataFrame(tabla)
    st.dataframe(df_tabla.style.format({
        "Distancia (km)": "{:.2f}",
        "Pérdida (dB)": "{:.2f}",
        "Atenuación acumulada (dB)": "{:.2f}"
    }), use_container_width=True)

elif tabla_2025:
    acumulado = 0
    tabla = []
    for i, (dist, att) in enumerate(sorted(eventos_2025.items()), start=1):
        acumulado += att
        total = atenuacion_por_km * dist + acumulado
        tabla.append({
            "Nro Evento": i,
            "Distancia (km)": dist,
            "Pérdida (dB)": att,
            "Atenuación acumulada (dB)": round(total, 2)
        })
    tabla.append({
        "Nro Evento": "—",
        "Distancia (km)": distancia,
        "Pérdida (dB)": 0.0,
        "Atenuación acumulada (dB)": at_total_2025
    })
    df_tabla = pd.DataFrame(tabla)
    st.dataframe(df_tabla.style.format({
        "Distancia (km)": "{:.2f}",
        "Pérdida (dB)": "{:.2f}",
        "Atenuación acumulada (dB)": "{:.2f}"
    }), use_container_width=True)

