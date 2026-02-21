from sqlalchemy import Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Gasto(Base):
    __tablename__ = 'gastos'
    id = Column(Integer, primary_key=True)
    monto = Column(Float, nullable=False)
    categoria = Column(String)
    descripcion = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)