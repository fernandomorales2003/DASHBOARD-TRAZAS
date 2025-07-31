import streamlit as st
import pandas as pd
import pydeck as pdk
from zipfile import ZipFile
from xml.etree import ElementTree as ET

st.set_page_config(page_title="FTTH Malargüe", layout="wide")

# ---------- CARGA Y PARSEO DEL ARCHIVO KMZ ----------

@st.cache_data
def cargar_kmz(path):
    with ZipFile(path, 'r') as kmz:
        kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
        with kmz.open(kml_files[0]) as kml_file:
            kml_content = kml_file.read()

    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    root = ET.fromstring(kml_content)
    placemarks = root.findall(".//kml:Placemark", ns)

    lineas = []
    puntos = []

    for pm in placemarks:
        name = pm.find("kml:name", ns)
        line = pm.find(".//kml:LineString", ns)
        point = pm.find(".//kml:Point", ns)

        if line is not None:
            coords_text = line.find("kml:coordinates", ns).text.strip()
            coords = [c.split(',') for c in coords_text.split()]
            path = [{"lon": float(lon), "lat": float(lat)} for lon, lat, *_ in coords]
            lineas.append({"type": "LineString", "name": name.text if name is not None else "", "path": path})
        elif point is not None:
            coord = point.find("kml:coordinates", ns).text.strip().split(",")
            puntos.append({
                "type": "Point",
                "name": name.text if name is not None else "",
                "lon": float(coord[0]),
                "lat": float(coord[1])
            })

    return lineas, puntos

# Cambiar ruta si lo usás localmente
kmz_path = "FTTH-MALARGUE.kmz"
lineas, puntos = cargar_kmz(kmz_path)

# ---------- VISUALIZACIÓN ----------

st.title("🧭 Visualización de Red FTTH – Malargüe")

# Centro del mapa
lat_centro = pd.DataFrame(puntos)["lat"].mean()
lon_centro = pd.DataFrame(puntos)["lon"].mean()

view_state = pdk.ViewState(
    latitude=lat_centro,
    longitude=lon_centro,
    zoom=14,
    pitch=0,
)

# Capas a visualizar
layers = []

# --- CAPAS DE LÍNEAS ---
st.sidebar.subheader("🟦 Trazas de fibra")

for i, linea in enumerate(lineas):
    nombre = linea["name"]
    coords = linea["path"]

    if st.sidebar.checkbox(f"🧵 {nombre}", value=True, key=f"line_{i}"):
        df_coords = pd.DataFrame(coords)
        color = [255, 0, 0] if "TRONCAL" in nombre.upper() else [0, 150, 255]
        capa = pdk.Layer(
            "LineLayer",
            data=df_coords,
            get_source_position="index",
            get_target_position="index + 1",
            get_position=lambda x: [df_coords.iloc[x]["lon"], df_coords.iloc[x]["lat"]],
            get_color=color,
            get_width=5,
            pickable=True,
            id=f"linea_{i}",
        )
        layers.append(capa)

# --- CAPA DE PUNTOS ---
st.sidebar.subheader("📍 Elementos interiores")

if st.sidebar.checkbox("Mostrar puntos", value=True):
    df_puntos = pd.DataFrame(puntos)
    puntos_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_puntos,
        get_position='[lon, lat]',
        get_color=[0, 200, 0],
        get_radius=40,
        pickable=True,
    )
    layers.append(puntos_layer)

tooltip = {
    "html": "<b>{name}</b>",
    "style": {"backgroundColor": "white", "color": "black"}
}

st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip=tooltip,
    map_style="mapbox://styles/mapbox/light-v9"
))
