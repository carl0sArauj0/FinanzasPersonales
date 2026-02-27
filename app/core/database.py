import streamlit as st
from supabase import create_client, Client
import pandas as pd

import streamlit as st
from supabase import create_client, Client
import pandas as pd

# Inicializar cliente de Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

def get_all_gastos(usuario):
    res = supabase.table("gastos").select("*").eq("usuario", usuario).execute()
    return pd.DataFrame(res.data)

def save_gasto(monto, categoria, descripcion, usuario):
    data = {
        "usuario": usuario,
        "monto": float(monto),
        "categoria": categoria,
        "descripcion": descripcion
    }
    supabase.table("gastos").insert(data).execute()

def get_all_ahorros(usuario):
    res = supabase.table("ahorros").select("*").eq("usuario", usuario).execute()
    return pd.DataFrame(res.data)

def update_ahorro(banco, bolsillo, monto, usuario):
    supabase.table("ahorros").delete().eq("usuario", usuario).eq("banco", banco).eq("bolsillo", bolsillo).execute()
    data = {"usuario": usuario, "banco": banco, "bolsillo": bolsillo, "monto": float(monto)}
    supabase.table("ahorros").insert(data).execute()

def get_config_categories(usuario):
    res = supabase.table("categorias_config").select("categoria").eq("usuario", usuario).execute()
    cats = [item['categoria'] for item in res.data]
    return cats if cats else ["Alimentos", "Transporte", "Gastos Personales"]

def add_config_category(nombre, usuario):
    supabase.table("categorias_config").insert({"usuario": usuario, "categoria": nombre}).execute()

def delete_config_category(nombre, usuario):
    supabase.table("categorias_config").delete().eq("usuario", usuario).eq("categoria", nombre).execute()