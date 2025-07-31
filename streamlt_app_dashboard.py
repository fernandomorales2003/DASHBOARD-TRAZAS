import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import zipfile
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Recorrido Fibra", layout="wide")

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

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
        with zipfile.ZipFile("TR1 SUR.kmz", "r") as kmz:
            kml_str = kmz.read("doc.kml").decode("utf-8")
        root = ET.fromstring(kml_str)
        ns = {"kml": "http://www.opengis.net/kml/2.2"}
        coords = root.findall(".//kml:Placemark/kml:Point/kml:coordinates", ns)
        coordenadas = []
        for c in coords:
            lon, lat, *_ = map(float, c.text.strip().split(","))
            coordenadas.append((lat, lon))
        nombres = [
            "PUNTO 1 - DATACENTER",
            "PUNTO 2 - FOSC 01",
            "PUNTO 3 - FOSC 02",
            "PUNTO 4 - FOSC 03",
            "PUNTO 5 - FOSC 04",
            "PUNTO 6 - FOSC 05",
            "PUNTO 7 - FOSC 06",
            "PUNTO 8 - FOSC 07",
            "PUNTO 9 - FOSC 08",
            "PUNTO 10 - FOSC 09",
            "PUNTO 11 - FOSC 10",
            "PUNTO 12 - FOSC 11",
            "PUNTO 13 - FOSC 12",
            "PUNTO 14 - FOSC 13",
            "PUNTO 15 - FOSC 14",
            "PUNTO 16 - FOSC 15",
            "PUNTO 17 - FOSC 16",
            "PUNTO 18 - FOSC 17",
            "PUNTO 19 - FOSC 18",
            "PUNTO 20 - FOSC 19",
            "PUNTO 21 - FOSC 20",
            "PUNTO 22 - FOSC 21",
            "PUNTO 23 - FOSC 22",
            "PUNTO 24 - FOSC 23",
            "TORRE WISP"
        ]

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
            [puntos[i+1]["lon"], puntos[i+1]["lat"]]
        ],
        "dist": puntos[i+1]["dist"]
    } for i in range(len(puntos) - 1)]

    return pd.DataFrame(puntos), pd.DataFrame(segmentos), round(acumulada, 1), coordenadas

# UI
traza = st.selectbox("Seleccioná la traza:", ["TR-S-DER-02", "TR1SUR"])
df_puntos, df_lineas, total_distancia, coordenadas = generar_dataframe(traza)

st.markdown(f"### Distancia total del enlace **{traza}**: `{total_distancia} m`")

mostrar_corte = st.checkbox("Informar CORTE DE FIBRA")

corte = 0
if mostrar_corte:
    corte = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0, max_value=total_distancia, step=1.0
    )

# Capas de línea con color según corte
lineas_color = []
for i, row in df_lineas.iterrows():
    color = [0, 200, 255] if corte == 0 or row["dist"] <= corte else [255, 0, 0]
    lineas_color.append({
        "coordinates": row["coordinates"],
        "color": color
    })

line_layer = pdk.Layer(
    "LineLayer",
    data=lineas_color,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color="color",
    get_width=4,
)

# Capa de puntos
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=4.5,
    pickable=True,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist} m",
    "style": {"backgroundColor": "white"}
}

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0,
)

st.pydeck_chart(pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
