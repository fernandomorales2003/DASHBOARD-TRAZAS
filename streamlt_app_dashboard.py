import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

st.set_page_config(layout="wide", page_title="Comparador Curvas OTDR")
st.title("📡 Comparador de Curvas OTDR - Enlace MZA-NORTE")

# Estilos visuales generales
st.markdown("""
<style>
.container-box {
    border: 2px solid #204ecf;
    border-radius: 10px;
    padding: 1.5em;
    margin-bottom: 2em;
    background-color: #f9f9f9;
}
.transparent-bg {
    background-color: rgba(0,0,0,0) !important;
}
</style>
""", unsafe_allow_html=True)

# Parámetros del enlace
distancia = 50.0
atenuacion_por_km = 0.21

# Generar eventos
eventos_patron = {round((i+1)*4, 2): 0.15 for i in range(int(distancia // 4))}
puntos_disponibles = np.round(np.linspace(1, distancia - 1, int(distancia - 1)), 2)
puntos_nuevos = random.sample(list(set(puntos_disponibles) - set(eventos_patron.keys())), 8)
eventos_extra = {round(p, 2): round(random.uniform(0.15, 0.75), 2) for p in puntos_nuevos}
eventos_2025 = dict(sorted({**eventos_patron, **eventos_extra}.items()))

# Función curva
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
    return np.concatenate([x_ini, x_fibra, x_fin]), np.concatenate([y_ini, y_fibra, y_fin])

# Atenuaciones
at_total_2024 = round(atenuacion_por_km * distancia + sum(eventos_patron.values()), 2)
at_total_2025 = round(atenuacion_por_km * distancia + sum(eventos_2025.values()), 2)

# ==================== FILA 1 - INDICADORES ====================
with st.container():
    st.markdown('<div class="container-box">', unsafe_allow_html=True)
    st.subheader("📊 INDICADORES ENLACE MZA-NORTE")

    col1, col2, col3 = st.columns(3)
    porc_aumento = ((at_total_2025 - at_total_2024) / at_total_2024) * 100

    with col1:
        st.metric("🔦 Atenuación Total", f"{at_total_2025:.2f} dB (+{porc_aumento:.1f}%)")

    evento_max = max(eventos_2025.items(), key=lambda x: x[1])
    evento_max_dist = evento_max[0]
    evento_max_val = evento_max[1]

    with col2:
        st.metric("🚨 Mayor Evento", f"{evento_max_val:.2f} dB", help=f"Ocurre en el km {evento_max_dist:.2f}")

    eventos_adicionales = len(eventos_2025) - len(eventos_patron)
    with col3:
        st.metric("🛠️ Eventos Mantenimiento", f"{eventos_adicionales}")

    # Segunda fila: comparación de atenuaciones
    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"**Atenuación Total 2024:** {at_total_2024:.2f} dB")
    with col_b:
        st.markdown(f"**Atenuación Total 2025:** {at_total_2025:.2f} dB")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FILA 2 - CURVAS OTDR ====================
with st.container():
    st.markdown('<div class="container-box">', unsafe_allow_html=True)
    st.subheader("📈 CURVAS OTDR COMPARATIVAS")

    fig, ax = plt.subplots(figsize=(8.4, 4.2), facecolor='none')

    x_2024, y_2024 = generar_curva(atenuacion_por_km, eventos_patron)
    x_2025, y_2025 = generar_curva(atenuacion_por_km, eventos_2025)

    ax.plot(x_2024, y_2024, label="MZA-NORTE-2024-06", color="#00cc83", linewidth=2)
    ax.plot(x_2025, y_2025, label="MZA-NORTE-2025-06", color="#ffffff", linewidth=2)

    for punto in eventos_extra.keys():
        y_val = -atenuacion_por_km * punto - sum(v for k, v in eventos_2025.items() if k <= punto)
        ax.plot(punto, y_val, 'ro')

    ax.set_facecolor("none")
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Potencia (dB)")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend(facecolor='none')
    st.pyplot(fig)
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== FILA 3 - OPEX ====================
with st.container():
    st.markdown('<div class="container-box">', unsafe_allow_html=True)
    st.subheader("💰 COSTO OPERATIVO (OPEX)")
    costo_opex = random.randint(300, 1000)
    st.markdown(f"### Estimación de OPEX anual: **${costo_opex} USD**")
    st.markdown('</div>', unsafe_allow_html=True)

# ==================== TABLAS OPCIONALES ====================
st.subheader("📋 Mostrar tabla de eventos")
col1, col2 = st.columns(2)
with col1:
    tabla_2024 = st.checkbox("Ver eventos 2024", value=False)
with col2:
    tabla_2025 = st.checkbox("Ver eventos 2025", value=False)

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
    st.dataframe(pd.DataFrame(tabla), use_container_width=True)
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
    st.dataframe(pd.DataFrame(tabla), use_container_width=True)
