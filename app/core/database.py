from sqlalchemy import create_all_engines, create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine('sqlite:///data/finanzas.db', echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_gasto(monto, categoria, descripcion):
    from .models import Gasto
    db = SessionLocal()
    nuevo_gasto = Gasto(monto=monto, categoria=categoria, descripcion=descripcion)
    db.add(nuevo_gasto)
    db.commit()
    db.refresh(nuevo_gasto)
    db.close()