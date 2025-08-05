import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(layout="wide")
st.title("📡 Dashboard FTTx - MZA NORTE")

# ---------- PRIMERA FILA: Tabla de potencia por HUB ----------

# Simular valores entre -21 dBm y -18 dBm
hubs = ["HUB 1.1", "HUB 1.2", "HUB 2.1", "HUB 2.2", "HUB 3.1", "HUB 3.2"]
potencias = np.random.uniform(-21, -18, size=len(hubs)).round(2)

tabla_potencias = pd.DataFrame({
    "HUB": hubs,
    "Potencia (dBm)": potencias
})

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("🔌 Potencia por HUB")
    st.table(tabla_potencias)
with col2:
    st.empty()  # Reservado para contenido futuro
with col3:
    st.empty()  # Reservado para contenido futuro

# ---------- SEGUNDA FILA: Mapa ----------

# Simulación de coordenadas
data = pd.DataFrame({
    'lat': [-32.89, -32.91, -32.88],
    'lon': [-68.83, -68.82, -68.84],
    'cliente': ['Cliente A', 'Cliente B', 'Cliente C']
})

layer = pdk.Layer(
    'ScatterplotLayer',
    data,
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=100,
)

view_state = pdk.ViewState(
    latitude=data["lat"].mean(),
    longitude=data["lon"].mean(),
    zoom=12,
    pitch=0,
)

st.subheader("🗺️ Mapa de Clientes")
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state))

# ---------- TERCERA FILA: Gráficos ----------

col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Distribución de Clientes")
    st.bar_chart(pd.Series(np.random.randint(10, 100, size=6), index=hubs))

with col2:
    st.subheader("🏠 Distribución por HUB")
    st.bar_chart(pd.Series(np.random.randint(5, 50, size=6), index=hubs))
