import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Asegurar que encuentre el core del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, get_all_ahorros, update_ahorro, 
    save_gasto, get_config_categories, add_config_category, 
    delete_config_category, get_unique_banks, get_pockets_by_bank
)

# Configuración de la página
st.set_page_config(page_title="Finanzas", layout="wide", page_icon="🏦")

# --- SIDEBAR / LOGIN ---
with st.sidebar:
    st.title("🏦 Finanzas Personales")
    user = st.text_input("Tu Usuario:", value="Invitado").strip().lower()
    
    st.divider()
    menu = st.radio("Sección Principal", ["📊 Mis Gastos", "💰 Mi Patrimonio", "⚙️ Configuración"])
    
    # --- BOTÓN DE DESCARGA CSV ---
    st.divider()
    st.subheader("📥 Exportar Datos")
    df_descarga = get_all_gastos(user)
    if not df_descarga.empty:
        csv = df_descarga.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Gastos (CSV)",
            data=csv,
            file_name=f'gastos_{user}.csv',
            mime='text/csv'
        )
    
    st.info("Desarrollado por Carlos Araújo. Datos en la nube con Supabase.")

# --- SECCIÓN GASTOS (CON INTEGRACIÓN BANCARIA) ---
if menu == "📊 Mis Gastos":
    st.header(f"Gestión de Gastos - {user.capitalize()}")
    
    # Obtenemos los bancos que el usuario tiene con dinero
    lista_bancos = get_unique_banks(user)
    
    if not lista_bancos:
        st.warning("⚠️ Para registrar gastos, primero crea un Banco y un Bolsillo con saldo en la sección 'Mi Patrimonio'.")
    else:
        with st.expander("➕ Registrar Nuevo Gasto (Descontar de Ahorros)"):
            cats = get_config_categories(user)
            with st.form("f_gasto", clear_on_submit=True):
                col1, col2 = st.columns(2)
                monto_g = col1.number_input("Monto ($)", min_value=0, value=0,step=1000,format="%d")
                cat_g = col2.selectbox("Categoría", options=cats)
                
                # --- SELECTBOXES DEPENDIENTES ---
                col_b1, col_b2 = st.columns(2)
                banco_sel = col_b1.selectbox("¿De qué Banco sale?", options=lista_bancos)
                
                # Cargamos bolsillos dinámicamente según el banco elegido
                pockets_disp = get_pockets_by_bank(user, banco_sel)
                bolsillo_sel = col_b2.selectbox("¿De qué Bolsillo?", options=pockets_disp)
                
                desc_g = st.text_input("Descripción (ej: Almuerzo)")

                enviar_gasto = st.form_submit_button("Guardar y Restar Saldo")
                
                if enviar_gasto:
                    if monto_g > 0 and desc_g:
                        save_gasto(monto_g, cat_g, desc_g, user, banco_sel, bolsillo_sel)
                        st.success(f"¡Gasto registrado! Se restaron ${monto_g:,.0f} de {banco_sel}")
                    else:
                        st.error("Ingresa un monto mayor a 0 y una descripción.")

    # Visualización de Gastos
    df_g = get_all_gastos(user)
    if not df_g.empty:
        st.metric("Total Gastado", f"${df_g['monto'].sum():,.0f}")
        
        col_chart, col_table = st.columns([1, 1])
        
        with col_chart:
            # --- GRÁFICA DE PASTEL ---
            st.subheader("Distribución por Categoría")
            fig_pie = px.pie(
                df_g, 
                values='monto', 
                names='categoria', 
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with col_table:
            # --- HISTORIAL  ---
            st.subheader("Historial de Movimientos")
            
            columnas_principales = ['monto', 'categoria', 'descripcion']
            otras_columnas = [c for c in df_g.columns if c not in columnas_principales]
            
            df_reordenado = df_g[columnas_principales + otras_columnas]
            
            # Limpiamos columnas internas para la vista
            columnas_a_quitar = ['id', 'usuario']
            for col in columnas_a_quitar:
                if col in df_reordenado.columns:
                    df_reordenado = df_reordenado.drop(columns=[col])
            
            st.dataframe(df_reordenado.sort_values(by='fecha', ascending=False) if 'fecha' in df_reordenado.columns else df_reordenado, use_container_width=True)

# --- SECCIÓN PATRIMONIO (CON RANKING) ---
elif menu == "💰 Mi Patrimonio":
    st.header(f"Estado de Ahorros - {user.capitalize()}")
    
    df_ah = get_all_ahorros(user)
    
    if not df_ah.empty:
        # --- RANKING DE BANCOS (MAYOR A MENOR) ---
        st.subheader("🏆 Saldo Total por Banco")
        resumen_bancos = df_ah.groupby('banco')['monto'].sum().sort_values(ascending=False)
        
        # Mostramos el ranking en columnas pequeñas
        cols_ranking = st.columns(len(resumen_bancos) if len(resumen_bancos) < 4 else 4)
        for i, (b_name, b_monto) in enumerate(resumen_bancos.items()):
            cols_ranking[i % 4].metric(b_name, f"${b_monto:,.0f}")
        
        st.divider()
        
        # Gráficos de Patrimonio
        col_ah1, col_ah2 = st.columns([1,1])
        with col_ah1:
            st.subheader("Distribución Bancaria")
            fig_sun = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto', 
                                  color='monto', color_continuous_scale='RdYlGn')
            st.plotly_chart(fig_sun, use_container_width=True)
        with col_ah2:
            st.subheader("Detalle de Cuentas")
            st.table(df_ah[['banco', 'bolsillo', 'monto']].sort_values(by='monto', ascending=False))
    
    # Formulario para actualizar o crear bolsillos
    with st.expander("📝 Configurar / Actualizar Cuentas"):
        with st.form("f_ahorro_manual", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            b_manual = c1.text_input("Banco (ej: Nequi)")
            p_manual = c2.text_input("Bolsillo (ej: Ahorros)")
            m_manual = c3.number_input("Saldo Actual", min_value=0, value=0, step=1000, format="%d")
            if st.form_submit_button("Guardar Saldo"):
                if b_manual and p_manual:
                    update_ahorro(b_manual, p_manual, m_manual, user)
                    st.success("Saldo actualizado correctamente.")
                    st.rerun()

# --- SECCIÓN CONFIGURACIÓN ---
elif menu == "⚙️ Configuración":
    st.header("Categorías de Gastos")
    st.write("Personaliza las categorías que usas para clasificar tus salidas de dinero.")
    
    cats = get_config_categories(user)
    
    st.subheader("Tus Categorías")
    cols_cat = st.columns(3)
    for i, c in enumerate(cats):
        with cols_cat[i % 3]:
            st.info(f"**{c}**")
            if st.button(f"Eliminar {c}", key=f"del_{c}"):
                delete_config_category(c, user)
                st.rerun()
    
    st.divider()
    st.subheader("Agregar Nueva Categoría")
    with st.form("add_cat_form"):
        nueva_c = st.text_input("Nombre de la categoría")
        if st.form_submit_button("Añadir"):
            if nueva_c:
                add_config_category(nueva_c, user)
                st.rerun()