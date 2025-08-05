import streamlit as st
import pandas as pd
import random
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("📡 Dashboard OTDR - Enlace TR1-SUR")

# --- Fila Principal: 3 Columnas ---
col1, col2, col3 = st.columns(3)

# --- COLUMNA 1 ---
with col1:
    st.subheader("📌 Estado de Enlaces (KPI)")
    enlaces_info = {
        "MZA-FTTH-01": {"Tx": 0, "Rx_cert": -20},
        "MZA-FTTH-02": {"Tx": 5, "Rx_cert": -20},
        "MZA-CCTV-01": {"Tx": 0, "Rx_cert": -14},
        "MZA-WS-01": {"Tx": 3, "Rx_cert": -14},
        "MZA-WS-02": {"Tx": 3, "Rx_cert": -12},
        "MZA-WS-03": {"Tx": 3, "Rx_cert": -8},
    }

    def calcular_atenuaciones(tx, rx_cert):
        at_cert = tx - rx_cert
        variacion = random.uniform(-3, 3)
        at_actual = at_cert + variacion
        return round(at_cert, 2), round(at_actual, 2)

    def evaluar_estado(at_cert, at_actual):
        diferencia = at_actual - at_cert
        if diferencia <= 0.5:
            return "OK"
        elif diferencia <= 2:
            return "ADVERTENCIA"
        else:
            return "CRÍTICO"

    def estado_icono_color(estado):
        if estado == "OK":
            return "✅", "#2ecc71"
        elif estado == "ADVERTENCIA":
            return "⚠️", "#f1c40f"
        else:
            return "❌", "#e74c3c"

    datos = []
    for enlace, valores in enlaces_info.items():
        tx = valores["Tx"]
        rx = valores["Rx_cert"]
        at_cert, at_actual = calcular_atenuaciones(tx, rx)
        estado = evaluar_estado(at_cert, at_actual)
        datos.append({
            "Enlace": enlace,
            "Tx": tx,
            "Rx_cert": rx,
            "Atenuación Certificada": at_cert,
            "Atenuación Actual": at_actual,
            "Estado": estado
        })

    df = pd.DataFrame(datos)
    cols_kpi = st.columns(3)
    for i, row in enumerate(df.itertuples()):
        icono, color = estado_icono_color(row.Estado)
        with cols_kpi[i % 3]:
            st.markdown(f"""
                <div style="background-color:{color};
                            padding:20px;
                            border-radius:10px;
                            text-align:center;
                            color:white;
                            margin-bottom:20px;">
                    <h4>{row.Enlace}</h4>
                    <p style="font-size:24px;">{icono} <strong>{row.Estado}</strong></p>
                </div>
            """, unsafe_allow_html=True)

# --- COLUMNA 2 ---
with col2:
    # Fila 1: Gráfico de Barras
    st.subheader("📊 Atenuación Certificada vs Actual")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Certificada"], name="Certificada", marker_color="#00cc83"))
    fig.add_trace(go.Bar(x=df["Enlace"], y=df["Atenuación Actual"], name="Actual", marker_color="#16865e"))
    fig.update_layout(barmode="group", yaxis_title="Atenuación (dB)", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # Fila 2: Indicadores
    st.subheader("📈 Indicadores")
    total_ok = df[df["Estado"] == "OK"].shape[0]
    total_enlaces = df.shape[0]
    df["Diferencia"] = df["Atenuación Actual"] - df["Atenuación Certificada"]
    enlace_mas_degradado = df.loc[df["Diferencia"].idxmax()]
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Enlaces OK", f"{total_ok} de {total_enlaces}")
    c2.metric("🔻 Enlace más degradado", enlace_mas_degradado["Enlace"])
    c3.metric("📉 Variación potencia", f"{enlace_mas_degradado['Diferencia']:.2f} dB")

    # Fila 3: Distribución Clientes
    st.subheader("🏠 Distribución de Clientes")
    selected_enlace = st.selectbox("Seleccionar Troncal", df["Enlace"].tolist(), index=0)
    corte_detectado = df[df["Enlace"] == selected_enlace]["Estado"].values[0] == "CRÍTICO"

    if selected_enlace == "MZA-WS-01":
        total_clientes = 750 if not corte_detectado else 0
        tipo_cliente = "WISP"
    else:
        total_clientes = random.randint(200, 500) if not corte_detectado else 0
        tipo_cliente = "Residenciales"

    st.markdown(f"**Total de clientes operativos:** {total_clientes} ({tipo_cliente})")

# --- COLUMNA 3 ---
with col3:
    st.subheader("🛠️ Información Adicional")
    st.info("Aquí podés incluir alertas, trazas OTDR, eventos futuros u otros datos.")
