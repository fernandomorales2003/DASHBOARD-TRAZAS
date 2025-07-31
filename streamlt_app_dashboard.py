import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Recorrido Fibra TR-S-DER-02", layout="wide")

# Coordenadas reales extraídas desde el KMZ (lat, lon)
coordenadas = [
    (-35.4708633166351, -69.57766819274954),
    (-35.47083740176508, -69.57721906428888),
    (-35.46764651517933, -69.57737240456761),
    (-35.46761649309932, -69.5759568599952),
    (-35.46756355662158, -69.57341267990935),
    (-35.46753178131413, -69.57224349438995),
    (-35.46837993738643, -69.57198745833407),
    (-35.46893739593073, -69.57172257903295),
    (-35.46912611146244, -69.57036092765886),
    (-35.46920773755725, -69.56846211087797),
    (-35.47012176367126, -69.56763305227337),
]

# Construcción de puntos y segmentos
puntos = [{"label": f"Punto {i+1}", "lat": lat, "lon": lon} for i, (lat, lon) in enumerate(coordenadas)]

segmentos = []
for i in range(len(puntos) - 1):
    segmentos.append({
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i + 1]["lon"], puntos[i + 1]["lat"]]
        ]
    })

df_puntos = pd.DataFrame(puntos)
df_lineas = pd.DataFrame(segmentos)

# Capas de visualización
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
    get_radius=60,
    pickable=True,
)

# Vista centrada en el primer punto
view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=14,
    pitch=0,
)

tooltip = {"html": "<b>{label}</b>", "style": {"backgroundColor": "white"}}

st.title("Recorrido de fibra óptica – TR-S-DER-02")
st.pydeck_chart(pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
