import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Ruta de Fibra - TR-S-DER-02", layout="wide")

# Coordenadas extraídas del KMZ
coordenadas = [
    (-35.473805, -69.584011),
    (-35.473657, -69.583697),
    (-35.470261, -69.577935),
    (-35.469419, -69.576504),
    (-35.467605, -69.573353),
    (-35.462728, -69.56498),
    (-35.462174, -69.564131),
    (-35.460918, -69.562169),
    (-35.460465, -69.561451),
]

nombres = [
    "DATACENTER",
    "FOSC 01",
    "FOSC 02",
    "HUB 1.1",
    "HUB 1.2",
    "HUB 2.1",
    "HUB 2.2",
    "HUB 3.1",
    "HUB 3.2",
]

# Calcular distancias acumuladas
from geopy.distance import geodesic
distancias = [0]
acum = 0
for i in range(1, len(coordenadas)):
    d = geodesic(coordenadas[i-1], coordenadas[i]).meters
    acum += d
    distancias.append(round(acum, 1))

# DataFrame de puntos
df_puntos = pd.DataFrame({
    "lat": [lat for lat, lon in coordenadas],
    "lon": [lon for lat, lon in coordenadas],
    "label": nombres,
    "distancia": distancias
})

# Icono personalizado solo para DATACENTER
df_puntos["icon_data"] = None
df_puntos.loc[0, "icon_data"] = {
    "url": "https://cdn-icons-png.flaticon.com/512/900/900797.png",
    "width": 128,
    "height": 128,
    "anchorY": 128
}

# Segmentos de línea entre los puntos
segmentos = []
for i in range(len(coordenadas) - 1):
    segmentos.append({
        "coordinates": [
            [coordenadas[i][1], coordenadas[i][0]],
            [coordenadas[i+1][1], coordenadas[i+1][0]]
        ]
    })
df_lineas = pd.DataFrame(segmentos)

# Capas
line_layer = pdk.Layer(
    "LineLayer",
    data=df_lineas,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

icon_layer = pdk.Layer(
    "IconLayer",
    data=df_puntos[df_puntos["icon_data"].notnull()],
    get_icon="icon_data",
    get_position='[lon, lat]',
    get_size=4,
    size_scale=10,
    pickable=True,
)

scatter_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos[1:],  # Excluye DATACENTER
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=75,  # Agrandado 50%
    pickable=True,
)

# Vista inicial más cercana
view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0
)

# Tooltip con información
tooltip = {
    "html": "<b>{label}</b><br/>Distancia desde inicio: {distancia} m",
    "style": {"backgroundColor": "white", "color": "black"}
}

# Render
st.title("Recorrido de Fibra - TR-S-DER-02")
st.pydeck_chart(pdk.Deck(
    layers=[line_layer, icon_layer, scatter_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
