from typing import List, Optional
from datetime import datetime

from domain.repositories import IProductRepository, IChatRepository
from domain.entities import ChatMessage, ChatContext
from domain.exceptions import ChatServiceError
from application.dtos import ChatMessageRequestDTO, ChatMessageResponseDTO, ChatHistoryDTO


class ChatService:
    """
    Servicio de aplicación para gestionar el chat con IA.

    Orquesta el flujo completo:
        1. Recupera productos y contexto del historial.
        2. Llama al servicio de IA para generar una respuesta.
        3. Persiste los mensajes del usuario y del asistente.
        4. Devuelve el DTO de respuesta.
    """

    def __init__(
        self,
        product_repository: IProductRepository,
        chat_repository: IChatRepository,
        ai_service,  # GeminiService – sin tipado estricto para evitar acoplamiento
    ):
        self.product_repository = product_repository
        self.chat_repository = chat_repository
        self.ai_service = ai_service

    # ------------------------------------------------------------------
    # Método principal
    # ------------------------------------------------------------------

    async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
        """
        Procesa un mensaje del usuario y devuelve la respuesta del asistente.

        Flujo:
            1. Obtener todos los productos disponibles.
            2. Obtener los últimos 6 mensajes del historial de la sesión.
            3. Crear un ChatContext con ese historial.
            4. Llamar a ai_service.generate_response() con el mensaje, productos y contexto.
            5. Guardar el mensaje del usuario en el repositorio.
            6. Guardar la respuesta del asistente en el repositorio.
            7. Retornar un ChatMessageResponseDTO.
        """
        try:
            # 1. Obtener productos
            products = self.product_repository.get_all()

            # 2. Obtener historial reciente (últimos 6 mensajes)
            recent_messages = self.chat_repository.get_recent_messages(
                session_id=request.session_id,
                count=6,
            )

            # 3. Crear contexto conversacional
            context = ChatContext(messages=recent_messages)

            # 4. Llamar al servicio de IA (operación asíncrona)
            assistant_response: str = await self.ai_service.generate_response(
                user_message=request.message,
                products=products,
                context=context,
            )

            now = datetime.utcnow()

            # 5. Guardar mensaje del usuario
            user_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="user",
                message=request.message,
                timestamp=now,
            )
            self.chat_repository.save_message(user_message)

            # 6. Guardar respuesta del asistente
            assistant_message = ChatMessage(
                id=None,
                session_id=request.session_id,
                role="assistant",
                message=assistant_response,
                timestamp=now,
            )
            self.chat_repository.save_message(assistant_message)

            # 7. Retornar DTO de respuesta
            return ChatMessageResponseDTO(
                session_id=request.session_id,
                user_message=request.message,
                assistant_message=assistant_response,
                timestamp=now,
            )

        except Exception as e:
            raise ChatServiceError(f"Error al procesar el mensaje: {str(e)}")

    # ------------------------------------------------------------------
    # Métodos adicionales
    # ------------------------------------------------------------------

    def get_session_history(
        self, session_id: str, limit: Optional[int] = None
    ) -> List[ChatHistoryDTO]:
        """
        Obtiene el historial completo (o limitado) de una sesión.

        Returns:
            Lista de ChatHistoryDTO en orden cronológico.
        """
        messages = self.chat_repository.get_session_history(session_id, limit)
        return [
            ChatHistoryDTO(
                id=msg.id,
                role=msg.role,
                message=msg.message,
                timestamp=msg.timestamp,
            )
            for msg in messages
        ]

    def clear_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión.

        Returns:
            Cantidad de mensajes eliminados.
        """
        return self.chat_repository.delete_session_history(session_id)
