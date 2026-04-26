from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para transferir datos de productos entre capas.

    Pydantic valida automáticamente los tipos y ejecuta los
    field_validators antes de crear el objeto.

    Attributes:
        id (Optional[int]): Identificador del producto (None si es nuevo).
        name (str): Nombre del producto.
        brand (str): Marca del producto.
        category (str): Categoría (Running, Casual, Formal).
        size (str): Talla del zapato.
        color (str): Color del producto.
        price (float): Precio en dólares, debe ser mayor a 0.
        stock (int): Unidades disponibles, no puede ser negativo.
        description (str): Descripción detallada del producto.
    """

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v: float) -> float:
        """Valida que el precio sea estrictamente mayor a 0."""
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("stock")
    @classmethod
    def stock_must_be_non_negative(cls, v: int) -> int:
        """Valida que el stock no sea negativo."""
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir el mensaje del usuario en el endpoint POST /chat.

    Attributes:
        session_id (str): Identificador único de la sesión del usuario.
        message (str): Texto del mensaje enviado por el usuario.
    """

    session_id: str
    message: str

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        """Valida que el mensaje no esté vacío ni sea solo espacios."""
        if not v.strip():
            raise ValueError("El mensaje no puede estar vacío")
        return v

    @field_validator("session_id")
    @classmethod
    def session_id_not_empty(cls, v: str) -> str:
        """Valida que el session_id no esté vacío ni sea solo espacios."""
        if not v.strip():
            raise ValueError("El session_id no puede estar vacío")
        return v


class ChatMessageResponseDTO(BaseModel):
    """
    DTO para retornar la respuesta del asistente de IA al cliente.

    Attributes:
        session_id (str): Identificador de la sesión.
        user_message (str): Mensaje original del usuario.
        assistant_message (str): Respuesta generada por el asistente de IA.
        timestamp (datetime): Marca de tiempo del intercambio.
    """

    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para representar un mensaje individual en el historial de chat.

    Attributes:
        id (int): Identificador del mensaje.
        role (str): Rol del emisor ('user' o 'assistant').
        message (str): Contenido del mensaje.
        timestamp (datetime): Marca de tiempo del mensaje.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    timestamp: datetime