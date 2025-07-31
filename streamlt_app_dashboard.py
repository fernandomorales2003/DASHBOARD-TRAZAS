import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import zipfile
from xml.etree import ElementTree as ET

st.set_page_config(page_title="Recorrido de fibra óptica", layout="wide")

# ------------------- FUNCIONES ------------------------

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def extraer_coordenadas_kmz(kmz_file):
    with zipfile.ZipFile(kmz_file, 'r') as kmz:
        kml_filename = [f for f in kmz.namelist() if f.endswith('.kml')][0]
        with kmz.open(kml_filename, 'r') as kml_file:
            tree = ET.parse(kml_file)
            root = tree.getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            coords = root.findall('.//kml:coordinates', ns)
            coordenadas = []
            for coord in coords:
                partes = coord.text.strip().split()
                for parte in partes:
                    lon, lat, *_ = parte.split(',')
                    coordenadas.append((float(lat), float(lon)))
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
    else:
        coordenadas = extraer_coordenadas_kmz("TR1 SUR.kmz")
        nombres = [f"PUNTO {i+1}" for i in range(len(coordenadas))]
        nombres[0] = "DATACENTER"
        if len(nombres) >= 2:
            nombres[1] = "FOSC 01"
        if len(nombres) >= 3:
            nombres[2] = "FOSC 02"
        if len(nombres) >= 4:
            nombres[3] = "FOSC 03"
        nombres[-1] = "TORRE WISP"

    # Calcular distancias
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
        "dist": distancias[i]
    } for i, (lat, lon) in enumerate(coordenadas)]

    segmentos = [{
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i+1]["lon"], puntos[i+1]["lat"]],
        ],
        "dist_inicio": puntos[i]["dist"],
        "dist_fin": puntos[i+1]["dist"]
    } for i in range(len(puntos) - 1)]

    df_puntos = pd.DataFrame(puntos)
    df_lineas = pd.DataFrame(segmentos)
    return df_puntos, df_lineas, round(acumulada, 1), coordenadas

# ------------------- UI ------------------------

tab = st.selectbox("Seleccioná la traza a visualizar:", ["TR-S-DER-02", "TR1-SUR"])

df_puntos, df_lineas, total_distancia, coordenadas = generar_dataframe(tab)

st.markdown(f"### Distancia total del enlace: `{total_distancia} m`")

# Informe de corte
distancia_corte = None
activar_corte = st.checkbox("Informar CORTE DE FIBRA")
if activar_corte:
    distancia_corte = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=float(total_distancia),
        step=1.0
    )

# ------------------- MAPA ------------------------

# Dividir en capas azul y roja si hay corte
lineas_azul = []
lineas_rojas = []

for i, row in df_lineas.iterrows():
    if distancia_corte is not None and row["dist_inicio"] >= distancia_corte:
        lineas_rojas.append(row)
    else:
        lineas_azul.append(row)

line_layer_azul = pdk.Layer(
    "LineLayer",
    data=pd.DataFrame(lineas_azul),
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

line_layer_roja = pdk.Layer(
    "LineLayer",
    data=pd.DataFrame(lineas_rojas),
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
    get_radius=3,
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist} m",
    "style": {"backgroundColor": "white"}
}

st.pydeck_chart(pdk.Deck(
    layers=[line_layer_azul, line_layer_roja, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))


