import streamlit as st
import pandas as pd
import pydeck as pdk
import math
import zipfile
import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import os

# --- Funciones auxiliares ---
def haversine(coord1, coord2):
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371 * c * 1000

def extraer_coords_kmz(kmz_path):
    if not os.path.exists(kmz_path):
        return []
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kml_str = kmz.read('doc.kml').decode('utf-8')
    root = ET.fromstring(kml_str)
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    coords = root.findall('.//kml:LineString/kml:coordinates', namespace)
    puntos = []
    for coord in coords:
        pares = coord.text.strip().split()
        for par in pares:
            lon, lat, *_ = map(float, par.split(','))
            puntos.append((lat, lon))
    return puntos

def generar_dataframe(traza):
    if traza == "TR-S-DER-02":
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
        coordenadas = extraer_coords_kmz("TR1 SUR.kmz")
        nombres = [
            f"PUNTO {i+1} - " + nombre for i, nombre in enumerate([
                "DATACENTER", "FOSC 01", "FOSC 02", "FOSC 03", "FOSC 04", "FOSC 05",
                "FOSC 06", "FOSC 07", "FOSC 08", "FOSC 09", "FOSC 10", "TORRE WISP"])
        ]

    distancias = [0]
    total = 0
    for i in range(1, len(coordenadas)):
        d = haversine(coordenadas[i - 1], coordenadas[i])
        total += d
        distancias.append(total)

    df_puntos = pd.DataFrame({
        "nombre": nombres,
        "lat": [p[0] for p in coordenadas],
        "lon": [p[1] for p in coordenadas],
        "dist": distancias
    })

    df_lineas = pd.DataFrame([
        {
            "start_lat": coordenadas[i][0], "start_lon": coordenadas[i][1],
            "end_lat": coordenadas[i + 1][0], "end_lon": coordenadas[i + 1][1],
            "dist_acum": distancias[i + 1]
        }
        for i in range(len(coordenadas) - 1)
    ])

    return df_puntos, df_lineas, total, coordenadas

# --- Streamlit ---
st.set_page_config(page_title="Dashboard de Trazas de Fibra", layout="wide")
st.title("📍 Mapa de trazas de fibra ")

# --- Barra lateral ---
traza = st.sidebar.selectbox("Seleccionar traza", ["TR-S-DER-02", "TR1-SUR"])
corte_activo = st.sidebar.checkbox("Informar corte")
if corte_activo:
    distancia_corte = st.sidebar.number_input("Distancia del corte (m)", min_value=0.0)
else:
    distancia_corte = 0

# --- Datos y coordenadas ---
df_puntos, df_lineas, distancia_total, coordenadas = generar_dataframe(traza)
distancias = df_puntos['dist'].tolist()
nombres = df_puntos['nombre'].tolist()

# --- Clientes por HUB ---
clientes_por_hub = {
    "HUB 1.1": 38, "HUB 1.2": 60,
    "HUB 2.1": 50, "HUB 2.2": 43,
    "HUB 3.1": 35, "HUB 3.2": 55
}

# --- Capas de líneas y puntos ---
colores = []
for _, row in df_lineas.iterrows():
    if corte_activo and row["dist_acum"] > distancia_corte:
        colores.append([255, 0, 0])
    else:
        colores.append([0, 128, 255])

layer_lineas = pdk.Layer(
    "LineLayer",
    data=df_lineas.assign(color=colores),
    get_source_position='[start_lon, start_lat]',
    get_target_position='[end_lon, end_lat]',
    get_color='color',
    get_width=5,
    pickable=True
)

layer_puntos = pdk.Layer(
    "ScatterplotLayer",
    data=df_puntos,
    get_position='[lon, lat]',
    get_color='[0, 200, 100]',
    get_radius=10,
    pickable=True
)

layer_corte = None
if corte_activo and 0 < distancia_corte < distancia_total:
    for i in range(1, len(distancias)):
        if distancias[i] >= distancia_corte:
            ratio = ((distancia_corte - distancias[i - 1]) / (distancias[i] - distancias[i - 1]))
            lat_corte = coordenadas[i - 1][0] + ratio * (coordenadas[i][0] - coordenadas[i - 1][0])
            lon_corte = coordenadas[i - 1][1] + ratio * (coordenadas[i][1] - coordenadas[i - 1][1])
            layer_corte = pdk.Layer(
                "ScatterplotLayer",
                data=pd.DataFrame({"lat": [lat_corte], "lon": [lon_corte]}),
                get_position='[lon, lat]',
                get_color='[255, 255, 0]',
                get_radius=15,
                pickable=True
            )
            break

# --- Mapa ---
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=df_puntos['lat'].mean(),
        longitude=df_puntos['lon'].mean(),
        zoom=15,
        pitch=0,
    ),
    layers=[layer_lineas, layer_puntos] + ([layer_corte] if layer_corte else []),
    tooltip={"text": "{nombre}"}
))

# --- Gráficos de clientes (solo para TR-S-DER-02) ---
if traza == "TR-S-DER-02":
    st.markdown("### Distribución de clientes por HUB y Puerto PON")
    col1, col2 = st.columns(2)

    with col1:
        opcion = st.radio("Seleccionar visualización:", ["Radar Chart", "Barras por PON"])
        if opcion == "Radar Chart":
            labels = list(clientes_por_hub.keys())
            values = list(clientes_por_hub.values())
            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=values, theta=labels, fill='toself', name='Clientes'))
            fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=False)
            st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        pon1 = clientes_por_hub.get("HUB 1.1", 0) + clientes_por_hub.get("HUB 1.2", 0)
        pon2 = clientes_por_hub.get("HUB 2.1", 0) + clientes_por_hub.get("HUB 2.2", 0)
        pon3 = clientes_por_hub.get("HUB 3.1", 0) + clientes_por_hub.get("HUB 3.2", 0)
        if opcion == "Barras por PON":
            fig_bar = go.Figure(data=[
                go.Bar(x=["PON1", "PON2", "PON3"], y=[pon1, pon2, pon3], marker_color='lightskyblue')
            ])
            fig_bar.update_layout(
                xaxis_title="Puerto PON",
                yaxis_title="Cantidad de Clientes",
                showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    # Estado según corte
    if corte_activo and distancia_corte > 0:
        total_afectados = 0
        total_operativos = 0
        for i, nombre in enumerate(nombres):
            if nombre.startswith("HUB") and i < len(distancias):
                if distancias[i] > distancia_corte:
                    total_afectados += clientes_por_hub.get(nombre, 0)
                else:
                    total_operativos += clientes_por_hub.get(nombre, 0)

        st.markdown("### Estado de clientes según el corte")
        col1, col2 = st.columns(2)
        col1.metric("Clientes operativos", total_operativos)
        col2.metric("Clientes sin servicio", total_afectados)
