# fiber_map_kml.py

import streamlit as st
import zipfile
from fastkml import kml
from shapely.geometry import LineString, Point
import pandas as pd
import pydeck as pdk
import os

st.set_page_config(page_title="Recorrido de Fibra desde KML", layout="wide")
st.title("Visualización de Recorrido de Fibra Óptica desde archivo KMZ")

uploaded_file = st.file_uploader("Subí el archivo KMZ (KML comprimido)", type=["kmz"])

if uploaded_file:
    # Guardar archivo
    kmz_path = "temp.kmz"
    kml_path = "ruta.kml"

    with open(kmz_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extraer el KML del KMZ
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        for file in kmz.namelist():
            if file.endswith(".kml"):
                kmz.extract(file, path=".")
                os.rename(file, kml_path)
                break

    # Leer el archivo KML
    with open(kml_path, "r", encoding="utf-8") as f:
        doc = f.read()

    # Parsear el KML
    k = kml.KML()
    k.from_string(doc)
    features = list(k.features())
    placemarks = list(features[0].features())

    puntos = []
    lineas = []

    for pm in placemarks:
        geom = pm.geometry
        if isinstance(geom, Point):
            puntos.append({
                "label": pm.name,
                "lat": geom.y,
                "lon": geom.x
            })
        elif isinstance(geom, LineString):
            coords = list(geom.coords)
            for i in range(len(coords) - 1):
                lineas.append({"coordinates": [list(coords[i]), list(coords[i+1])]})


    df_puntos = pd.DataFrame(puntos)
    df_lineas = pd.DataFrame(lineas)

    # Mapa
    point_layer = pdk.Layer(
        "ScatterplotLayer", data=df_puntos,
        get_position='[lon, lat]', get_color=[255, 0, 0],
        get_radius=50, pickable=True
    )

    line_layer = pdk.Layer(
        "LineLayer", data=df_lineas,
        get_source_position="coordinates[0]",
        get_target_position="coordinates[1]",
        get_color=[0, 200, 255], get_width=4
    )

    if not df_puntos.empty:
        center_lat = df_puntos["lat"].mean()
        center_lon = df_puntos["lon"].mean()
    else:
        center_lat = center_lon = 0

    view_state = pdk.ViewState(
        latitude=center_lat, longitude=center_lon,
        zoom=13, pitch=0
    )

    tooltip = {"html": "<b>{label}</b>", "style": {"backgroundColor": "white"}}

    st.pydeck_chart(pdk.Deck(
        layers=[line_layer, point_layer],
        initial_view_state=view_state,
        tooltip=tooltip
    ))
