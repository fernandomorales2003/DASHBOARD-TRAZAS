import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

# Título superior de la página
st.markdown("## Dashboard OTDR - TRONCAL MZA-NORTE")

# Simular curvas limpias (sin ruido)
def generar_curva(distancia_km, nombre, eventos=[], base_atenuacion=0.25):
    pasos = 1000
    x = np.linspace(0, distancia_km, pasos)
    y = base_atenuacion * x

    # Aplicar eventos como caídas bruscas
    for evento in eventos:
        pos = int((evento['distancia'] / distancia_km) * pasos)
        y[pos:] -= evento['pérdida']

    return x, y

# Eventos reales (solo los de pérdida mayor a 0.30 dB se marcan)
eventos_2024 = [{'distancia': 10, 'pérdida': 0.25}, {'distancia': 25, 'pérdida': 0.35}, {'distancia': 40, 'pérdida': 0.20}]
eventos_2025 = [{'distancia': 10, 'pérdida': 0.25}, {'distancia': 25, 'pérdida': 0.60}, {'distancia': 40, 'pérdida': 0.45}]

# Generar curvas
x_2024, y_2024 = generar_curva(50, "2024/06", eventos_2024)
x_2025, y_2025 = generar_curva(50, "2025/06", eventos_2025)

# Fila superior
with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.markdown("### 🔷 TRONCAL MZA-NORTE - Comparación 2024/06 vs 2025/06 (1550 nm)")

        mostrar_2024 = st.checkbox("Mostrar curva 2024/06", value=True)
        mostrar_2025 = st.checkbox("Mostrar curva 2025/06", value=True)

        fig, ax = plt.subplots(figsize=(8, 4))
        if mostrar_2024:
            ax.plot(x_2024, y_2024, label="2024/06", color="blue")
            for e in eventos_2024:
                if e['pérdida'] > 0.30:
                    ax.plot(e['distancia'], 0.25*e['distancia'] - e['pérdida'], 'o', color='blue')

        if mostrar_2025:
            ax.plot(x_2025, y_2025, label="2025/06", color="red")
            for e in eventos_2025:
                if e['pérdida'] > 0.30:
                    ax.plot(e['distancia'], 0.25*e['distancia'] - e['pérdida'], 'o', color='red')

        ax.set_xlabel("Distancia (km)")
        ax.set_ylabel("Nivel de señal (dB)")
        ax.set_title("Curva OTDR - Comparación")
        ax.legend()
        ax.grid(True)
        ax.text(35, -5, "🔴 Eventos con pérdida > 0.30 dB marcados", fontsize=8)
        st.pyplot(fig)

# Tabla de eventos debajo
st.markdown("### 📊 Tabla de Eventos Detectados")

def tabla_eventos(nombre, eventos):
    filtrados = [e for e in eventos if e['pérdida'] > 0.30]
    df = pd.DataFrame(filtrados)
    df['Curva'] = nombre
    return df[['Curva', 'distancia', 'pérdida']]

df_2024 = tabla_eventos("2024/06", eventos_2024)
df_2025 = tabla_eventos("2025/06", eventos_2025)

df_final = pd.concat([df_2024, df_2025])
df_final.columns = ['Curva', 'Distancia (km)', 'Pérdida (dB)']
st.dataframe(df_final, use_container_width=True)

# Presupuesto de pérdidas
st.markdown("### 🧮 Presupuesto de Pérdidas Estimado")

def calcular_presupuesto(eventos, conector_ini=0.5, conector_fin=0.5):
    perdidas_eventos = sum(e['pérdida'] for e in eventos)
    perdida_total = perdidas_eventos + conector_ini + conector_fin
    return round(perdida_total, 2)

col_p1, col_p2 = st.columns(2)
with col_p1:
    st.metric("Total Pérdidas 2024/06", f"{calcular_presupuesto(eventos_2024)} dB")
with col_p2:
    st.metric("Total Pérdidas 2025/06", f"{calcular_presupuesto(eventos_2025)} dB")

