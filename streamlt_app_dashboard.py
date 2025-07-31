import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Fiber Route Mendoza", layout="wide")

# Coordenadas reales del centro sobre Av. San Martín
lat0 = -33.085064
lon0 = -68.46635

# Creamos puntos: DATACENTER, FUSIONES cada ~2 km, y OLT1 final
labels = ["DATACENTER", "FUSIÓN 1", "FUSIÓN 2", "FUSIÓN 3", "OLT1"]
puntos = []

# Los 3 primeros puntos sobre Av. San Martín hacia norte (~0.018° lat ≈ 2 km)
for i in range(3):
    puntos.append({
        "lat": lat0 + i * 0.018,
        "lon": lon0,
        "label": labels[i]
    })

# Luego giramos este (~2 km ≈ 0.018° longitud positiva), hasta completar 8 km total
for j in range(3,5):
    puntos.append({
        "lat": puntos[2]["lat"],
        "lon": lon0 + (j-2) * 0.018,
        "label": labels[j]
    })

df_puntos = pd.DataFrame(puntos)

# Construimos segmentos del recorrido
segmentos = []
for i in range(len(puntos)-1):
    segmentos.append({"coordinates": [
        [puntos[i]["lon"], puntos[i]["lat"]],
        [puntos[i+1]["lon"], puntos[i+1]["lat"]]
    ]})
df_lineas = pd.DataFrame(segmentos)

# LineLayer y PointLayer
line_layer = pdk.Layer(
    "LineLayer", data=df_lineas,
    get_source_position="coordinates[0]",
    get_target_position="coordinates[1]",
    get_color=[0, 200, 255], get_width=4)

point_layer = pdk.Layer(
    "ScatterplotLayer", data=df_puntos,
    get_position='[lon, lat]', get_color=[255, 0, 0],
    get_radius=50, pickable=True)

view_state = pdk.ViewState(
    latitude=lat0 + 0.018*1.5, longitude=lon0 + 0.018*0.5,
    zoom=12.5, pitch=0)

tooltip = {"html": "<b>{label}</b>", "style": {"backgroundColor": "white"}}

st.title("Simulación de recorrido de fibra sobre calles reales en Mendoza")
st.pydeck_chart(pdk.Deck(layers=[line_layer, point_layer],
                         initial_view_state=view_state,
                         tooltip=tooltip))
