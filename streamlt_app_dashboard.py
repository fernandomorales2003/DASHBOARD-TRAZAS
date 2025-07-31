import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import zipfile
from xml.etree import ElementTree as ET

st.set_page_config(page_title="Recorrido de fibra óptica", layout="wide")

# ---------- Funciones generales ----------

def haversine(coord1, coord2):
    R = 6371000  # metros
    lat1, lon1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def cargar_kmz(kmz_path):
    with zipfile.ZipFile(kmz_path, 'r') as z:
        kml_file = [f for f in z.namelist() if f.endswith('.kml')][0]
        with z.open(kml_file) as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            coords = root.findall('.//kml:coordinates', ns)
            coordenadas = []
            for c in coords:
                for line in c.text.strip().split():
                    lon, lat, *_ = map(float, line.split(','))
                    coordenadas.append((lat, lon))
            return coordenadas

def generar_dataframe(nombre_traza):
    if nombre_traza == "TR-S-DER-02":
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
        nombres = [
            "DATACENTER", "FOSC 01", "FOSC 02",
            "HUB 1.1", "HUB 1.2", "HUB 2.1",
            "HUB 2.2", "HUB 3.1", "HUB 3.2"
        ]
    else:  # TR1-SUR
        coordenadas = cargar_kmz("TR1 SUR.kmz")
        nombres = [
            "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03", "FOSC 04",
            "FOSC 05", "FOSC 06", "FOSC 07", "FOSC 08", "FOSC 09",
            "FOSC 10", "TORRE WISP"
        ]

    # Validar longitudes iguales
    if len(coordenadas) != len(nombres):
        st.error(f"Error: Hay {len(coordenadas)} coordenadas pero {len(nombres)} nombres definidos.")
        st.stop()

    distancias = []
    acumulada = 0
    for i in range(len(coordenadas)):
        if i == 0:
            distancias.append(0)
        else:
            d = haversine(coordenadas[i - 1], coordenadas[i])
            acumulada += d
            distancias.append(round(acumulada, 1))

    puntos = [{
        "label": nombres[i],
        "lat": lat,
        "lon": lon,
        "dist": f"{distancias[i]} m",
        "dist_val": distancias[i]
    } for i, (lat, lon) in enumerate(coordenadas)]

    segmentos = [{
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i+1]["lon"], puntos[i+1]["lat"]],
            "dist_acum": puntos[i+1]["dist_val"]
        ]
    } for i in range(len(puntos) - 1)]

    df_puntos = pd.DataFrame(puntos)
    df_lineas = pd.DataFrame(segmentos)
    return df_puntos, df_lineas, round(acumulada, 1), coordenadas

# ---------- Interfaz ----------

traza = st.selectbox("Seleccioná la traza:", ["TR-S-DER-02", "TR1-SUR"])
df_puntos, df_lineas, total_distancia, coordenadas = generar_dataframe(traza)

st.markdown(f"### Distancia total del enlace **{traza}**: `{total_distancia} m`")

# Checkbox para corte de fibra
mostrar_corte = st.checkbox("Informar CORTE DE FIBRA")

if mostrar_corte:
    corte = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=total_distancia,
        step=1.0
    )
else:
    corte = 0

# Capas de líneas por color según distancia
lineas_azules = df_lineas[df_lineas["coordinates"].apply(lambda c: c["dist_acum"] <= corte or corte == 0)]
lineas_rojas = df_lineas[df_lineas["coordinates"].apply(lambda c: c["dist_acum"] > corte and corte != 0)]

line_layer_azul = pdk.Layer(
    "LineLayer",
    data=lineas_azules,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

line_layer_rojo = pdk.Layer(
    "LineLayer",
    data=lineas_rojas,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[255, 0, 0],
    get_width=4,
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=6,
    pickable=True,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist}",
    "style": {"backgroundColor": "white"}
}

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0,
)

st.pydeck_chart(pdk.Deck(
    layers=[line_layer_azul, line_layer_rojo, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
