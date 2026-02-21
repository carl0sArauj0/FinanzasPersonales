import logging
import signal
import sys
import os

# Aseguramos que Python vea la carpeta 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from neonize.client import NewClient
from neonize.events import MessageEv
from app.core.parser import parse_expense
from app.core.database import init_db, save_gasto

# Inicializar DB
init_db()

def on_message(client: NewClient, event: MessageEv):
    try:
        # 1. Obtener el ID del chat (JID) de forma robusta
        # En versiones nuevas es: event.Info.MessageSource.Chat
        chat_jid = event.Info.MessageSource.Chat
        
        # 2. Extraer el texto del mensaje
        msg = event.Message
        text = ""
        
        if msg.conversation:
            text = msg.conversation
        elif msg.extendedTextMessage and msg.extendedTextMessage.text:
            text = msg.extendedTextMessage.text
        elif msg.imageMessage and msg.imageMessage.caption:
            text = msg.imageMessage.caption

        # Si no hay texto, salimos
        if not text:
            return

        print(f"\n--- Nuevo Mensaje ---")
        print(f"Texto: {text}")

        # 3. Procesar con Ollama (asegúrate de que phi3 esté corriendo)
        data = parse_expense(text)
        print(f"IA interpretó: {data}")

        if data and "monto" in data and "error" not in data:
            # 4. Guardar en SQLite
            save_gasto(
                monto=float(data['monto']), 
                categoria=data.get('categoria', 'Otros'), 
                descripcion=data.get('descripcion', text)
            )
            
            # 5. Confirmar por WhatsApp
            respuesta = f"✅ *Gasto Registrado*\n💰 Monto: ${data['monto']}\n📁 Cat: {data['categoria']}"
            client.send_message(chat_jid, respuesta)
            print("Respuesta enviada a WhatsApp")
            
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def main():
    if not os.path.exists("data"):
        os.makedirs("data")

    # Usamos session.db para guardar la conexión
    client = NewClient("data/session.db")
    client.event(MessageEv)(on_message)

    print("--- BOT DE FINANZAS LOCAL CONECTADO ---")
    print("Esperando mensajes...")
    
    client.connect()

if __name__ == "__main__":
    main()