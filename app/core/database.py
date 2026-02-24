from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from .models import Base
from .models import CategoriaConfig

# Definimos la ruta de la base de datos 
DB_DIR = "/mnt/c/Users/carlo/OneDrive/Desktop/finanzas_app_data"
DB_PATH = os.path.join(DB_DIR, "finanzas.db")
database_url = f'sqlite:////{DB_PATH}'  
engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    if not os.path.exists(DB_DIR):
        # Creamos la carpeta en el escritorio desde WSL
        os.makedirs(DB_DIR, exist_ok=True)
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

def get_config_categories():
    db = SessionLocal()
    # Si la tabla está vacía, podrías devolver unas por defecto
    cats = db.query(CategoriaConfig).all()
    db.close()
    if not cats:
        return ["Alimentos", "Transporte", "Gastos Personales"] # Por defecto
    return [c.nombre for c in cats]

def add_config_category(nombre):
    db = SessionLocal()
    nueva = CategoriaConfig(nombre=nombre)
    db.add(nueva)
    try:
        db.commit()
    except:
        db.rollback()
    db.close()

def delete_config_category(nombre):
    db = SessionLocal()
    cat = db.query(CategoriaConfig).filter_by(nombre=nombre).first()
    if cat:
        db.delete(cat)
        db.commit()
    db.close()