from app.core.database import engine
from app.core.models import Base
import os

def reset():
    print("⚠️  Borrando todas las tablas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Base de datos vaciada.")
    
    # Opcional: Borrar el archivo de sesión de WhatsApp si quieres re-vincular
    # os.remove("data/session.db") 

if __name__ == "__main__":
    confirmacion = input("¿Estás seguro de que quieres borrar todos tus gastos? (s/n): ")
    if confirmacion.lower() == 's':
        reset()