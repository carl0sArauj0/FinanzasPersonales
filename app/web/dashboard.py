import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de ruta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, 
    get_all_ahorros, 
    update_ahorro, 
    save_gasto, # Importamos para el registro manual
    get_config_categories, 
    add_config_category, 
    delete_config_category
)

st.set_page_config(page_title="Finanzas Dashboard", layout="wide", page_icon="📉")

# --- NAVEGACIÓN ---
with st.sidebar:
    st.title("🏦 Finanzas")
    seccion = st.radio("Menú Principal", ["📊 Gastos", "💰 Ahorros y Bancos", "⚙️ Configuración"])
    st.divider()
    st.info("Agente IA: Activo solo para el administrador.")

# --- SECCIÓN: 📊 GASTOS ---
if seccion == "📊 Gastos":
    st.header("Gestión de Gastos")

    # --- FORMULARIO MANUAL (NUEVO) ---
    with st.expander("➕ Agregar Gasto Manualmente"):
        categorias_disponibles = get_config_categories()
        
        with st.form("form_gasto_manual"):
            col1, col2 = st.columns(2)
            monto = col1.number_input("Monto ($)", min_value=0.0, step=100.0)
            categoria = col2.selectbox("Categoría", options=categorias_disponibles)
            descripcion = st.text_input("Descripción (ej: Almuerzo ejecutivo)")
            
            if st.form_submit_button("Guardar Gasto"):
                if monto > 0 and descripcion:
                    save_gasto(monto, categoria, descripcion)
                    st.success("Gasto registrado correctamente.")
                    st.rerun()
                else:
                    st.error("Por favor ingresa un monto y una descripción.")

    st.divider()

    # --- VISUALIZACIÓN ---
    data = get_all_gastos()
    if not data:
        st.warning("No hay gastos registrados. Usa el formulario de arriba o WhatsApp.")
    else:
        df = pd.DataFrame(data)
        total_gastos = df['monto'].sum()
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Gasto Total", f"${total_gastos:,.2f}")
        col_m2.metric("Transacciones", len(df))
        
        st.divider()
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.subheader("Distribución (%)")
            df_cat = df.groupby('categoria')['monto'].sum().reset_index()
            fig = px.pie(df_cat, values='monto', names='categoria', hole=0.5, 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("Historial")
            st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)

# --- SECCIÓN: 💰 AHORROS ---
elif seccion == "💰 Ahorros y Bancos":
    st.header("Estado del Patrimonio")
    
    with st.expander("📝 Actualizar Saldo Bancario"):
        with st.form("form_ahorro"):
            c1, c2, c3 = st.columns(3)
            bank = c1.text_input("Banco")
            pocket = c2.text_input("Bolsillo")
            amount = c3.number_input("Saldo Actual", min_value=0.0)
            if st.form_submit_button("Actualizar Saldo"):
                if bank and pocket:
                    update_ahorro(bank, pocket, amount)
                    st.success("Saldo actualizado.")
                    st.rerun()

    ahorros_data = get_all_ahorros()
    if ahorros_data:
        df_ah = pd.DataFrame(ahorros_data)
        st.metric("Patrimonio Total", f"${df_ah['monto'].sum():,.2f}")
        fig_sun = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto')
        st.plotly_chart(fig_sun, use_container_width=True)
        st.table(df_ah)

# --- SECCIÓN: ⚙️ CONFIGURACIÓN ---
elif seccion == "⚙️ Configuración":
    st.header("Configuración de Categorías")
    
    categorias = get_config_categories()
    cols = st.columns(3)
    for i, cat in enumerate(categorias):
        with cols[i % 3]:
            st.info(f"**{cat}**")
            if st.button(f"Eliminar {cat}"):
                delete_config_category(cat)
                st.rerun()

    st.divider()
    with st.form("add_cat"):
        nueva = st.text_input("Nueva Categoría")
        if st.form_submit_button("Añadir"):
            if nueva:
                add_config_category(nueva)
                st.rerun()

# --- ZONA DE PELIGRO ---
if st.sidebar.button("🗑️ Resetear App"):
    from app.core.database import engine
    from app.core.models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    st.rerun()