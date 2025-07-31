import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido Fibra TR-S-DER-02", layout="wide")

# -------------------- Función Haversine --------------------
def haversine(coord1, coord2):
    R = 6371000  # metros
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# -------------------- Coordenadas y nombres --------------------
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

# -------------------- Cálculo de distancias acumuladas --------------------
distancias = []
acumulada = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acumulada += d
        distancias.append(round(acumulada, 1))

dist_total = round(acumulada, 1)

# -------------------- Entrada del usuario --------------------
st.title("Recorrido de fibra óptica – TR-S-DER-02")
st.write(f"Distancia total del enlace: **{dist_total} m**")

corte_metros = st.number_input(
    "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
    min_value=0.0,
    max_value=dist_total,
    step=10.0,
    value=0.0,
    help="El valor no puede superar la distancia total del enlace."
)

st.info(f"Distancia ingresada para el corte: {corte_metros} m")

# -------------------- Crear DataFrame de puntos --------------------
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

df_puntos = pd.DataFrame(puntos)

# -------------------- Construcción de segmentos por colores --------------------
segmentos_azul = []
segmentos_rojo = []
acumulada = 0

for i in range(len(coordenadas) - 1):
    p1, p2 = coordenadas[i], coordenadas[i+1]
    d = haversine(p1, p2)

    if acumulada + d <= corte_metros or corte_metros == 0:
        segmentos_azul.append({"coordinates": [[p1[1], p1[0]], [p2[1], p2[0]]]})
    elif acumulada >= corte_metros:
        segmentos_rojo.append({"coordinates": [[p1[1], p1[0]], [p2[1], p2[0]]]})
    else:
        # Dividir el segmento en 2 partes si el corte está dentro de este tramo
        ratio = (corte_metros - acumulada) / d
        lat_cut = p1[0] + ratio * (p2[0] - p1[0])
        lon_cut = p1[1] + ratio * (p2[1] - p1[1])
        # Azul hasta el punto de corte
        segmentos_azul.append({"coordinates": [[p1[1], p1[0]], [lon_cut, lat_cut]]})
        # Rojo después del punto de corte
        segmentos_rojo.append({"coordinates": [[lon_cut, lat_cut], [p2[1], p2[0]]]})
    acumulada += d

df_azul = pd.DataFrame(segmentos_azul)
df_rojo = pd.DataFrame(segmentos_rojo)

# -------------------- Capas de pydeck --------------------
linea_azul = pdk.Layer(
    "LineLayer",
    data=df_azul,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

linea_roja = pdk.Layer(
    "LineLayer",
    data=df_rojo,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[255, 0, 0],
    get_width=4,
)

puntos_layer = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color=[255, 0, 0],
    get_radius=4.5,  # 50% más grande
    pickable=True,
)

view_state = pdk.ViewState(
    latitude=coordenadas[0][0],
    longitude=coordenadas[0][1],
    zoom=15.5,
    pitch=0,
)

tooltip = {
    "html": "<b>{label}</b><br/>Distancia: {dist}",
    "style": {"backgroundColor": "white"}
}

# -------------------- Render del Mapa --------------------
st.pydeck_chart(pdk.Deck(
    layers=[linea_azul, linea_roja, puntos_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
