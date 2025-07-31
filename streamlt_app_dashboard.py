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
    # Guardar archivo KMZ
    kmz_path = "temp.kmz"
    kml_path = "ruta.kml"

    with open(kmz_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extraer el archivo .kml del .kmz
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        for file in kmz.namelist():
            if file.endswith(".kml"):
                kmz.extract(file, path=".")
                os.rename(file, kml_path)
                break

    # Leer y parsear KML
    with open(kml_path, "r", encoding="utf-8") as f:
        doc = f.read()

   k = kml.KML()
k.from_string(doc)

# Función recursiva para obtener todos los Placemarks del árbol
def get_all_placemarks(features):
    placemarks = []
    for f in features:
        try:
            if hasattr(f, 'geometry') and f.geometry:
                placemarks.append(f)
            elif hasattr(f, 'features'):
                placemarks.extend(get_all_placemarks(list(f.features())))
        except Exception as e:
            st.warning(f"Error al procesar un feature: {e}")
    return placemarks

# Obtener todos los niveles desde la raíz
try:
    root_features = list(k.features())
    if not root_features:
        st.error("El archivo KML no contiene geometría reconocible.")
        st.stop()
    all_placemarks = get_all_placemarks(root_features)
except Exception as e:
    st.error(f"No se pudo procesar el archivo KML: {e}")
    st.stop()
    # Procesar geometrías
    puntos = []
    lineas = []

    for pm in all_placemarks:
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

    # Capas para Pydeck
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
