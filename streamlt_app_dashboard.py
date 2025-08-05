import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="DASHBOARD OTDR")

# Título centrado
st.markdown("<h1 style='text-align:center'>DASHBOARD OTDR</h1>", unsafe_allow_html=True)

# Parámetros del enlace
distancia = 50.0
atenuacion_por_km = 0.21

# Eventos patrón
eventos_patron = {round((i+1)*4, 2): 0.15 for i in range(int(distancia // 4))}
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

# ---------- FILA 1 ----------
col1, col2, col3 = st.columns(3, border=True)

with col1:
    st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
    st.subheader("📊 ENLACE MZA-NORTE")
    st.metric("🔦 Atenuación Total", f"{at_total_2025:.2f} dB (+{porc_aumento:.1f}%)")
    nivel_vumetro = max(0, min(100, int(porc_aumento)))
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
        <path d="M50 150 A100 100 0 0 1 250 150" fill="none" stroke="url(#fuelGradient)" stroke-width="20" />
        <g transform="rotate({-90 + int(nivel_vumetro * 180 / 100)},150,150)">
          <line x1="150" y1="150" x2="150" y2="70" stroke="#59ebf8" stroke-width="2" />
        </g>
        <circle cx="150" cy="150" r="4" fill="#000" />
      </svg>
    </div>
    """
    st.components.v1.html(html_code, height=200)

    evento_max = max(eventos_2025.items(), key=lambda x: x[1])
    st.metric("🚨 Mayor Evento", f"{evento_max[1]:.2f} dB", help=f"Ocurre en el km {evento_max[0]:.2f}")
    eventos_adicionales = len(eventos_2025) - len(eventos_patron)
    st.metric("🛠️ Cantidad de Eventos Mantenimiento", f"{eventos_adicionales}")
    st.markdown(f"**Atenuación Total 2024:** {at_total_2024:.2f} dB")
    st.markdown(f"**Atenuación Total 2025:** {at_total_2025:.2f} dB")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.subheader("📌 Estado de Enlaces (KPI)")
    enlaces_info = {
        "MZA-FTTH-01": {"Tx": 0, "Rx_cert": -20},
        "MZA-FTTH-02": {"Tx": 5, "Rx_cert": -20},
        "MZA-CCTV-01": {"Tx": 0, "Rx_cert": -14},
        "MZA-WS-01": {"Tx": 3, "Rx_cert": -14},
        "MZA-WS-02": {"Tx": 3, "Rx_cert": -12},
        "MZA-WS-03": {"Tx": 3, "Rx_cert": -8},
    }

    def calcular_atenuaciones(tx, rx_cert):
        at_cert = tx - rx_cert
        variacion = random.uniform(-3, 3)
        at_actual = at_cert + variacion
        return round(at_cert, 2), round(at_actual, 2)

    def evaluar_estado(at_cert, at_actual):
        diferencia = at_actual - at_cert
        if diferencia <= 0.5:
            return "OK"
        elif diferencia <= 2:
            return "ADVERTENCIA"
        else:
            return "CRÍTICO"

    def estado_icono_color(estado):
        if estado == "OK":
            return "✅", "#2ecc71"
        elif estado == "ADVERTENCIA":
            return "⚠️", "#f1c40f"
        else:
            return "❌", "#e74c3c"

    datos = []
    for enlace, valores in enlaces_info.items():
        tx = valores["Tx"]
        rx = valores["Rx_cert"]
        at_cert, at_actual = calcular_atenuaciones(tx, rx)
        estado = evaluar_estado(at_cert, at_actual)
        datos.append({
            "Enlace": enlace,
            "Tx": tx,
            "Rx_cert": rx,
            "Atenuación Certificada": at_cert,
            "Atenuación Actual": at_actual,
            "Estado": estado
        })

    df = pd.DataFrame(datos)

    for row in df.itertuples():
        icono, color = estado_icono_color(row.Estado)
        st.markdown(f"""
            <div style="background-color:{color};
                        padding:2px 20px;
                        border-radius:10px;
                        text-align:center;
                        color:white;
                        margin-bottom:12px;
                        width:100%;
                        height:auto;">
                <h5 style="margin: 4px 0;">{icono} {row.Enlace} – <span style="font-weight:normal;">{row.Estado}</span></h5>
            </div>
        """, unsafe_allow_html=True)

with col3:
    st.header("📡 Potencias Simuladas de HUBs")

    hubs = ["HUB 1.1", "HUB 1.2", "HUB 2.1", "HUB 2.2", "HUB 3.1", "HUB 3.2"]
    potencias = np.round(np.random.uniform(-21, -18, size=len(hubs)), 2)
    df_potencias = pd.DataFrame({"HUB": hubs, "Potencia (dBm)": potencias})
    st.dataframe(df_potencias, use_container_width=True)
