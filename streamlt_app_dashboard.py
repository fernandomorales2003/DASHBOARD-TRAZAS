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
    kmz_path = "temp.kmz"
    kml_path = "ruta.kml"

    with open(kmz_path, "wb") as f:
        f.write(uploaded_file.read())

    # Extraer KML desde KMZ
    with zipfile.ZipFile(kmz_path, 'r') as archive:
        for fname in archive.namelist():
            if fname.endswith(".kml"):
                archive.extract(fname, path=".")
                os.rename(fname, kml_path)
                break

    # Leer el archivo KML
    with open(kml_path, "r", encoding="utf-8") as f:
        kml_content = f.read()

    kml_parser = kml.KML()
    kml_parser.from_string(kml_content)

    # Función recursiva para extraer todos los Placemark
    def extract_placemarks(feature_list):
        placemarks = []
        for feat in feature_list:
            try:
                if hasattr(feat, "geometry") and feat.geometry:
                    placemarks.append(feat)
                elif hasattr(feat, "features"):
                    children = list(feat.features())
                    placemarks.extend(extract_placemarks(children))
            except Exception as e:
                st.warning(f"Error procesando un feature: {e}")
        return placemarks

    try:
        all_features = list(kml_parser.features())
        if not all_features:
            st.error("No se encontraron features en el KML.")
            st.stop()
        placemarks = extract_placemarks(all_features)
    except Exception as e:
        st.error(f"No se pudo procesar el archivo KML: {e}")
        st.stop()

    # Armar dataframes
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
            coords = l

