import sys
import os

# Esto busca la ruta de la raíz del proyecto y la agrega a Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import streamlit as st
import pandas as pd
from app.core.database import get_all_gastos

# Configuración de la página
st.set_page_config(page_title="Monai Local", layout="wide")

st.title("📊 Mi Dashboard de Finanzas")

# Obtener datos
data = get_all_gastos()

if not data:
    st.warning("Aún no hay gastos registrados. ¡Manda un mensaje por WhatsApp!")
else:
    df = pd.DataFrame(data)
    
    # Mostrar métricas rápidas
    total = df['monto'].sum()
    st.metric("Gasto Total", f"${total:,.2f}")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gastos por Categoría")
        st.bar_chart(df.groupby('categoria')['monto'].sum())
    
    with col2:
        st.subheader("Últimos Movimientos")
        st.dataframe(df.sort_values(by='fecha', ascending=False))