import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido Fibra TR-S-DER-02", layout="wide")

# Función para calcular distancia entre dos coordenadas
def haversine(coord1, coord2):
    R = 6371000  # Radio de la Tierra en metros
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Coordenadas corregidas desde KMZ
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

# Calcular distancias acumuladas
distancias = []
acumulada = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acumulada += d
        distancias.append(round(acumulada, 1))

# Puntos y líneas
puntos = [{
    "label": f"Punto {i+1}",
    "lat": lat,
    "lon": lon,
    "dist": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

segmentos = [{
    "coordinates": [
        [puntos[i]["lon"], puntos[i]["lat"]],
        [puntos[i+1]["lon"], puntos[i+1]["lat"]]
    ]
} for i in range(len(puntos) - 1)]

df_puntos = pd.DataFrame(puntos)
df_lineas = pd.DataFrame(segmentos)

# Capas para pydeck
line_layer = pdk.Layer(
    "LineLayer",
    data=df_lineas,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=2,  # 10% del tamaño original
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=14,
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
