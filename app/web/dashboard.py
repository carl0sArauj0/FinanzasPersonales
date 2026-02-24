import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de ruta para encontrar el core del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Importamos las funciones de la base de datos (asegúrate de haberlas añadido a app/core/database.py)
from app.core.database import (
    get_all_gastos, 
    get_all_ahorros, 
    update_ahorro, 
    get_config_categories, 
    add_config_category, 
    delete_config_category
)

# Configuración visual de Streamlit
st.set_page_config(page_title="Monai Local - Finanzas", layout="wide", page_icon="📉")

# --- ESTILOS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; }
    .category-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e6e9ef;
        background-color: white;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏦 Monai Local")
    seccion = st.radio("Menú Principal", ["📊 Gastos", "💰 Ahorros y Bancos", "⚙️ Configuración"])
    st.divider()
    st.info("Esta herramienta procesa tus datos localmente para garantizar tu privacidad.")

# --- SECCIÓN: 📊 GASTOS ---
if seccion == "📊 Gastos":
    st.header("Análisis de Gastos")
    data = get_all_gastos()
    
    if not data:
        st.warning("No hay gastos registrados aún. Envía uno por WhatsApp (ej: 'Cena 50k')")
    else:
        df = pd.DataFrame(data)
        total_gastos = df['monto'].sum()
        
        # Métricas principales
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Gasto Total", f"${total_gastos:,.2f}")
        col_m2.metric("Nº de Transacciones", len(df))
        col_m3.metric("Promedio por Gasto", f"${(total_gastos/len(df)):,.2f}")
        
        st.divider()
        
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            st.subheader("Porcentajes por Categoría")
            # El gráfico se adapta automáticamente a las categorías que existan en los datos
            df_cat = df.groupby('categoria')['monto'].sum().reset_index()
            fig_pie = px.pie(
                df_cat, values='monto', names='categoria',
                hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_c2:
            st.subheader("Resumen Numérico")
            df_resumen = df_cat.copy()
            df_resumen['%'] = (df_resumen['monto'] / total_gastos * 100).map('{:.1f}%'.format)
            df_resumen['Total'] = df_resumen['monto'].map('${:,.2f}'.format)
            st.table(df_resumen[['categoria', 'Total', '%']])

        st.subheader("Historial Completo")
        st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)

# --- SECCIÓN: 💰 AHORROS Y BANCOS ---
elif seccion == "💰 Ahorros y Bancos":
    st.header("Estado del Patrimonio")
    
    with st.expander("📝 Actualizar Saldo Manualmente"):
        with st.form("form_ahorro"):
            c1, c2, c3 = st.columns(3)
            bank = c1.text_input("Banco (ej: Bancolombia, Nequi)")
            pocket = c2.text_input("Bolsillo (ej: Ahorros, Viajes)")
            amount = c3.number_input("Nuevo Saldo Total", min_value=0.0)
            if st.form_submit_button("Actualizar Saldo"):
                if bank and pocket:
                    update_ahorro(bank, pocket, amount)
                    st.success(f"Saldo de {pocket} en {bank} actualizado.")
                    st.rerun()
                else:
                    st.error("Por favor completa los campos de Banco y Bolsillo.")

    ahorros_data = get_all_ahorros()
    if not ahorros_data:
        st.info("Registra tus saldos bancarios para ver el análisis de tu patrimonio.")
    else:
        df_ah = pd.DataFrame(ahorros_data)
        total_ahorros = df_ah['monto'].sum()
        st.metric("Patrimonio Total", f"${total_ahorros:,.2f}")
        
        st.divider()
        
        col_a1, col_a2 = st.columns([1,1])
        
        with col_a1:
            st.subheader("Distribución Bancaria")
            fig_sun = px.sunburst(
                df_ah, path=['banco', 'bolsillo'], values='monto',
                color='banco', color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_sun, use_container_width=True)
            
        with col_a2:
            st.subheader("Detalle por Bolsillo")
            df_ah_disp = df_ah.copy()
            df_ah_disp['Monto'] = df_ah_disp['monto'].map('${:,.2f}'.format)
            st.table(df_ah_disp[['banco', 'bolsillo', 'Monto']].sort_values(by='banco'))

# --- SECCIÓN: ⚙️ CONFIGURACIÓN (NUEVA) ---
elif seccion == "⚙️ Configuración":
    st.header("Configuración de Categorías")
    st.write("Define las categorías que la IA utilizará para clasificar tus gastos.")

    # Listar categorías actuales
    categorias_actuales = get_config_categories()
    
    st.subheader("Tus Categorías de Gasto")
    
    if not categorias_actuales:
        st.info("No tienes categorías personalizadas. Se están usando las de por defecto.")
    
    # Mostrar categorías en cuadrícula con botón de eliminar
    cols = st.columns(3)
    for i, cat in enumerate(categorias_actuales):
        with cols[i % 3]:
            st.markdown(f"""<div class='category-card'><b>{cat}</b></div>""", unsafe_allow_html=True)
            if st.button(f"Eliminar {cat}", key=f"btn_{cat}"):
                delete_config_category(cat)
                st.rerun()

    st.divider()

    # Formulario para añadir nueva categoría
    st.subheader("Añadir Nueva Categoría")
    with st.form("add_category_form"):
        nueva_cat = st.text_input("Nombre de la categoría (ej: Salud, Mascotas, Regalos)")
        if st.form_submit_button("Registrar Categoría"):
            if nueva_cat:
                if nueva_cat in categorias_actuales:
                    st.error("Esta categoría ya existe.")
                else:
                    add_config_category(nueva_cat)
                    st.success(f"Categoría '{nueva_cat}' añadida correctamente.")
                    st.rerun()
            else:
                st.warning("Escribe un nombre para la categoría.")

# --- ZONA DE PELIGRO ---
st.sidebar.divider()
st.sidebar.subheader("Zona de Peligro")
if st.sidebar.button("🗑️ Borrar Todos los Datos"):
    if st.sidebar.checkbox("Confirmo que quiero borrar TODO"):
        from app.core.database import engine
        from app.core.models import Base
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.sidebar.warning("Base de datos reiniciada.")
        st.rerun()
    else:
        st.sidebar.info("Marca la casilla de confirmación primero.")