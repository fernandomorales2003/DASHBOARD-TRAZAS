import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(page_title="Dashboard Recorridos de Fibra", layout="wide")

# ------------------ Función para calcular distancia entre coordenadas ------------------
def haversine(coord1, coord2):
    R = 6371000  # Radio terrestre en metros
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ------------------ Trazas de fibra ------------------

trazas = {
    "TR-S-DER-02": {
        "coordenadas": [
            (-35.4708633166351,  -69.57766819274954),
            (-35.47083740176508, -69.57721906428888),
            (-35.46764651517933, -69.57737240456761),
            (-35.46761649309932, -69.5759568599952),
            (-35.46756355662158, -69.57341267990935),
            (-35.47194972736314, -69.57318668647875),
            (-35.47188945240595, -69.57254924372452),
            (-35.47297521564813, -69.5724348810358),
            (-35.47299678040343, -69.57282559280863),
        ],
        "nombres": [
            "DATACENTER", "FOSC 01", "FOSC 02",
            "HUB 1.1", "HUB 1.2", "HUB 2.1",
            "HUB 2.2", "HUB 3.1", "HUB 3.2"
        ]
    },
    "TR1SUR": {
        "coordenadas": [
            (-35.4730863, -69.5729684),
            (-35.4740099, -69.5729239),
            (-35.4751252, -69.5730236),
            (-35.4762636, -69.5729911),
            (-35.4772253, -69.5730797),
            (-35.4781271, -69.5729631),
            (-35.4788925, -69.5728786),
            (-35.4795409, -69.5727586),
            (-35.4802015, -69.5727435),
            (-35.4808795, -69.5727606),
            (-35.4813982, -69.5727803),
            (-35.4820307, -69.5727982),
            (-35.4825607, -69.5728372),
            (-35.4831356, -69.5728735),
            (-35.4836058, -69.5729023),
            (-35.4840177, -69.5729331),
            (-35.4845312, -69.5729755),
            (-35.4851000, -69.5730070),
            (-35.4856378, -69.5730595),
            (-35.4862387, -69.5730999),
            (-35.4868164, -69.5731460),
            (-35.4873772, -69.5731753),
            (-35.4879106, -69.5732147),
            (-35.4883911, -69.5732453),
            (-35.4889000, -69.5732744),
            (-35.4895000, -69.5733000)
        ],
        "nombres": [f"PUNTO {i+1} - FOSC {str(i+1).zfill(2)}" for i in range(24)] + ["TORRE WISP"]
    }
}

# ------------------ Selección de traza ------------------
traza_seleccionada = st.selectbox("Seleccioná la traza a visualizar", list(trazas.keys()))

data = trazas[traza_seleccionada]
coordenadas = data["coordenadas"]
nombres = data["nombres"]

# ------------------ Distancias acumuladas ------------------
distancias = []
acumulada = 0
for i in range(len(coordenadas)):
    if i == 0:
        distancias.append(0)
    else:
        d = haversine(coordenadas[i - 1], coordenadas[i])
        acumulada += d
        distancias.append(round(acumulada, 1))

# ------------------ Info de corte de fibra ------------------
st.markdown(f"**Distancia total del enlace:** {int(acumulada)} metros")

corte_activado = st.checkbox("Informar CORTE DE FIBRA")
corte_distancia = 0

if corte_activado:
    corte_distancia = st.number_input(
        "Ingresá la distancia (en metros) donde se detecta un corte de fibra:",
        min_value=0.0,
        max_value=acumulada,
        step=1.0,
        value=0.0
    )

# ------------------ Puntos ------------------
puntos = [{
    "label": nombres[i],
    "lat": lat,
    "lon": lon,
    "dist": f"{distancias[i]} m"
} for i, (lat, lon) in enumerate(coordenadas)]

# ------------------ Segmentos ------------------
segmentos_azules = []
segmentos_rojos = []

for i in range(len(puntos) - 1):
    dist_inicio = distancias[i]
    dist_fin = distancias[i+1]
    segmento = {
        "coordinates": [
            [puntos[i]["lon"], puntos[i]["lat"]],
            [puntos[i+1]["lon"], puntos[i+1]["lat"]]
        ]
    }
    if dist_fin <= corte_distancia:
        segmentos_azules.append(segmento)
    elif dist_inicio >= corte_distancia:
        segmentos_rojos.append(segmento)
    else:
        segmentos_azules.append(segmento)

# ------------------ Capas ------------------
df_puntos = pd.DataFrame(puntos)
df_azul = pd.DataFrame(segmentos_azules)
df_rojo = pd.DataFrame(segmentos_rojos)

line_layer_azul = pdk.Layer(
    "LineLayer",
    data=df_azul,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255],
    get_width=4,
)

line_layer_rojo = pdk.Layer(
    "LineLayer",
    data=df_rojo,
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
    get_radius=2,
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

# ------------------ Mostrar mapa ------------------
st.title(f"Recorrido de fibra óptica – {traza_seleccionada}")
st.pydeck_chart(pdk.Deck(
    layers=[line_layer_azul, line_layer_rojo, point_layer],
    initial_view_state=view_state,
    tooltip=tooltip
))
