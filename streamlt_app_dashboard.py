import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import random

st.set_page_config(layout="wide", page_title="Comparador Curvas OTDR")
st.title("📡 Comparador de Curvas OTDR - Enlace MZA-NORTE")

# Parámetros del enlace
distancia = 50.0
atenuacion_por_km = 0.21

# Generar eventos patrón
eventos_patron = {round((i + 1) * 4, 2): 0.15 for i in range(int(distancia // 4))}

# Eventos adicionales aleatorios
puntos_disponibles = np.round(np.linspace(1, distancia - 1, int(distancia - 1)), 2)
puntos_nuevos = random.sample(list(set(puntos_disponibles) - set(eventos_patron.keys())), 8)
eventos_extra = {round(p, 2): round(random.uniform(0.15, 0.75), 2) for p in puntos_nuevos}
eventos_2025 = dict(sorted({**eventos_patron, **eventos_extra}.items()))

# Función para curva OTDR
def generar_curva(at_km, eventos):
    x_ini = np.array([0.0, 0.005, 0.075])
    y_ini = np.array([0.0, 0.8, -0.25])
    x_fibra = np.linspace(0.075, distancia - 0.075, 1000)
    y_fibra = -at_km * x_fibra + y_ini[-1]
    for punto, perdida in eventos.items():
        idx = np.searchsorted(x_fibra, punto)
        y_fibra[idx:] -= perdida
    y_fin_base = y_fibra[-1]
    x_fin = np.array([distancia - 0.075 + 0.005, distancia - 0.075 + 0.010, distancia])
    y_fin = np.array([y_fin_base, y_fin_base + 0.8, y_fin_base - 0.5])
    return np.concatenate([x_ini, x_fibra, x_fin]), np.concatenate([y_ini, y_fibra, y_fin])

# Cálculos
at_total_2024 = round(atenuacion_por_km * distancia + sum(eventos_patron.values()), 2)
at_total_2025 = round(atenuacion_por_km * distancia + sum(eventos_2025.values()), 2)
porc_aumento = ((at_total_2025 - at_total_2024) / at_total_2024) * 100
evento_max = max(eventos_2025.items(), key=lambda x: x[1])
eventos_adicionales = len(eventos_2025) - len(eventos_patron)

# Función para mostrar indicadores
def mostrar_indicadores():
    st.metric("🔦 Atenuación Total", f"{at_total_2025:.2f} dB (+{porc_aumento:.1f}%)")
    st.metric("🚨 Mayor Evento", f"{evento_max[1]:.2f} dB", help=f"Ocurre en el km {evento_max[0]:.2f}")
    st.metric("🛠️ Cantidad de Eventos Mantenimiento", f"{eventos_adicionales}")
    st.markdown(f"**Atenuación Total 2024:** {at_total_2024:.2f} dB")
    st.markdown(f"**Atenuación Total 2025:** {at_total_2025:.2f} dB")

# Función para mostrar gráfico
def mostrar_grafico():
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    x_2024, y_2024 = generar_curva(atenuacion_por_km, eventos_patron)
    x_2025, y_2025 = generar_curva(atenuacion_por_km, eventos_2025)
    ax.plot(x_2024, y_2024, label="MZA-NORTE-2024-06")
    ax.plot(x_2025, y_2025, label="MZA-NORTE-2025-06")
    for punto in eventos_extra.keys():
        y_val = -atenuacion_por_km * punto - sum(v for k, v in eventos_2025.items() if k <= punto)
        ax.plot(punto, y_val, 'ro')
    ax.set_xlabel("Distancia (km)")
    ax.set_ylabel("Potencia (dB)")
    ax.grid(True, linewidth=0.5, alpha=0.5)
    ax.legend()
    st.pyplot(fig)

# Función para mostrar tabla
def mostrar_tabla():
    col_check1, col_check2 = st.columns(2)
    with col_check1:
        tabla_2024 = st.checkbox("Ver eventos 2024", value=False)
    with col_check2:
        tabla_2025 = st.checkbox("Ver eventos 2025", value=False)

    if tabla_2024 and tabla_2025:
        st.warning("Selecciona solo una tabla a la vez.")
    elif tabla_2024 or tabla_2025:
        eventos = eventos_patron if tabla_2024 else eventos_2025
        total_final = at_total_2024 if tabla_2024 else at_total_2025
        acumulado = 0
        tabla = []
        for i, (dist, att) in enumerate(sorted(eventos.items()), start=1):
            acumulado += att
            total = atenuacion_por_km * dist + acumulado
            tabla.append({
                "Nro Evento": i,
                "Distancia (km)": dist,
                "Pérdida (dB)": att,
                "Atenuación acumulada (dB)": round(total, 2)
            })
        tabla.append({
            "Nro Evento": "—",
            "Distancia (km)": distancia,
            "Pérdida (dB)": 0.0,
            "Atenuación acumulada (dB)": total_final
        })
        st.dataframe(pd.DataFrame(tabla), use_container_width=True)

# Función para aplicar borde
def seccion_con_borde(titulo, contenido_func):
    st.markdown(
        f"""<div style="border: 2px solid #0f256e; border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">""",
        unsafe_allow_html=True
    )
    with st.container():
        st.subheader(titulo)
        contenido_func()
    st.markdown("</div>", unsafe_allow_html=True)

# UI en primera columna
col1, _, _ = st.columns(3)
with col1:
    seccion_con_borde("📊 ANÁLISIS ENLACE MZA-NORTE", mostrar_indicadores)
    seccion_con_borde("📈 Curvas OTDR Comparativas", mostrar_grafico)
    seccion_con_borde("📋 Tabla de eventos", mostrar_tabla)
