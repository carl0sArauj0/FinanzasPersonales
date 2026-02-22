from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Importamos la Base desde models para que SQLAlchemy sepa qué tablas crear
from .models import Base

# Definimos la ruta de la base de datos 
DB_PATH = "data/finanzas.db"
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
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

def get_all_gastos():
    from .models import Gasto
    db = SessionLocal()
    try:
        # Obtenemos todos los gastos de la base de datos
        gastos = db.query(Gasto).all()
        # Los convertimos a una lista de diccionarios para que Pandas los entienda
        return [
            {
                "id": g.id,
                "monto": g.monto,
                "categoria": g.categoria,
                "descripcion": g.descripcion,
                "fecha": g.fecha
            }
            for g in gastos
        ]
    finally:
        db.close()