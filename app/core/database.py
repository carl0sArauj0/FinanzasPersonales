import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Conexión con Google Sheets (Asegúrate de configurar los Secrets en Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_gastos(usuario):
    try:
        df = conn.read(worksheet="gastos", ttl=0)
        return df[df['usuario'] == usuario]
    except:
        return pd.DataFrame(columns=["fecha", "usuario", "monto", "categoria", "descripcion"])

def save_gasto(monto, categoria, descripcion, usuario):
    df = conn.read(worksheet="gastos", ttl=0)
    nuevo_gasto = pd.DataFrame([{
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "usuario": usuario,
        "monto": float(monto),
        "categoria": categoria,
        "descripcion": descripcion
    }])
    updated_df = pd.concat([df, nuevo_gasto], ignore_index=True)
    conn.update(worksheet="gastos", data=updated_df)

def get_all_ahorros(usuario):
    try:
        df = conn.read(worksheet="ahorros", ttl=0)
        return df[df['usuario'] == usuario]
    except:
        return pd.DataFrame(columns=["usuario", "banco", "bolsillo", "monto"])

def update_ahorro(banco, bolsillo, monto, usuario):
    df = conn.read(worksheet="ahorros", ttl=0)
    # Filtrar para eliminar el registro viejo si existe y actualizarlo
    if not df.empty:
        df = df[~((df['usuario'] == usuario) & (df['banco'] == banco) & (df['bolsillo'] == bolsillo))]
    
    nuevo_ahorro = pd.DataFrame([{
        "usuario": usuario, 
        "banco": banco, 
        "bolsillo": bolsillo, 
        "monto": float(monto)
    }])
    updated_df = pd.concat([df, nuevo_ahorro], ignore_index=True)
    conn.update(worksheet="ahorros", data=updated_df)

def get_config_categories(usuario):
    try:
        df = conn.read(worksheet="config", ttl=0)
        user_cats = df[df['usuario'] == usuario]['nombre_categoria'].tolist()
        if not user_cats:
            return ["Alimentos", "Transporte", "Gastos Personales"]
        return user_cats
    except:
        return ["Alimentos", "Transporte", "Gastos Personales"]

def add_config_category(nombre, usuario):
    df = conn.read(worksheet="config", ttl=0)
    nueva = pd.DataFrame([{"usuario": usuario, "nombre_categoria": nombre}])
    updated_df = pd.concat([df, nueva], ignore_index=True)
    conn.update(worksheet="config", data=updated_df)

def delete_config_category(nombre, usuario):
    df = conn.read(worksheet="config", ttl=0)
    if not df.empty:
        updated_df = df[~((df['usuario'] == usuario) & (df['nombre_categoria'] == nombre))]
        conn.update(worksheet="config", data=updated_df)