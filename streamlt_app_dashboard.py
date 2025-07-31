import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import zipfile
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Dashboard Recorrido de Fibra", layout="wide")

# ------------------------------------------
# FUNCIONES
# ------------------------------------------
def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_kmz_coordinates(kmz_path):
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kml_file = [f for f in kmz.namelist() if f.endswith('.kml')][0]
        with kmz.open(kml_file, 'r') as file:
            tree = ET.parse(file)
            root = tree.getroot()
            ns = {'kml': 'http://www.opengis.net/kml/2.2'}
            coords = []
            for placemark in root.findall('.//kml:Placemark', ns):
                coord_elem = placemark.find('.//kml:coordinates', ns)
                if coord_elem is not None:
                    coord_text = coord_elem.text.strip()
                    lon, lat, *_ = map(float, coord_text.split(','))
                    coords.append((lat, lon))
            return coords

def generar_dataframe(traza_nombre):
    if traza_nombre == "TR-S-DER-02":
        coords = [
            (-35.4708633166351, -69.57766819274954),
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
            "DATACENTER", "FOSC 01", "FOSC 02", "HUB 1.1", "HUB 1.2",
            "HUB 2.1", "HUB 2.2", "HUB 3.1", "HUB 3.2"
        ]
    else:  # TR1-SUR
        coords = parse_kmz_coordinates("TR1 SUR.kmz")
        nombres = [f"PUNTO {i+1} - " + (
            "DATACENTER" if i == 0 else "TORRE WISP" if i == len(coords) - 1 else f"FOSC {i:02}"
        ) for i in range(len(coords))]

    distancias = [0]
    acumulada = 0
    for i in range(1, len(coords)):
        d = haversine(coords[i - 1], coords[i])
        acumulada += d
        distancias.append(acumulada)

    puntos = [{
        "label": nombres[i],
        "lat": coords[i][0],
        "lon": coords[i][1],
        "dist": f"{distancias[i]:.1f} m",
        "dist_val": distancias[i]
    } for i in range(len(coords))]

    segmentos = [{
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i + 1]["lon"], puntos[i + 1]["lat"]],
        ],
        "dist_acum": puntos[i + 1]["dist_val"]
    } for i in range(len(puntos) - 1)]

    df_puntos = pd.DataFrame(puntos)
    df_lineas = pd.DataFrame(segmentos)
    return df_puntos, df_lineas, distancias[-1], coords

# ------------------------------------------
# UI Streamlit
# ------------------------------------------
st.title("Recorrido de Fibra Óptica")

traza = st.selectbox("Seleccionar traza", ["TR-S-DER-02", "TR1-SUR"])
df_puntos, df_lineas, total_distancia, coordenadas = generar_dataframe(traza)

st.markdown(f"**Distancia total del enlace:** {total_distancia:.1f} m")

# Activar informe de corte
corte_activo = st.checkbox("Informar CORTE DE FIBRA")
corte_distancia = 0
if corte_activo:
    corte_distancia = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=total_distancia,
        value=0.0,
        step=1.0
    )

# Capa de puntos
point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=30,
    pickable=True,
)

# Capa de líneas según corte
segmentos_corte = df_lineas.to_dict("records")
lineas = []
for seg in segmentos_corte:
    color = [0, 200, 255] if seg["dist_acum"] <= corte_distancia or corte_distancia == 0 else [255, 0, 0]
    lineas.append(pdk.Layer(
        "LineLayer",
        data=[seg],
        get_source_position="coordinates[0]",
        get_target_position="coordinates[1]",
        get_color=color,
        get_width=4
    ))

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
    layers=[point_layer] + lineas,
    initial_view_state=view_state,
    tooltip=tooltip
))
