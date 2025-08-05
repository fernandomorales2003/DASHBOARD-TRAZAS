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
    st.header("📡 Potencias Recepción de HUBs")
    hubs = ["HUB 1.1", "HUB 1.2", "HUB 2.1", "HUB 2.2", "HUB 3.1", "HUB 3.2"]
    potencias = np.round(np.random.uniform(-21, -18, size=len(hubs)), 2)
    df_potencias = pd.DataFrame({"HUB": hubs, "Potencia (dBm)": potencias})
    st.dataframe(df_potencias, use_container_width=True)
    
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
with col3:
    import math
    import pydeck as pdk

    # --- Función para calcular distancia entre coordenadas (Haversine)
    def haversine(coord1, coord2):
        R = 6371000
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    # --- Datos de trazas
    trazas = {
        "TR-S-DER-02": {
            "coordenadas": [
                (-35.4708633166351,  -69.57766819274954),
                (-35.47083740176508, -69.57721906428888),
                (-35.46764651517933, -69.57737240456761),
                (-35.46761649309932, -69.5759568599952),
                (-35.46756355662158, -69.57341267990935),
                (-35.47194972736314, -69.57318668647875),
                (-35.47188945240595, -69.57254924372452),
                (-35.47297521564813, -69.5724348810358),
                (-35.47299678040343, -69.57282559280863)
            ],
            "nombres": [
                "DATACENTER", "FOSC 01", "FOSC 02",
                "HUB 1.1", "HUB 1.2", "HUB 2.1",
                "HUB 2.2", "HUB 3.1", "HUB 3.2"
            ],
            "color_base": [0, 200, 255],
            "clientes_hubs": {
                "HUB 1.1": 38,
                "HUB 1.2": 60,
                "HUB 2.1": 50,
                "HUB 2.2": 43,
                "HUB 3.1": 35,
                "HUB 3.2": 55
            }
        }
    }

    st.subheader("🗺️ Mapa con Detección de Corte")
    st.sidebar.title("Configuración del Mapa")
    traza_seleccionada = st.sidebar.selectbox("Seleccioná la traza", list(trazas.keys()))

    datos_traza = trazas[traza_seleccionada]
    coordenadas = datos_traza["coordenadas"]
    nombres = datos_traza["nombres"]
    color_base = datos_traza["color_base"]

    # --- Calcular distancias acumuladas
    distancias = []
    acumulada = 0
    for i in range(len(coordenadas)):
        if i == 0:
            distancias.append(0)
        else:
            d = haversine(coordenadas[i - 1], coordenadas[i])
            acumulada += d
            distancias.append(round(acumulada, 1))

    st.sidebar.markdown("### Corte de fibra")
    corte_activo = st.sidebar.checkbox("Informar corte de fibra")

    distancia_corte = 0
    if corte_activo:
        distancia_total = distancias[-1]
        distancia_corte = st.sidebar.number_input(
            "Distancia de corte (m)", min_value=0.0, max_value=distancia_total,
            value=0.0, step=1.0
        )

    st.markdown(f"**Distancia total del enlace:** {distancias[-1]:.1f} m")

    puntos = [{
        "label": nombres[i],
        "lat": lat,
        "lon": lon,
        "dist": distancias[i],
        "dist_str": f"{distancias[i]} m"
    } for i, (lat, lon) in enumerate(coordenadas)]

    segmentos = []
    marcador_corte = None

    for i in range(len(puntos) - 1):
        d_inicio = puntos[i]["dist"]
        d_fin = puntos[i+1]["dist"]
        color = color_base

        if d_inicio < distancia_corte < d_fin:
            ratio = (distancia_corte - d_inicio) / (d_fin - d_inicio)
            lat_interp = puntos[i]["lat"] + ratio * (puntos[i+1]["lat"] - puntos[i]["lat"])
            lon_interp = puntos[i]["lon"] + ratio * (puntos[i+1]["lon"] - puntos[i]["lon"])

            segmentos.append({
                "coordinates": [[puntos[i]["lon"], puntos[i]["lat"]], [lon_interp, lat_interp]],
                "color": color_base
            })
            segmentos.append({
                "coordinates": [[lon_interp, lat_interp], [puntos[i+1]["lon"], puntos[i+1]["lat"]]],
                "color": [255, 0, 0]
            })

            marcador_corte = {
                "lat": lat_interp,
                "lon": lon_interp,
                "label": "CORTE DETECTADO",
                "dist_str": f"{distancia_corte:.1f} m"
            }

        else:
            if distancia_corte and d_inicio >= distancia_corte:
                color = [255, 0, 0]
            segmentos.append({
                "coordinates": [[puntos[i]["lon"], puntos[i]["lat"]], [puntos[i+1]["lon"], puntos[i+1]["lat"]]],
                "color": color
            })

    df_puntos = pd.DataFrame(puntos)
    df_segmentos = pd.DataFrame(segmentos)
    df_corte = pd.DataFrame([marcador_corte]) if marcador_corte else pd.DataFrame()

    # --- Capas del Mapa
    line_layer = pdk.Layer("LineLayer", data=df_segmentos,
        get_source_position="coordinates[0]", get_target_position="coordinates[1]",
        get_color="color", get_width=4)

    point_layer = pdk.Layer("ScatterplotLayer", data=df_puntos,
        get_position='[lon, lat]', get_color=[255, 0, 0], get_radius=5, pickable=True)

    corte_layer = pdk.Layer("ScatterplotLayer", data=df_corte,
        get_position='[lon, lat]', get_color=[255, 255, 0], get_radius=8,
        pickable=True) if not df_corte.empty else None

    view_state = pdk.ViewState(latitude=coordenadas[0][0], longitude=coordenadas[0][1], zoom=13)

    layers = [line_layer, point_layer]
    if corte_layer:
        layers.append(corte_layer)

    tooltip = {"html": "<b>{label}</b><br/>Distancia: {dist_str}", "style": {"backgroundColor": "white"}}
    st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view_state, tooltip=tooltip))

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
    c1.markdown(f"""
    <div style="text-align:center;">
        <div style="font-weight:bold;">✅ Enlaces OK</div>
        <div style="font-size:12px;">{total_ok} de {total_enlaces}</div>
    </div>
""", unsafe_allow_html=True)

c2.markdown(f"""
    <div style="text-align:center;">
        <div style="font-weight:bold;">🔻 Enlace más degradado</div>
        <div style="font-size:12px;">{enlace_mas_degradado["Enlace"]}</div>
    </div>
""", unsafe_allow_html=True)

c3.markdown(f"""
    <div style="text-align:center;">
        <div style="font-weight:bold;">📉 Variación potencia</div>
        <div style="font-size:12px;">{enlace_mas_degradado['Diferencia']:.2f} dB</div>
    </div>
""", unsafe_allow_html=True)


with col3:
    pass
