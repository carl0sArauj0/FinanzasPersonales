import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os
import bcrypt

# 1. Configuración de la página (DEBE SER LA PRIMERA INSTRUCCIÓN)
st.set_page_config(page_title="Finanzas Pro", layout="wide", page_icon="🏦")

# Asegurar que encuentre el core del proyecto
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app.core.database import (
    get_all_gastos, get_all_ahorros, update_ahorro, 
    save_gasto, get_config_categories, add_config_category, 
    delete_config_category, get_unique_banks, get_pockets_by_bank,
    validar_usuario, crear_usuario, delete_gasto, delete_ahorro
)

# -- Lógica de la sesión --
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
    st.session_state['user'] = ""

# -- Pantalla de login -- 
def login_screen():
    st.title("🔐 Bienvenido a tu Dashboard de Finanzas Personales")
    tab1, tab2 = st.tabs(["Iniciar Sesión", "Registrarse"])

    with tab1:
        with st.form("login_form"):
            u = st.text_input("Usuario").lower().strip()
            p = st.text_input("Contraseña", type="password")
            if st.form_submit_button("Entrar"):
                if validar_usuario(u, p):
                    st.session_state['authenticated'] = True
                    st.session_state['user'] = u
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos")

    with tab2:
        st.info("Crea una cuenta para empezar a trackear tus finanzas.")
        with st.form("register_form", clear_on_submit=True):
            new_u = st.text_input("Nuevo Usuario").lower().strip()
            new_p = st.text_input("Nueva Contraseña", type="password")
            confirm_p = st.text_input("Confirmar Contraseña", type="password")
            
            if st.form_submit_button("Crear Cuenta"):
                if not new_u:
                    st.error("❌ El nombre de usuario no puede estar vacío.")
                elif new_p != confirm_p:
                    st.error("❌ Las contraseñas no coinciden.")
                elif len(new_p) < 4:
                    st.error("❌ La contraseña debe tener al menos 4 caracteres.")
                else:
                    if crear_usuario(new_u, new_p):
                        st.success(f"✅ ¡Cuenta '{new_u}' creada! Ahora puedes iniciar sesión.")
                    else:
                        st.error("❌ El usuario ya existe o hubo un error en el servidor.")

# -- Cuerpo de la app --
if not st.session_state['authenticated']:
    login_screen()
