import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Inicializar cliente de Supabase usando los Secrets
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# --- FUNCIONES DE GASTOS ---

def get_all_gastos(usuario):
    res = supabase.table("gastos").select("*").eq("usuario", usuario).order("id", desc=True).execute()
    return pd.DataFrame(res.data)

def save_gasto(monto, categoria, descripcion, usuario, banco, bolsillo):
    # 1. Registrar el gasto
    data_gasto = {
        "usuario": usuario,
        "monto": float(monto),
        "categoria": categoria,
        "descripcion": descripcion,
        "banco": banco,
        "bolsillo": bolsillo
    }
    supabase.table("gastos").insert(data_gasto).execute()

    # 2. Lógica de resta automática en Ahorros
    # Buscamos el saldo actual de ese bolsillo específico
    res = supabase.table("ahorros").select("monto").eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()
    
    if res.data:
        saldo_actual = res.data[0]['monto']
        nuevo_saldo = saldo_actual - float(monto)
        # Actualizamos el saldo restando el gasto
        supabase.table("ahorros").update({"monto": nuevo_saldo}).eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()

# --- FUNCIONES DE AHORROS ---

def get_all_ahorros(usuario):
    res = supabase.table("ahorros").select("*").eq("usuario", usuario).execute()
    return pd.DataFrame(res.data)

def update_ahorro(banco, bolsillo, monto, usuario):
    # Borramos si existe y creamos el nuevo registro (Upsert manual)
    supabase.table("ahorros").delete().eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()
    data = {"usuario": usuario, "banco": banco, "bolsillo": bolsillo, "monto": float(monto)}
    supabase.table("ahorros").insert(data).execute()

# --- NUEVAS FUNCIONES PARA LOS DROPDOWNS DINÁMICOS ---

def get_unique_banks(usuario):
    """Devuelve una lista única de los bancos que el usuario tiene registrados."""
    res = supabase.table("ahorros").select("banco").eq("usuario", usuario).execute()
    if not res.data:
        return []
    banks = list(set([item['banco'] for item in res.data]))
    return sorted(banks)

def get_pockets_by_bank(usuario, banco):
    """Devuelve los bolsillos asociados a un banco específico del usuario."""
    res = supabase.table("ahorros").select("bolsillo").eq("usuario", usuario).eq("banco", banco).execute()
    if not res.data:
        return []
    pockets = [item['bolsillo'] for item in res.data]
    return sorted(pockets)

# --- FUNCIONES DE CONFIGURACIÓN ---

def get_config_categories(usuario):
    res = supabase.table("categorias_config").select("categoria").eq("usuario", usuario).execute()
    cats = [item['categoria'] for item in res.data]
    return cats if cats else ["Alimentos", "Transporte", "Gastos Personales"]

def add_config_category(nombre, usuario):
    supabase.table("categorias_config").insert({"usuario": usuario, "categoria": nombre}).execute()

def delete_config_category(nombre, usuario):
    supabase.table("categorias_config").delete().eq("usuario", usuario).eq("categoria", nombre).execute()