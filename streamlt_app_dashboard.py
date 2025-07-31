import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Recorrido de Fibra", layout="wide")

# ---------- Funciones ----------
def haversine(coord1, coord2):
    R = 6371000  # metros
    lat1, lon1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generar_traza(nombre):
    if nombre == "TR-S-DER-02":
        coords = [
            (-33.085064, -68.46635),
            (-33.084365, -68.467158),
            (-33.083632, -68.467997),
            (-33.082891, -68.468815),
            (-33.082170, -68.469633),
            (-33.081450, -68.470452),
            (-33.080780, -68.471240)
        ]
        nombres = [
            "DATACENTER", "FUSIÓN 1", "FUSIÓN 2", "FUSIÓN 3",
            "FUSIÓN 4", "FUSIÓN 5", "OLT 1"
        ]
    else:  # TR1-SUR
        coords = [
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
        nombres = [
            "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03", "FOSC 04", "FOSC 05",
            "FOSC 06", "FOSC 07", "FOSC 08", "FOSC 09", "FOSC 10", "TORRE WISP"
        ]
    return coords, nombres

# ---------- Barra lateral ----------
st.sidebar.title("Configuración de Traza")
traza_seleccionada = st.sidebar.selectbox("Seleccionar traza", ["TR-S-DER-02", "TR1-SUR"])

coordenadas, nombres = generar_traza(traza_seleccionada)

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

distancia_total = distancias[-1]
st.sidebar.markdown(f"**Distancia total:** `{distancia_total:.1f} m`")

# Corte de fibra
corte_activo = st.sidebar.checkbox("Informar CORTE DE FIBRA")
distancia_corte = 0
if corte_activo:
    distancia_corte = st.sidebar.number_input(
        "Ingresá la distancia (en metros) del corte:",
        min_value=0.0,
        max_value=distancia_total,
        value=0.0,
        step=1.0
    )

# ---------- Construcción de datos ----------
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": distancias[i],
    "dist_str": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

segmentos = []
corte_marcado = None

for i in range(len(puntos) - 1):
    d_inicio = puntos[i]["dist"]
    d_fin = puntos[i+1]["dist"]
    color = [0, 200, 255]  # Azul por defecto

    if corte_activo and d_inicio < distancia_corte < d_fin:
        # Interpolación
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

        corte_marcado = {
            "lat": lat_interp,
            "lon": lon_interp,
            "label": "Corte detectado a posición GPS"
        }
    else:
        if corte_activo and d_inicio >= distancia_corte:
            color = [255, 0, 0]  # Rojo
        segmentos.append({
            "coordinates": [
                [puntos[i]["lon"], puntos[i]["lat"]],
                [puntos[i+1]["lon"], puntos[i+1]["lat"]]
            ],
            "color": color
        })

# ---------- DataFrames ----------
df_puntos = pd.DataFrame(puntos)
df_segmentos = pd.DataFrame(segmentos)

layers = [
    pdk.Layer(
        "LineLayer",
        data=df_segmentos,
        get_source_position="coordinates[0]",
        get_target_position="coordinates[1]",
        get_color="color",
        get_width=4,
    ),
    pdk.Layer(
        "ScatterplotLayer",
        data=df_puntos,
        get_position='[lon, lat]',
        get_color=[255, 0, 0],
        get_radius=5,
        pickable=True,
    )
]

# Agregar punto de corte si existe
if corte_marcado:
    df_corte = pd.DataFrame([corte_marcado])
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=df_corte,
            get_position='[lon, lat]',
            get_color=[255, 255, 0],  # Amarillo
            get_radius=8,
            pickable=True,
        )
    )

# ---------- Visualización ----------
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
    layers=layers,
    initial_view_state=view_state,
    tooltip=tooltip
))
