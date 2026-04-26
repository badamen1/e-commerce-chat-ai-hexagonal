"""
src/infrastructure/api/main.py
-------------------------------
Punto de entrada de la aplicación FastAPI para el asistente de e-commerce.
Expone todos los endpoints REST y configura el middleware y el ciclo de vida.
"""

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# ── Infraestructura: DB ──────────────────────────────────────────────────────
from infrastructure.db.database import get_db, init_db
from infrastructure.db.models import ProductModel, ChatMemoryModel
from infrastructure.repositories.product_repository import SQLProductRepository
from infrastructure.repositories.chat_repository import SQLChatRepository
from infrastructure.llm_providers.gemini_service import GeminiService

# ── Aplicación: servicios y DTOs ─────────────────────────────────────────────
from application.product_service import ProductService
from application.chat_service import ChatService
from application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
    ChatHistoryDTO,
)

# ── Dominio: excepciones ──────────────────────────────────────────────────────
from domain.exceptions import ProductNotFoundError, ChatServiceError

# ─────────────────────────────────────────────────────────────────────────────
# Inicialización de la aplicación
# ─────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="E-commerce Chat AI API",
    description=(
        "API REST para el asistente virtual de ventas de zapatos. "
        "Permite consultar el catálogo de productos y mantener conversaciones "
        "contextuales con un agente de IA potenciado por Gemini."
    ),
    version="1.0.0",
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS middleware
# ─────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # En producción reemplaza por la URL del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Eventos del ciclo de vida
# ─────────────────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event() -> None:
    """
    Se ejecuta una única vez cuando la aplicación arranca.
    Crea las tablas en la BD y carga los datos iniciales si la BD está vacía.
    """
    init_db()


# ─────────────────────────────────────────────────────────────────────────────
# GET /  —  Información básica de la API
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["General"])
def read_root() -> dict:
    """
    Retorna información básica sobre la API: versión, descripción
    y lista de endpoints disponibles.
    """
    return {
        "name": "E-commerce Chat AI API",
        "version": "1.0.0",
        "description": "Asistente virtual de ventas de zapatos potenciado por Gemini."
    }


# ─────────────────────────────────────────────────────────────────────────────
# GET /products  —  Lista todos los productos
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/products", response_model=List[ProductDTO], tags=["Productos"])
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
    """
    Retorna la lista completa de productos registrados en el catálogo.

    - Usa el repositorio SQLAlchemy para acceder a la BD.
    - El ProductService convierte las entidades del dominio a DTOs de respuesta.
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    products = service.get_all_products()
    # Convertimos entidades del dominio → ProductDTO (Pydantic)
    return [ProductDTO.from_orm(p) if hasattr(ProductDTO, "from_orm")
            else ProductDTO(**p.__dict__) for p in products]


# ─────────────────────────────────────────────────────────────────────────────
# GET /products/{product_id}  —  Obtiene un producto por ID
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/products/{product_id}", response_model=ProductDTO, tags=["Productos"])
def get_product(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
    """
    Busca y retorna un producto específico por su ID.

    - Lanza **404** si el producto no existe en la base de datos.
    """
    repo = SQLProductRepository(db)
    service = ProductService(repo)
    try:
        product = service.get_product_by_id(product_id)
    except ProductNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Producto con id={product_id} no encontrado.",
        )
    return ProductDTO(**product.__dict__)


# ─────────────────────────────────────────────────────────────────────────────
# POST /chat  —  Procesa un mensaje de chat
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/chat", response_model=ChatMessageResponseDTO, tags=["Chat"])
async def chat(
    request: ChatMessageRequestDTO,
    db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
    """
    Recibe un mensaje del usuario y retorna la respuesta del asistente de IA.

    **Body esperado (JSON):**
    ```json
    {
      "session_id": "abc-123",
      "message": "¿Tienen zapatillas Nike talla 42?"
    }
    ```

    - Recupera el catálogo completo y el historial de la sesión.
    - Construye el contexto conversacional y llama a Gemini.
    - Persiste ambos mensajes (usuario + asistente) en la BD.
    - Lanza **500** si ocurre un error interno.
    """
    product_repo = SQLProductRepository(db)
    chat_repo = SQLChatRepository(db)
    gemini = GeminiService()
    service = ChatService(
        product_repository=product_repo,
        chat_repository=chat_repo,
        ai_service=gemini,
    )
    try:
        response = await service.process_message(request)
    except ChatServiceError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}",
        )
    return response


# ─────────────────────────────────────────────────────────────────────────────
# GET /chat/history/{session_id}  —  Historial de una sesión
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/chat/history/{session_id}",
    response_model=List[ChatHistoryDTO],
    tags=["Chat"],
)
def get_chat_history(
    session_id: str,
    limit: int = 10,
    db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
    """
    Retorna el historial de mensajes de una sesión de chat.

    - **session_id**: identificador único de la sesión (path parameter).
    - **limit**: máximo de mensajes a retornar (query parameter, por defecto 10).
    """
    chat_repo = SQLChatRepository(db)
    # Usamos un ProductRepository dummy; ChatService solo necesita chat_repo aquí
    product_repo = SQLProductRepository(db)
    service = ChatService(
        product_repository=product_repo,
        chat_repository=chat_repo,
        ai_service=None,  # No se necesita IA para consultar historial
    )
    return service.get_session_history(session_id, limit=limit)


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /chat/history/{session_id}  —  Elimina historial de una sesión
# ─────────────────────────────────────────────────────────────────────────────

@app.delete("/chat/history/{session_id}", tags=["Chat"])
def delete_chat_history(
    session_id: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    Elimina todos los mensajes asociados a una sesión de chat.

    Retorna la cantidad de mensajes eliminados.
    """
    chat_repo = SQLChatRepository(db)
    product_repo = SQLProductRepository(db)
    service = ChatService(
        product_repository=product_repo,
        chat_repository=chat_repo,
        ai_service=None,
    )
    deleted = service.clear_session_history(session_id)
    return {"session_id": session_id, "deleted_messages": deleted}


# ─────────────────────────────────────────────────────────────────────────────
# GET /health  —  Health check
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["General"])
def health_check() -> dict:
    """
    Endpoint de verificación de estado del servicio.
    Útil para monitoreo y load balancers.
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "E-commerce Chat AI API",
    }