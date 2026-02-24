import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Asegurar que encuentre el core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, get_all_ahorros, update_ahorro, 
    save_gasto, get_config_categories, add_config_category, delete_config_category
)

st.set_page_config(page_title="Monai Web", layout="wide", page_icon="🏦")

# --- LOGIN ---
with st.sidebar:
    st.title("🏦 Monai Web")
    user = st.text_input("Ingresa tu Nombre:", value="Invitado").strip().lower()
    st.divider()
    menu = st.radio("Ir a:", ["📊 Mis Gastos", "💰 Mis Ahorros", "⚙️ Configuración"])
    st.info("Tus datos se guardan en tiempo real.")

# --- SECCIÓN GASTOS ---
if menu == "📊 Mis Gastos":
    st.header(f"Gestión de Gastos - {user.capitalize()}")
    
    with st.expander("➕ Registrar Nuevo Gasto"):
        cats = get_config_categories(user)
        with st.form("f_gasto"):
            c1, c2 = st.columns(2)
            monto = c1.number_input("Monto ($)", min_value=0.0, step=1000.0)
            categoria = c2.selectbox("Categoría", options=cats)
            desc = st.text_input("Descripción")
            if st.form_submit_button("Guardar"):
                if monto > 0 and desc:
                    save_gasto(monto, categoria, desc, user)
                    st.success("¡Gasto guardado!")
                    st.rerun()

    df = get_all_gastos(user)
    if not df.empty:
        st.metric("Gasto Total", f"${df['monto'].sum():,.0f}")
        col1, col2 = st.columns([1, 1])
        with col1:
            fig = px.pie(df, values='monto', names='categoria', hole=0.4, title="Distribución")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.subheader("Últimos Movimientos")
            st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)

# --- SECCIÓN AHORROS ---
elif menu == "💰 Mis Ahorros":
    st.header(f"Patrimonio - {user.capitalize()}")
    
    with st.expander("📝 Actualizar Saldo"):
        with st.form("f_ahorro"):
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Banco")
            p = c2.text_input("Bolsillo")
            m = c3.number_input("Saldo Actual", min_value=0.0)
            if st.form_submit_button("Actualizar"):
                update_ahorro(b, p, m, user)
                st.success("Saldo actualizado.")
                st.rerun()

    df_ah = get_all_ahorros(user)
    if not df_ah.empty:
        st.metric("Total Ahorrado", f"${df_ah['monto'].sum():,.0f}")
        fig = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto')
        st.plotly_chart(fig, use_container_width=True)

# --- SECCIÓN CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.header("Tus Categorías Personalizadas")
    cats = get_config_categories(user)
    
    st.subheader("Actuales")
    cols = st.columns(3)
    for i, c in enumerate(cats):
        with cols[i % 3]:
            if st.button(f"🗑️ {c}", key=f"d_{c}"):
                delete_config_category(c, user)
                st.rerun()
    
    st.divider()
    st.subheader("Agregar Nueva")
    with st.form("a_cat"):
        n = st.text_input("Nombre de categoría")
        if st.form_submit_button("Añadir"):
            add_config_category(n, user)
            st.rerun()