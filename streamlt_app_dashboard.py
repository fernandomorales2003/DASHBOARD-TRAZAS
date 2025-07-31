import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido de Fibra Óptica", layout="wide")

# Función para calcular distancia entre coordenadas (Haversine)
def haversine(coord1, coord2):
    R = 6371000  # radio de la Tierra en metros
    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ----- Datos de ambas trazas -----

trazas = {
    "TR-S-DER-02": {
        "coordenadas": [
            (-32.925539, -68.857414), (-32.926744, -68.857481),
            (-32.928124, -68.857580), (-32.929415, -68.857657),
            (-32.930814, -68.857738), (-32.932139, -68.857819),
            (-32.933444, -68.857885), (-32.934757, -68.857960)
        ],
        "nombres": [
            "DATACENTER", "FUSIÓN 1", "FUSIÓN 2", "FUSIÓN 3",
            "FUSIÓN 4", "FUSIÓN 5", "FUSIÓN 6", "FUSIÓN 7"
        ],
        "color_base": [0, 255, 0]  # Verde
    },
    "TR1-SUR": {
        "coordenadas": [
            (-35.470812, -69.577695), (-35.470874, -69.577691),
            (-35.470914, -69.578495), (-35.473146, -69.578359),
            (-35.474385, -69.578319), (-35.474353, -69.577005),
            (-35.476546, -69.576911), (-35.476760, -69.585089),
            (-35.497015, -69.585443), (-35.497223, -69.581949),
            (-35.501802, -69.582158), (-35.501746, -69.582981)
        ],
        "nombres": [
            "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03",
            "FOSC 04", "FOSC 05", "FOSC 06", "FOSC 07",
            "FOSC 08", "FOSC 09", "FOSC 10", "TORRE WISP"
        ],
        "color_base": [0, 200, 255]  # Azul
    }
}

# ---- Menú lateral ----
st.sidebar.title("Configuración del Mapa")
traza_sel = st.sidebar.selectbox("Seleccionar traza", list(trazas.keys()))

# Cargar datos de la traza seleccionada
coordenadas = trazas[traza_sel]["coordenadas"]
nombres = trazas[traza_sel]["nombres"]
color_base = trazas[traza_sel]["color_base"]

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
st.sidebar.markdown(f"**Distancia total:** `{distancia_total:.1f} m`")

# Activar reporte de corte
corte_activo = st.sidebar.checkbox("Informar CORTE DE FIBRA")

distancia_corte = 0
if corte_activo:
    distancia_corte = st.sidebar.number_input(
        "Distancia (en metros) donde se detecta el corte:",
        min_value=0.0,
        max_value=distancia_total,
        value=0.0,
        step=1.0
    )

# Crear puntos y segmentos
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": distancias[i],
    "dist_str": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

segmentos = []
corte_gps = None

for i in range(len(puntos) - 1):
    d_inicio = puntos[i]["dist"]
    d_fin = puntos[i+1]["dist"]
    color = color_base
    if d_inicio < distancia_corte < d_fin:
        # Corte dentro del segmento
        ratio = (distancia_corte - d_inicio) / (d_fin - d_inicio)
        lat_interp = puntos[i]["lat"] + ratio * (puntos[i+1]["lat"] - puntos[i]["lat"])
        lon_interp = puntos[i]["lon"] + ratio * (puntos[i+1]["lon"] - puntos[i]["lon"])
        corte_gps = (lat_interp, lon_interp)

        segmentos.append({
            "coordinates": [[puntos[i]["lon"], puntos[i]["lat"]],
                            [lon_interp, lat_interp]],
            "color": color_base
        })
        segmentos.append({
            "coordinates": [[lon_interp, lat_interp],
                            [puntos[i+1]["lon"], puntos[i+1]["lat"]]],
            "color": [255, 0, 0]
        })
    else:
        if distancia_corte and d_inicio >= distancia_corte:
            color = [255, 0, 0]  # Rojo post-corte
        segmentos.append({
            "coordinates": [[puntos[i]["lon"], puntos[i]["lat"]],
                            [puntos[i+1]["lon"], puntos[i+1]["lat"]]],
            "color": color
        })

# DataFrames para pydeck
df_puntos = pd.DataFrame(puntos)
df_segmentos = pd.DataFrame(segmentos)

# Capas de visualización
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

layers = [line_layer, point_layer]

# Agregar marcador de corte en amarillo
if corte_gps:
    df_corte = pd.DataFrame([{
        "lat": corte_gps[0],
        "lon": corte_gps[1],
        "label": "CORTE DETECTADO",
        "dist_str": f"{distancia_corte:.1f} m"
    }])
    corte_layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_corte,
        get_position='[lon, lat]',
        get_color=[255, 255, 0],  # Amarillo
        get_radius=6,
        pickable=True
    )
    layers.append(corte_layer)

# View inicial
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

# Mostrar mapa
st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip=tooltip
))

