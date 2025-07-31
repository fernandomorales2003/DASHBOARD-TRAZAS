import streamlit as st
import zipfile
from fastkml import kml
from shapely.geometry import Point, LineString
import pydeck as pdk
import pandas as pd
import os

st.set_page_config(page_title="Recorrido Fibra KMZ", layout="wide")
st.title("Visualización de Recorrido de Fibra desde KMZ")

uploaded_file = st.file_uploader("Subí tu archivo KMZ", type=["kmz"])

if uploaded_file:
    # Guardamos y extraemos
    with open("temp.kmz", "wb") as f:
        f.write(uploaded_file.read())

    with zipfile.ZipFile("temp.kmz", "r") as kmz:
        kml_file = [name for name in kmz.namelist() if name.endswith(".kml")][0]
        kmz.extract(kml_file)
    
    # Leemos el contenido KML
    with open(kml_file, "r", encoding="utf-8") as f:
        doc = f.read()

    k = kml.KML()
    k.from_string(doc)

    # Extraemos todos los objetos (puntos y líneas) sin estructuras anidadas
    def extraer_geometrias(kml_root):
        puntos = []
        lineas = []

        def buscar(feats):
            for f in feats:
                if hasattr(f, "geometry"):
                    if isinstance(f.geometry, Point):
                        puntos.append({
                            "label": f.name or "Punto",
                            "lat": f.geometry.y,
                            "lon": f.geometry.x
                        })
                    elif isinstance(f.geometry, LineString):
                        coords = list(f.geometry.coords)
                        for i in range(len(coords) - 1):
                            lineas.append({
                                "coordinates": [list(coords[i]), list(coords[i + 1])]
                            })
                if hasattr(f, "features"):
                    buscar(list(f.features()))

        buscar(list(k.features()))
        return puntos, lineas

    try:
        puntos, lineas = extraer_geometrias(k)
        df_puntos = pd.DataFrame(puntos)
        df_lineas = pd.DataFrame(lineas)

        # Configuración de layers
        point_layer = pdk.Layer(
            "ScatterplotLayer",
            data=df_puntos,
            get_position='[lon, lat]',
            get_color=[255, 0, 0],
            get_radius=50,
            pickable=True,
        )

        line_layer = pdk.Layer(
            "LineLayer",
            data=df_lineas,
            get_source_position="coordinates[0]",
            get_target_position="coordinates[1]",
            get_color=[0, 200, 255],
            get_width=4,
        )

        # Mapa centrado
        if not df_puntos.empty:
            center_lat = df_puntos["lat"].mean()
            center_lon = df_puntos["lon"].mean()
        else:
            center_lat = center_lon = 0

        view_state = pdk.ViewState(
            latitude=center_lat,
            longitude=center_lon,
            zoom=13,
            pitch=0,
        )

        st.pydeck_chart(pdk.Deck(
            layers=[line_layer, point_layer],
            initial_view_state=view_state,
            tooltip={"html": "<b>{label}</b>", "style": {"backgroundColor": "white"}}
        ))

    except Exception as e:
        st.error(f"No se pudo procesar el archivo KMZ: {e}")
