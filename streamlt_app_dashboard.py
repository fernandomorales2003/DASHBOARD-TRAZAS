import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido de Fibra Óptica", layout="wide")

def haversine(coord1, coord2):
    R = 6371000
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# TR-S-DER-02
coordenadas_der = [
    (-33.085064, -68.46635),
    (-33.078960, -68.465488),
    (-33.074265, -68.464701),
    (-33.071256, -68.464160),
    (-33.066320, -68.463288),
    (-33.061682, -68.462452),
    (-33.057482, -68.461684),
    (-33.053170, -68.460850),
    (-33.048527, -68.460007)
]

nombres_der = [
    "DATACENTER", "FUSIÓN 1", "FUSIÓN 2", "FUSIÓN 3",
    "FUSIÓN 4", "FUSIÓN 5", "FUSIÓN 6", "FUSIÓN 7", "OLT1"
]

# TR1-SUR
coordenadas_sur = [
    (-35.470812, -69.577695),
    (-35.470874, -69.577691),
    (-35.470914, -69.578495),
    (-35.473146, -69.578359),
    (-35.474385, -69.578319),
    (-35.474353, -69.577005),
    (-35.476546, -69.576911),
    (-35.476760, -69.585089),
    (-35.497015, -69.585443),
    (-35.497223, -69.581949),
    (-35.501802, -69.582158),
    (-35.501746, -69.582981)
]

nombres_sur = [
    "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03",
    "FOSC 04", "FOSC 05", "FOSC 06", "FOSC 07",
    "FOSC 08", "FOSC 09", "FOSC 10", "TORRE WISP"
]

# Selección de traza
traza_seleccionada = st.selectbox("Seleccioná la traza:", ["TR-S-DER-02", "TR1-SUR"])

if traza_seleccionada == "TR-S-DER-02":
    coordenadas = coordenadas_der
    nombres = nombres_der
else:
    coordenadas = coordenadas_sur
    nombres = nombres_sur

# Cálculo de distancias
distancias = []
acum = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acum += d
        distancias.append(round(acum, 1))

distancia_total = distancias[-1]
st.markdown(f"### Distancia total del enlace: `{distancia_total:.1f} m`")

# Checkbox para corte
corte_activo = st.checkbox("Informar CORTE DE FIBRA")
distancia_corte = 0
if corte_activo:
    distancia_corte = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=distancia_total,
        value=0.0,
        step=1.0
    )

# Puntos y segmentos
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": distancias[i],
    "dist_str": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

segmentos = []
for i in range(len(puntos) - 1):
    d_inicio = puntos[i]["dist"]
    d_fin = puntos[i+1]["dist"]
    color = [0, 200, 255]  # Azul
    if d_inicio < distancia_corte < d_fin:
        ratio = (distancia_corte - d_inicio) / (d_fin - d_inicio)
        lat_interp = puntos[i]["lat"] + ratio * (puntos[i+1]["lat"] - puntos[i]["lat"])
        lon_interp = puntos[i]["lon"] + ratio * (puntos[i+1]["lon"] - puntos[i]["lon"])
        segmentos.append({
            "coordinates": [
                [puntos[i]["lon"], puntos[i]["lat"]],
                [lon_interp, lat_interp]
            ],
            "color": [0, 200, 255]
        })
        segmentos.append({
            "coordinates": [
                [lon_interp, lat_interp],
                [puntos[i+1]["lon"], puntos[i+1]["lat"]]
            ],
            "color": [255, 0, 0]
        })
    else:
        if distancia_corte and d_inicio >= distancia_corte:
            color = [255, 0, 0]  # Rojo
        segmentos.append({
            "coordinates": [
                [puntos[i]["lon"], puntos[i]["lat"]],
                [puntos[i+1]["lon"], puntos[i+1]["lat"]]
            ],
            "color": color
        })

df_puntos = pd.DataFrame(puntos)
df_segmentos = pd.DataFrame(segmentos)

line_layer = pdk.Layer(
    "LineLayer",
    data=df_segmentos,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color="color",
    get_width=4
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=4.5,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=13,
    pitch=0
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist_str}",
    "style": {"backgroundColor": "white"}
}

st.pydeck_chart(pdk.Deck(
    layers=[line_layer, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
