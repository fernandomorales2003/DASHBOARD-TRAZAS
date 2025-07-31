import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido Fibra TR1-SUR", layout="wide")

# Función para calcular distancia entre coordenadas (Haversine)
def haversine(coord1, coord2):
    R = 6371000  # metros
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

# Coordenadas de TR1-SUR extraídas del KMZ
coordenadas = [
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

# Nombres personalizados
nombres = [
    "PUNTO 1 - DATACENTER", "PUNTO 2 - FOSC 01", "PUNTO 3 - FOSC 02",
    "PUNTO 4 - FOSC 03", "PUNTO 5 - FOSC 04", "PUNTO 6 - FOSC 05",
    "PUNTO 7 - FOSC 06", "PUNTO 8 - FOSC 07", "PUNTO 9 - FOSC 08",
    "PUNTO 10 - FOSC 09", "PUNTO 11 - FOSC 10", "PUNTO 12 - TORRE WISP"
]

# Calcular distancias acumuladas
distancias = []
acumulada = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acumulada += d
        distancias.append(round(acumulada, 1))

# Mostrar distancia total
distancia_total = distancias[-1]
st.markdown(f"### Distancia total del enlace: `{distancia_total:.1f} m`")

# Checkbox para habilitar corte
corte_activo = st.checkbox("Informar CORTE DE FIBRA")

distancia_corte = 0
if corte_activo:
    distancia_corte = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=distancia_total,
        value=0.0,
        step=1.0,
    )

# Generar puntos y segmentos
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
        # Cortar en dos segmentos
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
        if d_inicio > distancia_corte:
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

# Capas de pydeck
line_layer = pdk.Layer(
    "LineLayer",
    data=df_segmentos,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color="color",
    get_width=4,
)

point_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=4.5,
    pickable=True,
)

# Mapa centrado en el primer punto
view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=13,
    pitch=0,
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
