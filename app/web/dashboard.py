import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de ruta para encontrar el core del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.core.database import get_all_gastos, get_all_ahorros, update_ahorro

# Configuración visual de Streamlit
st.set_page_config(page_title="Monai Local - Mi Dashboard", layout="wide", page_icon="📉")

# --- ESTILOS ---
st.markdown("""<style> .main { background-color: #f5f7f9; } </style>""", unsafe_allow_html=True)

# --- NAVEGACIÓN LATERAL ---
with st.sidebar:
    st.title("🏦 Finanzas")
    seccion = st.radio("Menú Principal", ["📊 Gastos", "💰 Ahorros y Bancos"])
    st.divider()
    st.info("Todo procesado localmente con Llama 3.2")

# --- SECCIÓN: GASTOS ---
if seccion == "📊 Gastos":
    st.header("Análisis de Gastos")
    data = get_all_gastos()
    
    if not data:
        st.warning("No hay gastos registrados aún. Envía uno por WhatsApp (ej: 'Pizza 30k')")
    else:
        df = pd.DataFrame(data)
        total_gastos = df['monto'].sum()
        
        # Métricas principales
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Gasto Total", f"${total_gastos:,.2f}")
        col_m2.metric("Nº de Transacciones", len(df))
        
        st.divider()
        
        col_c1, col_c2 = st.columns([1, 1])
        
        with col_c1:
            st.subheader("Porcentajes por Categoría")
            df_cat = df.groupby('categoria')['monto'].sum().reset_index()
            fig_pie = px.pie(
                df_cat, values='monto', names='categoria',
                hole=0.5, color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_c2:
            st.subheader("Resumen Numérico")
            df_resumen = df_cat.copy()
            df_resumen['%'] = (df_resumen['monto'] / total_gastos * 100).map('{:.1f}%'.format)
            df_resumen['monto'] = df_resumen['monto'].map('${:,.2f}'.format)
            st.table(df_resumen)

        st.subheader("Historial Completo")
        st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)

# --- SECCIÓN: AHORROS ---
elif seccion == "💰 Ahorros y Bancos":
    st.header("Estado del Patrimonio")
    
    # Formulario para actualizar manualmente
    with st.expander("📝 Actualizar Saldo Manualmente"):
        with st.form("form_ahorro"):
            c1, c2, c3 = st.columns(3)
            bank = c1.text_input("Banco")
            pocket = c2.text_input("Bolsillo")
            amount = c3.number_input("Nuevo Saldo Total", min_value=0.0)
            if st.form_submit_button("Actualizar"):
                update_ahorro(bank, pocket, amount)
                st.success(f"Saldo de {pocket} en {bank} actualizado.")
                st.rerun()

    ahorros_data = get_all_ahorros()
    if not ahorros_data:
        st.info("Registra tus saldos bancarios para ver el análisis.")
    else:
        df_ah = pd.DataFrame(ahorros_data)
        total_ahorros = df_ah['monto'].sum()
        st.metric("Patrimonio Total", f"${total_ahorros:,.2f}")
        
        st.divider()
        
        col_a1, col_a2 = st.columns([1,1])
        
        with col_a1:
            st.subheader("Distribución Bancaria (Sunburst)")
            # Gráfico Sunburst: Banco (dentro) -> Bolsillo (fuera)
            fig_sun = px.sunburst(
                df_ah, path=['banco', 'bolsillo'], values='monto',
                color='banco', color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_sun, use_container_width=True)
            
        with col_a2:
            st.subheader("Detalle por Bolsillo")
            st.table(df_ah[['banco', 'bolsillo', 'monto']].sort_values(by='banco'))

# --- ZONA DE PELIGRO ---
st.sidebar.divider()
if st.sidebar.button("🗑️ Borrar Todos los Datos"):
    from app.core.database import engine
    from app.core.models import Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    st.sidebar.warning("Base de datos reiniciada.")
    st.rerun()