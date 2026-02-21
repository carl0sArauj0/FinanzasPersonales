import streamlit as st
import pandas as pd
from app.core.database import get_all_gastos

st.set_page_config(page_title="Monai Local Dashboard", layout="wide")

st.title("📊 Mi Salud Financiera")

data = get_all_gastos() # Función que trae datos de SQLite
df = pd.DataFrame(data)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Gastos por Categoría")
    st.bar_chart(df.groupby('categoria')['monto'].sum())

with col2:
    st.subheader("Últimos Movimientos")
    st.table(df.tail(10))