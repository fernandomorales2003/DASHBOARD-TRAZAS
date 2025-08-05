import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("🔌 Dashboard de Red Óptica")

# --- Simulación de potencias HUBs ---
hubs = ["HUB 1.1", "HUB 1.2", "HUB 2.1", "HUB 2.2", "HUB 3.1", "HUB 3.2"]
potencias = np.random.uniform(-23, -17, len(hubs))
df_potencias = pd.DataFrame({"HUB": hubs, "Potencia (dBm)": potencias})

# --- Datos simulados para gráfica de barras ---
df = pd.DataFrame({
    "Enlace": ["TR1-NORTE", "TR1-SUR", "TR2-OESTE", "TR2-ESTE"],
    "Atenuación Certificada": [18.5, 19.2, 17.8, 18.0],
    "Atenuación Actual": [18.6, 27.2, 17.9, 18.1],
    "Estado": ["OK", "CORTE", "OK", "OK"]
})

corte_detectado = "CORTE" in df["Estado"].values

# --- Fila 1 ---
c1, c2, c3 = st.columns(3)

# Columna 1 - Fila 1: Indicadores
with c1:
    st.subheader("📈 Indicadores")
    total_ok = df[df["Estado"] == "OK"].shape[0]
    total_enlaces = df.shape[0]
    df["Diferencia"] = df["Atenuación Actual"] - df["Atenuación Certificada"]
    enlace_mas_degradado = df.loc[df["Diferencia"].idxmax()]
    m1, m2, m3 = st.columns(3)
    m1.metric("✅ Enlaces OK", f"{total_ok} de {total_enlaces}")
    m2.metric("🔻 Enlace más degradado", enlace_mas_degradado["Enlace"])
    m3.metric("📉 Variación potencia", f"{enlace_mas_degradado['Diferencia']:.2f} dB")

# Columna 2 - Fila 1: Gráfico de barras
with c2:
    st.subheader("📊 Atenuación Certificada vs Actual")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Certificada"], name="Certificada", marker_color="#00cc83"))
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Actual"], name="Actual", marker_color="#16865e"))
    fig.update_layout(barmode="group", yaxis_title="Atenuación (dB)", height=400)
    st.plotly_chart(fig, use_container_width=True)

# Columna 3 - Fila 1: Potencias Simuladas
with c3:
    st.subheader("📡 Potencias Simuladas de HUBs")
    st.dataframe(df_potencias, use_container_width=True)

# --- Fila 2 ---
c4, c5, c6 = st.columns(3)

with c4:
    st.subheader("🧪 Diagnóstico de Corte")
    if corte_detectado:
        st.error("🚨 Corte de fibra detectado en TR1-SUR")
    else:
        st.success("✅ Sin cortes detectados")

with c5:
    st.subheader("🗺️ Mapa Interactivo")
    st.markdown("(Aquí se insertaría un mapa con ubicación de nodos)")

with c6:
    st.subheader("📈 Gráficos de Distribución")
    st.markdown("(Aquí se mostraría un gráfico de clientes por zona)")

# --- Fila 3 ---
c7, c8, c9 = st.columns(3)

with c7:
    st.subheader("📋 Historial de Eventos")
    st.markdown("- 10:30 Corte detectado en TR1-SUR\n- 09:00 Revisión de HUB 1.1")

with c8:
    st.subheader("👥 Distribución de Clientes")
    if corte_detectado:
        st.metric("Clientes operativos", "0")
    else:
        st.metric("Clientes operativos", "750 WISP")

with c9:
    st.subheader("🔧 Tareas Programadas")
    st.markdown("- Mantenimiento HUB 3.2\n- Verificación señal TR2-OESTE")

