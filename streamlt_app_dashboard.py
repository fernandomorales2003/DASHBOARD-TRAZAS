import streamlit as st
import pandas as pd
import pydeck as pdk
import math

# Datos de ejemplo para dos trazas
trazas = {
    "TR-S-DER-02": {
        "coords": [
            (-32.8902, -68.8448),
            (-32.8912, -68.8450),
            (-32.8925, -68.8460),
            (-32.8935, -68.8465),
            (-32.8945, -68.8470)
        ],
        "distancia_corte": 3285.0
    },
    "TR1-SUR": {
        "coords": [
            (-32.8900, -68.8400),
            (-32.8910, -68.8410),
            (-32.8920, -68.8420),
            (-32.8930, -68.8430),
            (-32.8940, -68.8440)
        ],
        "distancia_corte": 0  # sin corte
    }
}

st.set_page_config(layout="wide")
st.title("📍 Mapa de Corte de Fibra Óptica")

# Selector de traza
traza_seleccionada = st.selectbox("Seleccioná la traza", list(trazas.keys()))

coords = trazas[traza_seleccionada]["coords"]
distancia_corte = trazas[traza_seleccionada]["distancia_corte"]

# Cálculo de distancia entre puntos
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radio de la Tierra en metros
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

distancias = [0]
total = 0
for i in range(1, len(coords)):
    d = haversine(coords[i-1][0], coords[i-1][1], coords[i][0], coords[i][1])
    total += d
    distancias.append(total)

data = pd.DataFrame({
    "lat": [lat for lat, lon in coords],
    "lon": [lon for lat, lon in coords],
    "distancia": distancias
})
data["dist_str"] = data["distancia"].apply(lambda x: f"{x:.1f} m")

# Agregar punto de corte si hay
if distancia_corte > 0:
    for i in range(1, len(distancias)):
        if distancias[i] >= distancia_corte:
            ratio = ((distancia_corte - distancias[i-1]) /
                     (distancias[i] - distancias[i-1]))
            lat_interp = coords[i-1][0] + ratio * (coords[i][0] - coords[i-1][0])
            lon_interp = coords[i-1][1] + ratio * (coords[i][1] - coords[i-1][1])
            marcador_corte = {
                "lat": lat_interp,
                "lon": lon_interp,
                "label": "CORTE DETECTADO A POSICIÓN GPS",
                "dist_str": f"{distancia_corte:.1f} m"
            }
            data = pd.concat([data, pd.DataFrame([marcador_corte])], ignore_index=True)
            break

# Capa de línea y capa de puntos
linea = pdk.Layer(
    "LineLayer",
    data=data,
    get_source_position='[lon, lat]',
    get_target_position='[lon, lat]',
    get_color='[0, 0, 255]',
    get_width=4,
    pickable=True
)

puntos = pdk.Layer(
    "ScatterplotLayer",
    data=data,
    get_position='[lon, lat]',
    get_fill_color='[255, 255, 0]' if distancia_corte > 0 else '[0, 200, 0]',
    get_radius=20,
    pickable=True
)

view_state = pdk.ViewState(
    latitude=data["lat"].mean(),
    longitude=data["lon"].mean(),
    zoom=15,
    pitch=0
)

tooltip = {
    "html": "<b>{label}</b><br>Distancia: {dist_str}",
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}

# Mostrar el mapa
st.pydeck_chart(pdk.Deck(
    layers=[linea, puntos],
    initial_view_state=view_state,
    tooltip=tooltip
))

# --- Agregado personalizado para TR1-SUR ---
if traza_seleccionada == "TR1-SUR":
    st.markdown("### Distribución de Clientes")
    col1, col2 = st.columns(2)
    col1.metric("Clientes operativos", "750")
    col2.metric("Cliente", "WISP")

# --- Indicadores adicionales solo para TR-S-DER-02 ---
if traza_seleccionada == "TR-S-DER-02":
    st.markdown("### Indicadores del Corte")
    col1, col2, col3 = st.columns(3)
    col1.metric("Distancia del corte", f"{distancia_corte:.1f} m")
    col2.metric("Latitud", f"{marcador_corte['lat']:.5f}")
    col3.metric("Longitud", f"{marcador_corte['lon']:.5f}")
