import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Recorrido Fibra TR-S-DER-02", layout="wide")

# Puntos extraídos del archivo KMZ
puntos = [
    {"label": "Inicio", "lat": -35.48093650938789, "lon": -69.58273473535873},
    {"label": "Punto", "lat": -35.48240487851016, "lon": -69.58042579070939},
    {"label": "Punto", "lat": -35.4833245422237, "lon": -69.57873352988782},
    {"label": "Punto", "lat": -35.48535003634032, "lon": -69.57606582049495},
    {"label": "Punto", "lat": -35.48775311021605, "lon": -69.5740814427083},
    {"label": "Fin", "lat": -35.49026422575704, "lon": -69.57225488990632},
]

# Segmentos del recorrido (líneas)
segmentos = []
for i in range(len(puntos)-1):
    segmentos.append({
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i+1]["lon"], puntos[i+1]["lat"]]
        ]
    })

df_puntos = pd.DataFrame(puntos)
df_lineas = pd.DataFrame(segmentos)

# Capa de línea (trayectoria)
line_layer = pdk.Layer(
    "LineLayer",
    data=df_lineas,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

# Capa de puntos
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=60,
    pickable=True,
)

# Vista inicial centrada en el primer punto
view_state = pdk.ViewState(
    latitude=puntos[0]["lat"],
    longitude=puntos[0]["lon"],
    zoom=13,
    pitch=0,
)

tooltip = {"html": "<b>{label}</b>", "style": {"backgroundColor": "white"}}

st.title("Recorrido de fibra óptica – TR-S-DER-02")
st.pydeck_chart(pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
