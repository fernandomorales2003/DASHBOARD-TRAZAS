import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido Fibra TR-S-DER-02", layout="wide")

# ----- Función para calcular distancia Haversine -----
def haversine(coord1, coord2):
    R = 6371000  # metros
    lat1, lon1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# ----- Coordenadas desde KMZ -----
coordenadas = [
    (-35.4708633166351,  -69.57766819274954),
    (-35.47083740176508, -69.57721906428888),
    (-35.46764651517933, -69.57737240456761),
    (-35.46761649309932, -69.5759568599952),
    (-35.46756355662158, -69.57341267990935),
    (-35.47194972736314, -69.57318668647875),
    (-35.47188945240595, -69.57254924372452),
    (-35.47297521564813, -69.5724348810358),
    (-35.47299678040343, -69.57282559280863),
]

nombres = [
    "DATACENTER", "FOSC 01", "FOSC 02",
    "HUB 1.1", "HUB 1.2", "HUB 2.1",
    "HUB 2.2", "HUB 3.1", "HUB 3.2"
]

# ----- Cálculo de distancias acumuladas -----
distancias = []
acumulada = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acumulada += d
        distancias.append(round(acumulada, 1))

# Total recorrido
distancia_total = distancias[-1]

# ----- Sidebar -----
st.sidebar.header("Corte de Fibra Óptica")
descripcion = st.sidebar.text_input("Descripción del corte")
distancia_corte = st.sidebar.number_input(
    f"Ingrese la distancia del corte (0–{int(distancia_total)} m)",
    min_value=0.0,
    max_value=distancia_total,
    step=1.0
)

# Mensaje informativo
if descripcion:
    st.sidebar.info(f"Descripción: {descripcion}")
st.sidebar.caption(f"Distancia total del recorrido: {int(distancia_total)} m")

# ----- Preparar puntos -----
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

# ----- Crear segmentos coloreados según el corte -----
segmentos = []
for i in range(len(puntos) - 1):
    color = [0, 200, 255]  # azul por defecto
    if distancias[i] >= distancia_corte and distancia_corte > 0:
        color = [255, 0, 0]  # rojo desde el punto del corte
    segmentos.append({
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i + 1]["lon"], puntos[i + 1]["lat"]]
        ],
        "color": color
    })

df_puntos = pd.DataFrame(puntos)
df_segmentos = pd.DataFrame(segmentos)

# ----- Capas Pydeck -----
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
    get_radius=3,  # tamaño ajustado
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist}",
    "style": {"backgroundColor": "white"}
}

st.title("Recorrido de fibra óptica – TR-S-DER-02")
st.pydeck_chart(pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
