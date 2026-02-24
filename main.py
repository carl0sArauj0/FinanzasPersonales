import sys
import os
import signal

# 1. Configuración de Rutas 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from neonize.client import NewClient
from neonize.events import MessageEv
from app.core.database import init_db, save_gasto, update_ahorro
from app.core.parser import parse_expense

# 2. Inicializar Base de Datos en el Escritorio de Windows
print("Conectando con la base de datos en el Escritorio...")
init_db()

OWNER_PHONE = "+573025150186"  

def on_message(client: NewClient, event: MessageEv):
    try:
        chat_jid = event.Info.MessageSource.Chat
        jid_str = str(chat_jid)

        # --- FILTRO DE SEGURIDAD ABSOLUTO ---
        # Solo procesa si el mensaje viene de TU número específico
        if OWNER_PHONE not in jid_str:
            return 

        # Extraer texto
        msg = event.Message
        text = (msg.conversation or 
                (msg.extendedTextMessage and msg.extendedTextMessage.text) or 
                (msg.imageMessage and msg.imageMessage.caption) or "")

        if not text:
            return

        print(f"\n--- Mensaje Recibido: {text} ---")

        # Procesar con IA
        data = parse_expense(text)
        print(f"IA interpretó: {data}")

        if "error" in data: return

        tipo = data.get("tipo", "gasto")

        if tipo == "gasto":
            save_gasto(float(data['monto']), data['categoria'], data.get('descripcion', text))
            client.send_message(chat_jid, f"💸 Gasto guardado: ${data['monto']}")
        
        elif tipo == "ahorro":
            update_ahorro(data['banco'], data['bolsillo'], float(data['monto']))
            client.send_message(chat_jid, f"💰 Ahorro actualizado en {data['banco']}")

    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def main():
    # Ruta estilo WSL para el Escritorio de Windows
    DB_DIR = "/mnt/c/Users/carlo/OneDrive/Desktop/finanzas_app_data"
    session_path = os.path.join(DB_DIR, "session.db")
    
    print(f"Iniciando cliente de WhatsApp...")
    client = NewClient(session_path)
    
    # IMPORTANTE: Registrar el evento de escucha
    client.event(MessageEv)(on_message)
    
    print("✅ Bot activo. Escríbete algo en WhatsApp para probar.")
    client.connect()

if __name__ == "__main__":
    main()