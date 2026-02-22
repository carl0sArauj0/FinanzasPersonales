import sys
import os
import streamlit as st
import pandas as pd
import plotly.express as px 

# Configuración de ruta para encontrar 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.core.database import get_all_gastos

st.set_page_config(page_title="Monai Local - Finanzas", layout="wide")

st.title("📊 Análisis de Gastos Personales")

data = get_all_gastos()

if not data:
    st.warning("No hay datos todavía. ¡Envía un mensaje por WhatsApp!")
else:
    df = pd.DataFrame(data)
    total_general = df['monto'].sum()

    # --- MÉTRICAS PRINCIPALES ---
    st.metric("Gasto Total Acumulado", f"${total_general:,.2f}")
    st.divider()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Distribución por Porcentaje")
        # Agrupamos por categoría y sumamos
        df_cat = df.groupby('categoria')['monto'].sum().reset_index()
        
        # Creamos el gráfico de torta con Plotly
        fig = px.pie(
            df_cat, 
            values='monto', 
            names='categoria',
            hole=0.4, # Lo hace tipo "dona" (más moderno)
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        # Forzamos a que muestre el porcentaje y el valor
        fig.update_traces(textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Resumen de Categorías")
        # Calculamos el porcentaje manualmente para la tabla
        df_resumen = df_cat.copy()
        df_resumen['Porcentaje'] = (df_resumen['monto'] / total_general * 100).map('{:.1f}%'.format)
        df_resumen['Total ($)'] = df_resumen['monto'].map('${:,.2f}'.format)
        
        st.table(df_resumen[['categoria', 'Total ($)', 'Porcentaje']])

    # --- TABLA DE DETALLES ---
    st.divider()
    st.subheader("📝 Historial de Movimientos")
    st.dataframe(df.sort_values(by='fecha', ascending=False), use_container_width=True)