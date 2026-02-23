from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
# Importamos la Base desde models para que SQLAlchemy sepa qué tablas crear
from .models import Base

# Definimos la ruta de la base de datos 
DB_DIR = Path(r'C:\Users\carlo\OneDrive\finanzas_app_data')
if not DB_DIR.exists():
    DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "finanzas.db"
database_url = f'sqlite:///{DB_PATH.as_posix()}'  
engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
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

def update_ahorro(banco, bolsillo, monto_nuevo):
    from .models import Ahorro
    db = SessionLocal()
    # Buscamos si ya existe ese bolsillo en ese banco
    item = db.query(Ahorro).filter_by(banco=banco, bolsillo=bolsillo).first()
    
    if item:
        item.monto = monto_nuevo
    else:
        item = Ahorro(banco=banco, bolsillo=bolsillo, monto=monto_nuevo)
        db.add(item)
    
    db.commit()
    db.close()

def get_ahorros():
    from .models import Ahorro
    db = SessionLocal()
    res = db.query(Ahorro).all()
    db.close()
    return res

def get_all_ahorros():
    from .models import Ahorro
    db = SessionLocal()
    res = db.query(Ahorro).all()
    db.close()
    return [{"banco": a.banco, "bolsillo": a.bolsillo, "monto": a.monto} for a in res]