import os
import streamlit as st
import pandas as pd
import pydeck as pdk
from zipfile import ZipFile
from xml.etree import ElementTree as ET

# --- TOKEN MAPBOX necesario para visualizar el mapa en Streamlit Cloud
os.environ["MAPBOX_API_KEY"] = "pk.eyJ1IjoiZGVtb3VzZXIiLCJhIjoiY2xwbnU1MnM1MGQ3dzN1bzRxenVjcjhuciJ9.nWTWVG93nTbXKDCWQBoSCA"

st.set_page_config(page_title="Fiber Route Mendoza KMZ", layout="wide")
st.title("📍 Simulación de recorrido FTTH con KMZ (Mendoza)")

# --- Función para cargar y parsear el archivo KMZ
@st.cache_data
def cargar_kmz(kmz_file):
    with ZipFile(kmz_file, 'r') as kmz:
        kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
        with kmz.open(kml_files[0]) as f:
            kml_data = f.read()

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    root = ET.fromstring(kml_data)
    placemarks = root.findall(".//kml:Placemark", ns)

    lineas = []
    puntos = []

    for pm in placemarks:
        name = pm.find("kml:name", ns).text if pm.find("kml:name", ns) is not None else "Sin nombre"
        line = pm.find(".//kml:LineString", ns)
        point = pm.find(".//kml:Point", ns)

        if line is not None:
            coords_text = line.find("kml:coordinates", ns).text.strip()
            coords = [c.split(',') for c in coords_text.split()]
            path = [{"lon": float(lon), "lat": float(lat)} for lon, lat, *_ in coords]
            lineas.append({"name": name, "path": path})
        elif point is not None:
            coord = point.find("kml:coordinates", ns).text.strip().split(",")
            puntos.append({
                "name": name,
                "lon": float(coord[0]),
                "lat": float(coord[1])
            })

    return lineas, puntos

# --- Subida del archivo KMZ
archivo = st.file_uploader("📁 Subí tu archivo KMZ", type=["kmz"])

if archivo:
    with open("traza.kmz", "wb") as f:
        f.write(archivo.read())

    lineas, puntos = cargar_kmz("traza.kmz")

    if not lineas and not puntos:
        st.error("⚠️ El archivo KMZ no contiene trazas ni elementos.")
        st.stop()

    # --- Centro aproximado del mapa
    lat0 = pd.DataFrame(puntos)["lat"].mean() if puntos else pd.DataFrame(lineas[0]["path"])["lat"].mean()
    lon0 = pd.DataFrame(puntos)["lon"].mean() if puntos else pd.DataFrame(lineas[0]["path"])["lon"].mean()

    view_state = pdk.ViewState(latitude=lat0, longitude=lon0, zoom=13.5, pitch=0)

    layers = []

    # --- Dibujar líneas de traza
    for i, linea in enumerate(lineas):
        df_linea = pd.DataFrame(linea["path"])
        color = [255, 0, 0] if "TRONCAL" in linea["name"].upper() else [0, 100, 255]

        layers.append(pdk.Layer(
            "LineLayer",
            data=df_linea,
            get_source_position="[lon, lat]",
            get_target_position="[lon, lat]",
            get_color=color,
            get_width=5,
            id=f"linea_{i}"
        ))

    # --- Dibujar puntos de elementos interiores
    if puntos:
        df_puntos = pd.DataFrame(puntos)
        layers.append(pdk.Layer(
            "ScatterplotLayer",
            data=df_puntos,
            get_position='[lon, lat]',
            get_color=[0, 200, 0],
            get_radius=50,
            pickable=True,
        ))

    # --- Tooltip sobre los puntos
    tooltip = {"html": "<b>{name}</b>", "style": {"backgroundColor": "white", "color": "black"}}

    # --- Mostrar mapa
    st.pydeck_chart(pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v9"
    ))
else:
    st.info("🗂️ Esperando un archivo KMZ para visualizar la traza de fibra.")
