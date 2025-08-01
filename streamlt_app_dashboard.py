import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Recorridos de Fibra", layout="wide")

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

# --- Datos de las trazas
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
    },
    "TR1-SUR": {
        "coordenadas": [
            (-35.470812, -69.577695), (-35.470874, -69.577691), (-35.470914, -69.578495),
            (-35.473146, -69.578359), (-35.474385, -69.578319), (-35.474353, -69.577005),
            (-35.476546, -69.576911), (-35.476760, -69.585089), (-35.497015, -69.585443),
            (-35.497223, -69.581949), (-35.501802, -69.582158), (-35.501746, -69.582981)
        ],
        "nombres": [
            "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03", "FOSC 04", "FOSC 05",
            "FOSC 06", "FOSC 07", "FOSC 08", "FOSC 09", "FOSC 10", "TORRE WISP"
        ],
        "color_base": [0, 200, 255]
    }
}

# --- Sidebar
st.sidebar.title("Configuración del Mapa")
traza_seleccionada = st.sidebar.selectbox("Seleccioná la traza", list(trazas.keys()))

# --- Cargar datos
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

# --- Sidebar - Corte de fibra
st.sidebar.markdown("### Corte de fibra")
corte_activo = st.sidebar.checkbox("Informar corte de fibra")

distancia_corte = 0
if corte_activo:
    distancia_total = distancias[-1]
    distancia_corte = st.sidebar.number_input(
        "Distancia de corte (m)", min_value=0.0, max_value=distancia_total,
        value=0.0, step=1.0
    )

# --- Mostrar distancia total
st.markdown(f"### Distancia total del enlace: `{distancias[-1]:.1f} m`")

# --- Armar puntos
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": distancias[i],
    "dist_str": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

# --- Segmentos y lógica de corte
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
            "coordinates": [
                [puntos[i]["lon"], puntos[i]["lat"]],
                [lon_interp, lat_interp]
            ],
            "color": color_base
        })
        segmentos.append({
            "coordinates": [
                [lon_interp, lat_interp],
                [puntos[i+1]["lon"], puntos[i+1]["lat"]]
            ],
            "color": [255, 0, 0]
        })

        marcador_corte = {
            "lat": lat_interp,
            "lon": lon_interp,
            "label": "CORTE DETECTADO A POSICIÓN GPS"
        }

    else:
        if distancia_corte and d_inicio >= distancia_corte:
            color = [255, 0, 0]
        segmentos.append({
            "coordinates": [
                [puntos[i]["lon"], puntos[i]["lat"]],
                [puntos[i+1]["lon"], puntos[i+1]["lat"]]
            ],
            "color": color
        })

# --- DataFrames para Pydeck
df_puntos = pd.DataFrame(puntos)
df_segmentos = pd.DataFrame(segmentos)
df_corte = pd.DataFrame([marcador_corte]) if marcador_corte else pd.DataFrame()

# --- Capas del Mapa
line_layer = pdk.Layer(
    "LineLayer",
    data=df_segmentos,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color="color",
    get_width=4,
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=5,
    pickable=True,
)

corte_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_corte,
    get_position='[lon, lat]',
    get_color=[255, 255, 0],
    get_radius=8,
    pickable=True
) if not df_corte.empty else None

# --- Mapa y vista
view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=13,
    pitch=0,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist_str}",
    "style": {"backgroundColor": "white"}
}

layers = [line_layer, point_layer]
if corte_layer:
    layers.append(corte_layer)

st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip=tooltip
))

# --- Radar Chart (sólo para TR-S-DER-02)
if traza_seleccionada == "TR-S-DER-02":
    clientes_por_hub = trazas["TR-S-DER-02"]["clientes_hubs"]
    categorias = list(clientes_por_hub.keys())
    valores = list(clientes_por_hub.values())
    categorias.append(categorias[0])
    valores.append(valores[0])

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        name='Clientes por HUB',
        line_color='deepskyblue'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        showlegend=False,
        title="Distribución de Clientes por HUB"
    )

    st.plotly_chart(fig, use_container_width=True)

    # --- Indicadores de clientes afectados por corte
    if corte_activo and distancia_corte > 0:
        total_afectados = 0
        total_operativos = 0
        for i, nombre in enumerate(nombres):
            if nombre.startswith("HUB") and i < len(distancias):
                if distancias[i] > distancia_corte:
                    total_afectados += clientes_por_hub.get(nombre, 0)
                else:
                    total_operativos += clientes_por_hub.get(nombre, 0)

        st.markdown("### Estado de clientes según el corte")
        col1, col2 = st.columns(2)
        col1.metric("Clientes operativos", total_operativos)
        col2.metric("Clientes sin servicio", total_afectados)
