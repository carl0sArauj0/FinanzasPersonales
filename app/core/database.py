from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Importamos la Base desde models para que SQLAlchemy sepa qué tablas crear
from .models import Base

# Definimos la ruta de la base de datos (relativa a la raíz del proyecto)
DB_PATH = "data/finanzas.db"
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Crea la carpeta data si no existe
    if not os.path.exists("data"):
        os.makedirs("data")
    # Crea las tablas definidas en models.py
    Base.metadata.create_all(bind=engine)

def save_gasto(monto, categoria, descripcion):
    from .models import Gasto
    db = SessionLocal()
    try:
        nuevo_gasto = Gasto(monto=monto, categoria=categoria, descripcion=descripcion)
        db.add(nuevo_gasto)
        db.commit()
        db.refresh(nuevo_gasto)
    except Exception as e:
        print(f"Error al guardar: {e}")
        db.rollback()
    finally:
        db.close()