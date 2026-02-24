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

class Ahorro(Base):
    __tablename__ = 'ahorros'
    id = Column(Integer, primary_key=True)
    banco = Column(String, nullable=False)
    bolsillo = Column(String, nullable=False)
    monto = Column(Float, default=0.0)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CategoriaConfig(Base):
    __tablename__ = 'categorias_config'
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)