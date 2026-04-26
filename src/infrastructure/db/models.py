from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from .database import Base
from datetime import datetime
class ProductModel(Base):
    __tablename__ = "products"
    #Identificador único del producto
    id = Column(Integer, primary_key=True, autoincrement=True,index=True)
    #Nombre del producto, no puede ser nulo
    name = Column(String(200), index=True, nullable=False)
    #Marca del producto, indexada para búsquedas rápidas
    brand=Column(String(100), index=True)
    #Categoría del producto, indexada para búsquedas rápidas
    category=Column(String(100), index=True)
    #Talla del producto, indexado para búsquedas rápidas
    size=Column(String(20), index=True)
    #Color del producto, indexado para búsquedas rápidas
    color=Column(String(50), index=True)
    #Precio del producto
    price = Column(Float)
    #Cantidad disponible en stock
    stock=Column(Integer)
    #Descripción del producto, puede ser texto largo
    description=Column(Text)

class ChatMemoryModel(Base):
    __tablename__ = "chat_memory"
    #Identificador único del mensaje en la conversación
    id = Column(Integer, primary_key=True, autoincrement=True,index=True)
    #Identificador de la sesión de chat, indexado para búsquedas rápidas
    session_id = Column(String(100), index=True)
    #Rol del mensaje, puede ser "user" o "assistant"
    role = Column(String(20), index=True)  # "user" o "assistant"
    #Contenido del mensaje, puede ser texto largo
    message = Column(Text)
    #Marca de tiempo del mensaje, con valor por defecto de la fecha y hora actual
    timestamp = Column(DateTime, default=datetime.utcnow)