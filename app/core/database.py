import streamlit as st
from supabase import create_client, Client
import pandas as pd
import bcrypt 
from datetime import datetime

# Inicializar cliente de Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- FUNCIONES DE AUTENTICACIÓN ---

def crear_usuario(usuario, password):
    """Cifra la contraseña y crea un nuevo registro en la tabla usuarios."""
    # Generamos la huella digital (hash) de la contraseña
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        supabase.table("usuarios").insert({
            "usuario": usuario.lower().strip(), 
            "password_hash": hashed
        }).execute()
        return True
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        return False

def validar_usuario(usuario, password):
    """Busca al usuario y compara la contraseña ingresada con el hash guardado."""
    res = supabase.table("usuarios").select("password_hash").eq("usuario", usuario.lower().strip()).execute()
    
    if res.data:
        stored_hash = res.data[0]['password_hash']
        # Comparamos la contraseña con el hash cifrado
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True
    return False

# --- FUNCIONES DE GASTOS ---

def get_all_gastos(usuario):
    res = supabase.table("gastos").select("*").eq("usuario", usuario).order("id", desc=True).execute()
    return pd.DataFrame(res.data)

def save_gasto(monto, categoria, descripcion, usuario, banco, bolsillo):
    data_gasto = {
        "usuario": usuario,
        "monto": float(monto),
        "categoria": categoria,
        "descripcion": descripcion,
        "banco": banco,
        "bolsillo": bolsillo
    }
    supabase.table("gastos").insert(data_gasto).execute()

    # Lógica de resta automática
    res = supabase.table("ahorros").select("monto").eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()
    if res.data:
        nuevo_saldo = res.data[0]['monto'] - float(monto)
        supabase.table("ahorros").update({"monto": nuevo_saldo}).eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()

# --- FUNCIONES DE AHORROS ---

def get_all_ahorros(usuario):
    res = supabase.table("ahorros").select("*").eq("usuario", usuario).execute()
    return pd.DataFrame(res.data)

def update_ahorro(banco, bolsillo, monto, usuario):
    supabase.table("ahorros").delete().eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()
    data = {"usuario": usuario, "banco": banco, "bolsillo": bolsillo, "monto": float(monto)}
    supabase.table("ahorros").insert(data).execute()

# --- FUNCIONES DE FILTRADO ---

def get_unique_banks(usuario):
    res = supabase.table("ahorros").select("banco").eq("usuario", usuario).execute()
    if not res.data: return []
    return sorted(list(set([item['banco'] for item in res.data])))

def get_pockets_by_bank(usuario, banco):
    res = supabase.table("ahorros").select("bolsillo").eq("usuario", usuario).eq("banco", banco).execute()
    if not res.data: return []
    return sorted([item['bolsillo'] for item in res.data])

# --- FUNCIONES DE CATEGORÍAS ---

def get_config_categories(usuario):
    res = supabase.table("categorias_config").select("categoria").eq("usuario", usuario).execute()
    cats = [item['categoria'] for item in res.data]
    return cats if cats else ["Alimentos", "Transporte", "Gastos Personales"]

def add_config_category(nombre, usuario):
    supabase.table("categorias_config").insert({"usuario": usuario, "categoria": nombre}).execute()

def delete_config_category(nombre, usuario):
    supabase.table("categorias_config").delete().eq("usuario", usuario).eq("categoria", nombre).execute()