else:
    user = st.session_state['user']

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👤 Hola, {user.capitalize()}")
        if st.button("Cerrar Sesión"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = ""
            st.rerun()
            
        st.divider()
        menu = st.radio("Sección Principal", ["📊 Mis Gastos", "💰 Mi Patrimonio", "⚙️ Configuración"])
    
        # --- BOTÓN DE DESCARGA CSV ---
        st.divider()
        st.subheader("📥 Exportar Datos")
        df_descarga = get_all_gastos(user)
        if not df_descarga.empty:
            csv_data = df_descarga.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Gastos (CSV)",
                data=csv_data,
                file_name=f'gastos_{user}.csv',
                mime='text/csv'
            )
        else:
            st.caption("No hay datos para descargar.")
        
        st.info("Desarrollado por Carlos Araújo.")

    # --- SECCIÓN GASTOS ---
    if menu == "📊 Mis Gastos":
        st.header(f"Gestión de Gastos")
        
        lista_bancos = get_unique_banks(user)
        
        if not lista_bancos:
            st.warning("⚠️ Primero crea un Banco y un Bolsillo con saldo en 'Mi Patrimonio'.")
        else:
            with st.expander("➕ Registrar Nuevo Gasto"):
                cats = get_config_categories(user)
                with st.form("f_gasto", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    monto_g = col1.number_input("Monto ($)", min_value=0, value=0, step=1000, format="%d")
                    cat_g = col2.selectbox("Categoría", options=cats)
                    
                    col_b1, col_b2 = st.columns(2)
                    banco_sel = col_b1.selectbox("¿De qué Banco sale?", options=lista_bancos)
                    pockets_disp = get_pockets_by_bank(user, banco_sel)
                    bolsillo_sel = col_b2.selectbox("¿De qué Bolsillo?", options=pockets_disp)
                    
                    desc_g = st.text_input("Descripción")
                    
                    if st.form_submit_button("Guardar y Restar Saldo"):
                        if monto_g > 0 and desc_g:
                            save_gasto(monto_g, cat_g, desc_g, user, banco_sel, bolsillo_sel)
                            st.success(f"¡Registrado! Se restaron ${monto_g:,.0f} de {banco_sel}")
                            st.rerun()
                        else:
                            st.error("Monto y descripción obligatorios.")

        # Visualización de Gastos
        df_g = get_all_gastos(user)
        if not df_g.empty:
            st.metric("Total Gastado", f"${df_g['monto'].sum():,.0f}")
            col_chart, col_table = st.columns([1, 1])
            
            with col_chart:
                st.subheader("Distribución")
                fig_pie = px.pie(df_g, values='monto', names='categoria', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_table:
                st.subheader("Historial")
                df_view = df_g.drop(columns=['id', 'usuario'], errors='ignore')
                st.dataframe(df_view.sort_values(by='fecha', ascending=False) if 'fecha' in df_view.columns else df_view, use_container_width=True)

            # --- GESTIONAR BORRADO (Dentro de la sección de gastos) ---
            st.divider()
            st.subheader("🗑️ Gestionar Movimientos")
            with st.expander("Eliminar un gasto específico"):
                opciones_borrar = {
                    f"ID: {row['id']} | ${row['monto']:,.0f} | {row['descripcion']}": row['id'] 
                    for _, row in df_g.iterrows()
                }
                seleccion = st.selectbox("Selecciona el gasto que deseas eliminar:", options=list(opciones_borrar.keys()))
                id_seleccionado = opciones_borrar[seleccion]
                
                st.warning(f"⚠️ **Atención:** Si eliminas este gasto, se devolverá el dinero a tu cuenta.")
                
                if st.button("Confirmar Eliminación", type="primary"):
                    if delete_gasto(id_seleccionado, user):
                        st.success("✅ Gasto eliminado y saldo restaurado.")
                        st.rerun()
                    else:
                        st.error("Error al eliminar.")

    # --- SECCIÓN PATRIMONIO ---
    elif menu == "💰 Mi Patrimonio":
        st.header(f"Estado de Ahorros")
        df_ah = get_all_ahorros(user)
    
        if not df_ah.empty:
            st.subheader("🏆 Saldo Total por Banco")
            resumen_bancos = df_ah.groupby('banco')['monto'].sum().sort_values(ascending=False)
            cols_ranking = st.columns(len(resumen_bancos) if len(resumen_bancos) < 4 else 4)
            for i, (b_name, b_monto) in enumerate(resumen_bancos.items()):
                cols_ranking[i % 4].metric(b_name, f"${b_monto:,.0f}")
            
            st.divider()
            col_ah1, col_ah2 = st.columns([1,1])
            with col_ah1:
                st.subheader("Distribución")
                fig_sun = px.sunburst(df_ah, path=['banco', 'bolsillo'], values='monto', color='monto', color_continuous_scale='RdYlGn')
                st.plotly_chart(fig_sun, use_container_width=True)
            with col_ah2:
                st.subheader("Detalle de Cuentas")
                st.table(df_ah[['banco', 'bolsillo', 'monto']].sort_values(by='monto', ascending=False))

            # BORRAR CUENTA / BOLSILLO ---
            st.divider()
            with st.expander("🗑️ Eliminar Cuenta / Bolsillo"):
                dict_ah_borrar = {
                    f"{row['banco']} - {row['bolsillo']} (${row['monto']:,.0f})": row['id'] 
                    for _, row in df_ah.iterrows()
                }
                sel_ah = st.selectbox("Selecciona la cuenta a eliminar:", options=list(dict_ah_borrar.keys()))
                id_ah_sel = dict_ah_borrar[sel_ah]
                
                st.warning("⚠️ **Atención:** Esto eliminará el registro del saldo. No afectará el historial de gastos pasados.")
                
                if st.button("Confirmar Eliminación de Cuenta", type="primary"):
                    if delete_ahorro(id_ah_sel, user):
                        st.success("✅ Cuenta eliminada correctamente.")
                        st.rerun()
                    else:
                        st.error("Error al eliminar la cuenta.")
    
        with st.expander("📝 Configurar / Actualizar Cuentas"):
            with st.form("f_ahorro_manual", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                b_manual = c1.text_input("Banco").strip().title()
                p_manual = c2.text_input("Bolsillo").strip().title()
                m_manual = c3.number_input("Saldo Actual", min_value=0, value=0, step=1000, format="%d")
                
                if st.form_submit_button("Guardar Saldo"):
                    if b_manual and p_manual:
                        update_ahorro(b_manual, p_manual, m_manual, user)
                        st.success("Saldo actualizado.")
                        st.rerun()
                    else:
                        st.error("Debes llenar Banco y Bolsillo.")

    # --- SECCIÓN CONFIGURACIÓN ---
    elif menu == "⚙️ Configuración":
        st.header("Categorías de Gastos")
        cats = get_config_categories(user)
        
        cols_cat = st.columns(3)
        for i, c in enumerate(cats):
            with cols_cat[i % 3]:
                st.info(f"**{c}**")
                if st.button(f"Eliminar {c}", key=f"del_{c}"):
                    delete_config_category(c, user)
                    st.rerun()
        
        st.divider()
        with st.form("add_cat_form", clear_on_submit=True):
            nueva_c = st.text_input("Nombre de la categoría")
            if st.form_submit_button("Añadir"):
                if nueva_c:
                    add_config_category(nueva_c, user)
                    st.rerun()