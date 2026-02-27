import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Asegurar que encuentre el core del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, get_all_ahorros, update_ahorro, 
    save_gasto, get_config_categories, add_config_category, delete_config_category
)

# Configuración de la página
st.set_page_config(page_title="Finanzas Web Pro", layout="wide", page_icon="🏦")

# --- LOGIN / IDENTIFICACIÓN ---
with st.sidebar:
    st.title("🏦 Finanzas Personales")
    user = st.text_input("Ingresa tu Nombre:", value="Invitado").strip().lower()
    
    st.divider()
    menu = st.radio("Ir a:", ["📊 Mis Gastos", "💰 Mis Ahorros", "⚙️ Configuración"])
    
    st.divider()
    st.info("Desarrollado por Carlos Araújo. Datos procesados en la nube segura.")

    # --- SECCIÓN DE DESCARGA DE DATOS ---
    st.subheader("📥 Exportar Datos")
    df_para_descarga = get_all_gastos(user)
    
    if not df_para_descarga.empty:
        # Convertimos el DataFrame a CSV
        csv = df_para_descarga.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar mis Gastos (CSV)",
            data=csv,
            file_name=f'gastos_{user}.csv',
            mime='text/csv',
            help="Descarga un respaldo de todos tus gastos registrados"
        )
    else:
        st.caption("No hay datos para descargar aún.")

# --- SECCIÓN GASTOS ---
if menu == "📊 Mis Gastos":
    st.header(f"Gestión de Gastos - {user.capitalize()}")
    
    with st.expander("➕ Registrar Nuevo Gasto"):
        # Obtenemos las categorías personalizadas del usuario
        cats = get_config_categories(user)
        with st.form("f_gasto"):
            c1, c2 = st.columns(2)
            monto = c1.number_input("Monto ($)", min_value=0.0, step=1000.0)
            categoria = c2.selectbox("Categoría", options=cats)
            desc = st.text_input("Descripción (ej: Almuerzo)")
            
            if st.form_submit_button("Guardar Gasto"):
                if monto > 0 and desc:
                    save_gasto(monto, categoria, desc, user)
                    st.success("¡Gasto guardado exitosamente!")
                    st.rerun()
                else:
                    st.error("Por favor ingresa un monto válido y una descripción.")

    # Carga de datos
    df = get_all_gastos(user)
    
    if not df.empty:
        # Métricas
        st.metric("Total Gastado", f"${df['monto'].sum():,.0f}")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            fig = px.pie(df, values='monto', names='categoria', hole=0.4, 
                         title="Distribución por Categoría",
                         color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.subheader("Últimos Movimientos")
            # Ordenamos por fecha si la columna existe, si no por ID
            if 'fecha' in df.columns:
                df_sorted = df.sort_values(by='fecha', ascending=False)
            else:
                df_sorted = df
            st.dataframe(df_sorted, use_container_width=True)
    else:
        st.info("Aún no has registrado gastos. ¡Empieza usando el formulario de arriba!")

# --- SECCIÓN AHORROS ---
elif menu == "💰 Mis Ahorros":
    st.header(f"Patrimonio - {user.capitalize()}")
    
    with st.expander("📝 Actualizar Saldo Bancario"):
        with st.form("f_ahorro"):
            c1, c2, c3 = st.columns(3)
            b = c1.text_input("Banco (ej: Nequi)")
            p = c2.text_input("Bolsillo (ej: Ahorros)")
            m = c3.number_input("Saldo Actual", min_value=0.0, step=10000.0)
            if st.form_submit_button("Actualizar Saldo"):
                if b and p:
                    update_ahorro(b, p, m, user)
                    st.success("Saldo actualizado correctamente.")
                    st.rerun()
                else:
                    st.error("Completa Banco y Bolsillo.")

    df_ah = get_all_ahorros(user)
    if not df_ah.empty:
        st.metric("Total en Ahorros", f"${df_ah['monto'].sum():,.0f}")
        
        fig = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto',
                          title="Mapa de mi Dinero",
                          color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
        st.table(df_ah[['banco', 'bolsillo', 'monto']])
    else:
        st.info("Registra tus cuentas bancarias para ver el análisis de patrimonio.")

# --- SECCIÓN CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.header("Tus Categorías Personalizadas")
    st.write("Configura las opciones que aparecerán cuando registres un gasto.")
    
    cats = get_config_categories(user)
    
    st.subheader("Categorías Actuales")
    if not cats:
        st.write("No tienes categorías. Se usarán las de defecto.")
    else:
        cols = st.columns(3)
        for i, c in enumerate(cats):
            with cols[i % 3]:
                st.info(f"**{c}**")
                if st.button(f"Borrar {c}", key=f"del_{c}"):
                    delete_config_category(c, user)
                    st.rerun()
    
    st.divider()
    st.subheader("Agregar Nueva Categoría")
    with st.form("a_cat"):
        n = st.text_input("Nombre de la categoría (ej: Mascotas, Suscripciones)")
        if st.form_submit_button("Añadir Categoría"):
            if n:
                add_config_category(n, user)
                st.success(f"Categoría '{n}' añadida.")
                st.rerun()
            else:
                st.warning("Escribe un nombre.")