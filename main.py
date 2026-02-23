import logging
import signal
import sys
import os

# Aseguramos que Python vea la carpeta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neonize.client import NewClient
from neonize.events import MessageEv
from app.core.parser import parse_expense
from app.core.database import init_db, save_gasto, update_ahorro

# Inicializar Base de Datos al arrancar
init_db()

def on_message(client: NewClient, event: MessageEv):
    try:
        # --- FILTROS DE SEGURIDAD ---
        chat_jid = event.Info.MessageSource.Chat
        jid_str = str(chat_jid)

        # 1. Ignorar Grupos y Estados
        if "@g.us" in jid_str or "@broadcast" in jid_str:
            return

        # 2. Solo procesar mensajes que TÚ envías
        if not event.Info.MessageSource.IsFromMe:
            return

        # --- EXTRACCIÓN DE TEXTO ---
        msg = event.Message
        text = (msg.conversation or 
                (msg.extendedTextMessage and msg.extendedTextMessage.text) or 
                (msg.imageMessage and msg.imageMessage.caption) or 
                "")

        if not text:
            return

        print(f"\n--- Procesando Mensaje ---")
        print(f"Texto: {text}")

        # --- PROCESAMIENTO CON IA ---
        data = parse_expense(text)
        print(f"IA interpretó: {data}")

        if "error" in data:
            return

        # --- DECISIÓN DE LÓGICA ---
        tipo = data.get("tipo", "gasto") # Por defecto asume gasto

        if tipo == "gasto":
            monto = float(data.get('monto', 0))
            cat = data.get('categoria', 'Gastos personales')
            desc = data.get('descripcion', text)
            
            save_gasto(monto, cat, desc)
            
            respuesta = f"💸 *Gasto Registrado*\n💰 ${monto:,.0f}\n📁 {cat}\n📝 {desc}"
            client.send_message(chat_jid, respuesta)

        elif tipo == "ahorro":
            monto = float(data.get('monto', 0))
            banco = data.get('banco', 'Otros')
            bolsillo = data.get('bolsillo', 'Principal')
            
            update_ahorro(banco, bolsillo, monto)
            
            respuesta = f"💰 *Ahorro Actualizado*\n🏦 {banco}\n📦 {bolsillo}\n💵 Nuevo Saldo: ${monto:,.0f}"
            client.send_message(chat_jid, respuesta)

    except Exception as e:
        print(f"Error en on_message: {e}")

def main():
    # Usamos la misma carpeta del escritorio para la sesión de WhatsApp
    DB_DIR = r'C:\Users\carlo\OneDrive\Desktop\finanzas_app_data'
    
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)

    session_path = os.path.join(DB_DIR, "session.db")
    client = NewClient(session_path)
    
    client.event(MessageEv)(on_message)
    print("--- Dashboard Finanzas CONECTADO ---")
    client.connect()

if __name__ == "__main__":
    main()