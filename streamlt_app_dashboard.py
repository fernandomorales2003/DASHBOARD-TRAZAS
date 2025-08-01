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
    pass


# ---------- FILA 2 ----------
col1, col2, col3 = st.columns(3, border=True)

with col1:
    st.subheader("📈 Curvas OTDR Comparativas")
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    x_2024, y_202_4 = generar_curva(atenuacion_por_km, eventos_patron)
    x_2025, y_2025 = generar_curva(atenuacion_por_km, eventos_2025)
    ax.plot(x_2024, y_202_4, label="MZA-NORTE-2024-06")
    ax.plot(x_2025, y_2025, label="MZA-NORTE-2025-06")
    for punto in eventos_extra.keys():
        y_val = -atenuacion_por_km * punto - sum(v for k, v in eventos_2025.items() if k <= punto)
        ax.plot(punto, y_val, 'ro')
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Potencia (dB)")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend()
    st.pyplot(fig)

with col2:
    st.subheader("📊 AT Certificada vs Actual")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Certificada"], name="Certificada", marker_color="#00cc83"))
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Actual"], name="Actual", marker_color="#16865e"))
    fig.update_layout(barmode="group", yaxis_title="Atenuación (dB)", height=400)
    st.plotly_chart(fig, use_container_width=True)

with col3:
    pass


# ---------- FILA 3 ----------
col1, col2, col3 = st.columns(3, border=True)

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

with col2:
    st.subheader("📈 Indicadores")
    total_ok = df[df["Estado"] == "OK"].shape[0]
    total_enlaces = df.shape[0]
    df["Diferencia"] = df["Atenuación Actual"] - df["Atenuación Certificada"]
    enlace_mas_degradado = df.loc[df["Diferencia"].idxmax()]
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Enlaces OK", f"{total_ok} de {total_enlaces}")
    c2.metric("🔻 Enlace más degradado", enlace_mas_degradado["Enlace"])
    c3.metric("📉 Variación potencia", f"{enlace_mas_degradado['Diferencia']:.2f} dB")

with col3:
    pass
