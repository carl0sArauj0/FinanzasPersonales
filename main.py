import logging
import signal
import sys
import os

# Aseguramos que Python vea la carpeta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neonize.client import NewClient
from neonize.events import MessageEv  # Cambio de nombre aquí
from app.core.parser import parse_expense
from app.core.database import init_db, save_gasto

# Inicializar DB
init_db()

def on_message(client: NewClient, event: MessageEv):
    # Acceder al mensaje de forma segura
    message = event.Message
    chat_jid = event.Info.Chat
    
    # Extraer el texto del mensaje (puede venir de diferentes campos de WhatsApp)
    text = (
        message.conversation or 
        message.extendedTextMessage.text or 
        message.imageMessage.caption or 
        ""
    )

    if text:
        print(f"Procesando: {text}")
        
        # 1. Procesar con Ollama
        data = parse_expense(text)
        
        if data and "monto" in data and "error" not in data:
            # 2. Guardar en SQLite
            save_gasto(
                monto=float(data['monto']), 
                categoria=data['categoria'], 
                descripcion=data['descripcion']
            )
            
            # 3. Confirmar por WhatsApp
            respuesta = f"✅ *Gasto Anotado*\n💰 Monto: ${data['monto']}\n📁 Categoría: {data['categoria']}\n📝: {data['descripcion']}"
            client.send_message(chat_jid, respuesta)
        elif "error" not in data:
            # Si Ollama devolvió algo pero no es un gasto
            pass

def main():
    # Creamos la carpeta data si no existe para evitar errores
    if not os.path.exists("data"):
        os.makedirs("data")

    # 'data/session.db' guardará tus credenciales
    client = NewClient("data/session.db")

    # Registramos el evento corregido
    client.event(MessageEv)(on_message)

    print("--- BOT DE FINANZAS LOCAL ---")
    print("Escanea el código QR en la terminal...")
    
    client.connect()

if __name__ == "__main__":
    main()