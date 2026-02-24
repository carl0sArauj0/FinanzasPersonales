import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Conexión oficial de Streamlit con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_all_gastos(usuario):
    try:
        df = conn.read(worksheet="gastos", ttl=0)
        return df[df['usuario'] == usuario]
    except:
        return pd.DataFrame(columns=["fecha", "usuario", "monto", "categoria", "descripcion"])

def save_gasto(monto, categoria, descripcion, usuario):
    try:
        df = conn.read(worksheet="gastos", ttl=0)
    except:
        df = pd.DataFrame(columns=["fecha", "usuario", "monto", "categoria", "descripcion"])
    
    nuevo = pd.DataFrame([{
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "usuario": usuario,
        "monto": float(monto),
        "categoria": categoria,
        "descripcion": descripcion
    }])
    df = pd.concat([df, nuevo], ignore_index=True)
    conn.update(worksheet="gastos", data=df)

def get_all_ahorros(usuario):
    try:
        df = conn.read(worksheet="ahorros", ttl=0)
        return df[df['usuario'] == usuario]
    except:
        return pd.DataFrame(columns=["usuario", "banco", "bolsillo", "monto"])

def update_ahorro(banco, bolsillo, monto, usuario):
    try:
        df = conn.read(worksheet="ahorros", ttl=0)
        if not df.empty:
            df = df[~((df['usuario'] == usuario) & (df['banco'] == banco) & (df['bolsillo'] == bolsillo))]
    except:
        df = pd.DataFrame(columns=["usuario", "banco", "bolsillo", "monto"])
        
    nuevo = pd.DataFrame([{"usuario": usuario, "banco": banco, "bolsillo": bolsillo, "monto": float(monto)}])
    df = pd.concat([df, nuevo], ignore_index=True)
    conn.update(worksheet="ahorros", data=df)

def get_config_categories(usuario):
    try:
        df = conn.read(worksheet="config", ttl=0)
        cats = df[df['usuario'] == usuario]['categoria'].tolist()
        return cats if cats else ["Alimentos", "Transporte", "Gastos Personales"]
    except:
        return ["Alimentos", "Transporte", "Gastos Personales"]

def add_config_category(nombre, usuario):
    try:
        df = conn.read(worksheet="config", ttl=0)
    except:
        df = pd.DataFrame(columns=["usuario", "categoria"])
    
    nueva = pd.DataFrame([{"usuario": usuario, "categoria": nombre}])
    df = pd.concat([df, nueva], ignore_index=True)
    conn.update(worksheet="config", data=df)

def delete_config_category(nombre, usuario):
    try:
        df = conn.read(worksheet="config", ttl=0)
        df = df[~((df['usuario'] == usuario) & (df['categoria'] == nombre))]
        conn.update(worksheet="config", data=df)
    except:
        pass