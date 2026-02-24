import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Forzar a que encuentre la carpeta app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, get_all_ahorros, update_ahorro, 
    save_gasto, get_config_categories, add_config_category, delete_config_category
)

st.set_page_config(page_title="Finanzas Dashboard", layout="wide", page_icon="🏦")

# --- LOGIN / IDENTIFICACIÓN ---
with st.sidebar:
    st.title("🏦 Finanzas Dashboard")
    usuario_input = st.text_input("Tu Nombre/ID:", value="Invitado").strip().lower()
    
    st.divider()
    if usuario_input:
        seccion = st.radio("Menú", ["📊 Mis Gastos", "💰 Mis Ahorros", "⚙️ Configuración"])
    else:
        st.warning("Por favor ingresa un nombre.")
        st.stop()

# --- SECCIÓN: GASTOS ---
if seccion == "📊 Mis Gastos":
    st.header(f"Gastos de {usuario_input.capitalize()}")
    
    with st.expander("➕ Registrar Gasto Manual"):
        # Importante: pasar el usuario a la función
        categorias = get_config_categories(usuario_input)
        with st.form("f_gasto"):
            col1, col2 = st.columns(2)
            m = col1.number_input("Monto ($)", min_value=0.0, step=500.0)
            c = col2.selectbox("Categoría", options=categorias)
            d = st.text_input("Descripción (ej: Cine)")
            if st.form_submit_button("Guardar Gasto"):
                if m > 0 and d:
                    save_gasto(m, c, d, usuario_input)
                    st.success("¡Registrado!")
                    st.rerun()

    df = get_all_gastos(usuario_input)
    if not df.empty:
        st.metric("Total Gastado", f"${df['monto'].sum():,.2f}")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(df, values='monto', names='categoria', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader("Historial")
            st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)
    else:
        st.info("Aún no tienes gastos. ¡Agrega el primero!")

# --- SECCIÓN: AHORROS ---
elif seccion == "💰 Mis Ahorros":
    st.header(f"Ahorros de {usuario_input.capitalize()}")
    
    with st.expander("📝 Actualizar Saldo"):
        with st.form("f_ahorro"):
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Banco")
            p = c2.text_input("Bolsillo")
            m = c3.number_input("Monto", min_value=0.0)
            if st.form_submit_button("Actualizar Saldo"):
                update_ahorro(b, p, m, usuario_input)
                st.success("Saldo actualizado.")
                st.rerun()

    df_ah = get_all_ahorros(usuario_input)
    if not df_ah.empty:
        st.metric("Patrimonio", f"${df_ah['monto'].sum():,.2f}")
        fig = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay ahorros registrados.")

# --- SECCIÓN: CONFIGURACIÓN ---
elif seccion == "⚙️ Configuración":
    st.header("Tus Categorías")
    cats = get_config_categories(usuario_input)
    
    cols = st.columns(3)
    for i, cat in enumerate(cats):
        with cols[i % 3]:
            if st.button(f"Eliminar {cat}", key=f"del_{cat}"):
                delete_config_category(cat, usuario_input)
                st.rerun()
    
    st.divider()
    with st.form("add_cat"):
        n = st.text_input("Nombre de nueva categoría")
        if st.form_submit_button("Añadir"):
            if n:
                add_config_category(n, usuario_input)
                st.rerun()