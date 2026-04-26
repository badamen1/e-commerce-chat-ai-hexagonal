"""
src/infrastructure/repositories/chat_repository.py
----------------------------------------------------
Implementación concreta de IChatRepository usando SQLAlchemy.
Gestiona el historial de conversaciones del chat con IA.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from infrastructure.db.models import ChatMemoryModel
from domain.repositories import IChatRepository
from domain.entities import ChatMessage


class SQLChatRepository(IChatRepository):
    """
    Repositorio de mensajes de chat con persistencia en SQLite a través de SQLAlchemy.

    Implementa todos los métodos de IChatRepository y se encarga de
    convertir entre modelos ORM (ChatMemoryModel) y entidades de dominio (ChatMessage).

    Attributes:
        db (Session): Sesión de SQLAlchemy inyectada por FastAPI (Depends).
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con la sesión de base de datos.

        Args:
            db (Session): Sesión activa de SQLAlchemy.
        """
        self.db = db

    # ------------------------------------------------------------------ #
    #  Métodos de escritura                                                #
    # ------------------------------------------------------------------ #

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje de chat en la base de datos.

        Args:
            message (ChatMessage): Entidad de mensaje a persistir.

        Returns:
            ChatMessage: Entidad guardada con el ID asignado por la BD.
        """
        chat_model = self._entity_to_model(message)
        self.db.add(chat_model)
        self.db.commit()
        self.db.refresh(chat_model)
        return self._model_to_entity(chat_model)

    # ------------------------------------------------------------------ #
    #  Métodos de lectura                                                  #
    # ------------------------------------------------------------------ #

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatMessage]:
        """
        Obtiene el historial completo (o limitado) de una sesión en orden cronológico.

        Los mensajes se retornan del más antiguo al más reciente.

        Args:
            session_id (str): Identificador de la sesión de chat.
            limit (Optional[int]): Número máximo de mensajes. None = sin límite.

        Returns:
            List[ChatMessage]: Mensajes en orden cronológico (más antiguos primero).
        """
        query = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).order_by(ChatMemoryModel.timestamp.asc())

        if limit:
            query = query.limit(limit)

        return [self._model_to_entity(m) for m in query.all()]

    def get_recent_messages(self, session_id: str, count: int = 6) -> List[ChatMessage]:
        """
        Obtiene los últimos N mensajes de una sesión en orden cronológico.

        Crucial para construir el contexto conversacional del prompt de IA.

        Args:
            session_id (str): Identificador de la sesión de chat.
            count (int): Número de mensajes recientes a retornar (por defecto 6).

        Returns:
            List[ChatMessage]: Últimos N mensajes en orden cronológico (más antiguos primero).
        """
        # Obtenemos los últimos N en orden descendente (recientes primero)
        messages = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).order_by(ChatMemoryModel.timestamp.desc()).limit(count).all()

        # Convertir a entidades y revertir para orden cronológico
        entities = [self._model_to_entity(m) for m in messages]
        entities.reverse()
        return entities

    # ------------------------------------------------------------------ #
    #  Método de eliminación                                               #
    # ------------------------------------------------------------------ #

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de mensajes de una sesión.

        Args:
            session_id (str): Identificador de la sesión a limpiar.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        count = self.db.query(ChatMemoryModel).filter(
            ChatMemoryModel.session_id == session_id
        ).delete()
        self.db.commit()
        return count

    # ------------------------------------------------------------------ #
    #  Métodos auxiliares de conversión                                    #
    # ------------------------------------------------------------------ #

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """
        Convierte un modelo ORM (ChatMemoryModel) a una entidad de dominio (ChatMessage).

        Args:
            model (ChatMemoryModel): Modelo ORM de la base de datos.

        Returns:
            ChatMessage: Entidad de dominio correspondiente.
        """
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """
        Convierte una entidad de dominio (ChatMessage) a un modelo ORM (ChatMemoryModel).

        Args:
            entity (ChatMessage): Entidad del dominio.

        Returns:
            ChatMemoryModel: Modelo ORM listo para persistir.
        """
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )