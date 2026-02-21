import logging
import signal
import sys
from neonize.client import NewClient
from neonize.events import MessageEvent
from app.core.parser import parse_expense
from app.core.database import init_db, save_gasto

# Inicializar DB
init_db()

def on_message(client: NewClient, event: MessageEvent):
    # Evitar procesar mensajes de grupos o estados (opcional)
    text = event.message.conversation or event.message.extendedTextMessage.text
    sender = event.info.sender.user

    if text:
        print(f"Mensaje recibido de {sender}: {text}")
        
        # 1. Procesar con Ollama
        data = parse_expense(text)
        
        if data and "monto" in data:
            # 2. Guardar en SQLite
            save_gasto(
                monto=data['monto'], 
                categoria=data['categoria'], 
                descripcion=data['descripcion']
            )
            
            # 3. Confirmar por WhatsApp
            respuesta = f"✅ Registrado: ${data['monto']} en {data['categoria']} ({data['descripcion']})"
            client.send_message(event.info.chat, respuesta)
        else:
            # Opcional: responder si no se entendió
            pass

def main():
    # Creamos el cliente de WhatsApp
    # 'session.db' guardará tus credenciales para no escanear QR siempre
    client = NewClient("data/session.db")

    # Registramos el evento de mensaje
    client.event(MessageEvent)(on_message)

    print("Escanea el código QR en la terminal para vincular WhatsApp...")
    
    # Manejo de cierre limpio
    def signal_handler(sig, frame):
        print("\nCerrando bot...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)

    # Conectar
    client.connect()

if __name__ == "__main__":
    main()