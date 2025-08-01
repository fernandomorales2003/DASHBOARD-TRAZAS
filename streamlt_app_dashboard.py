import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

st.set_page_config(layout="wide", page_title="DASHBOARD OTDR")

# Título centrado reemplaza st.title
st.markdown("<h1 style='text-align:center'>DASHBOARD OTDR</h1>", unsafe_allow_html=True)

# Parámetros del enlace
distancia = 50.0
atenuacion_por_km = 0.21

# Generar eventos patrón cada 4 km
eventos_patron = {round((i+1)*4, 2): 0.15 for i in range(int(distancia // 4))}

# Eventos adicionales aleatorios
puntos_disponibles = np.round(np.linspace(1, distancia - 1, int(distancia - 1)), 2)
puntos_nuevos = random.sample(list(set(puntos_disponibles) - set(eventos_patron.keys())), 8)
eventos_extra = {round(p, 2): round(random.uniform(0.15, 0.75), 2) for p in puntos_nuevos}
eventos_2025 = dict(sorted({**eventos_patron, **eventos_extra}.items()))

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

at_total_2024 = round(atenuacion_por_km * distancia + sum(eventos_patron.values()), 2)
at_total_2025 = round(atenuacion_por_km * distancia + sum(eventos_2025.values()), 2)
porc_aumento = ((at_total_2025 - at_total_2024) / at_total_2024) * 100

# FILA 1
col1, col2, col3 = st.columns(3, border=True)
with col1:
    # Agrupamos todo el contenido en un div centrado
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)

    st.subheader("📊 ENLACE MZA-NORTE")

    st.metric(
        label="🔦 Atenuación Total", 
        value=f"{at_total_2025:.2f} dB (+{porc_aumento:.1f}%)"
    )
    
    # Calcular nivel para el vúmetro, acotando entre 0 y 100
    nivel_vumetro = max(0, min(100, int(porc_aumento)))

    # Código HTML del vúmetro, con nivel dinámico y línea en color #59ebf8
    html_code = f"""
    <div style="display: flex; justify-content: center; margin-top: 10px;">
      <svg width="300" height="160" viewBox="0 0 300 160">
        <defs>
          <linearGradient id="fuelGradient" x1="0%" y1="100%" x2="100%" y2="0%">
            <stop offset="0%"   style="stop-color:#d4f7ec;stop-opacity:1" />
            <stop offset="20%"  style="stop-color:#80e9c5;stop-opacity:1" />
            <stop offset="40%"  style="stop-color:#33d49d;stop-opacity:1" />
            <stop offset="60%"  style="stop-color:#00cc83;stop-opacity:1" />
            <stop offset="80%"  style="stop-color:#009b6e;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#00805c;stop-opacity:1" />
          </linearGradient>
        </defs>

        <path d="M50 150 A100 100 0 0 1 250 150"
              fill="none"
              stroke="url(#fuelGradient)"
              stroke-width="20" />

        <g transform="rotate({-90 + int(nivel_vumetro * 180 / 100)},150,150)">
          <line x1="150" y1="150" x2="150" y2="70" stroke="#59ebf8" stroke-width="2" />
        </g>

        <circle cx="150" cy="150" r="4" fill="#000" />
      </svg>
    </div>
    """
    st.components.v1.html(html_code, height=200)

    evento_max = max(eventos_2025.items(), key=lambda x: x[1])
    st.metric(
        label="🚨 Mayor Evento",
        value=f"{evento_max[1]:.2f} dB",
        help=f"Ocurre en el km {evento_max[0]:.2f}"
    )
    eventos_adicionales = len(eventos_2025) - len(eventos_patron)
    st.metric(
        label="🛠️ Cantidad de Eventos Mantenimiento",
        value=f"{eventos_adicionales}"
    )
    st.markdown(f"**Atenuación Total 2024:** {at_total_2024:.2f} dB")
    st.markdown(f"**Atenuación Total 2025:** {at_total_2025:.2f} dB")

    st.markdown("</div>", unsafe_allow_html=True)

# FILA 2
col1, _, _ = st.columns(3, border=True)
with col1:
    st.subheader("📈 Curvas OTDR Comparativas")
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    x_2024, y_2024 = generar_curva(atenuacion_por_km, eventos_patron)
    x_2025, y_2025 = generar_curva(atenuacion_por_km, eventos_2025)
    ax.plot(x_2024, y_2024, label="MZA-NORTE-2024-06")
    ax.plot(x_2025, y_2025, label="MZA-NORTE-2025-06")
    for punto in eventos_extra.keys():
        y_val = -atenuacion_por_km * punto - sum(v for k, v in eventos_2025.items() if k <= punto)
        ax.plot(punto, y_val, 'ro')
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Potencia (dB)")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend()
    st.pyplot(fig)

# FILA 3
col1, _, _ = st.columns(3, border=True)
with col1:
    st.subheader("📋 Mostrar tabla de eventos")
    col_check1, col_check2 = st.columns(2)
    with col_check1:
        tabla_2024 = st.checkbox("Ver eventos 2024", value=False)
    with col_check2:
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

