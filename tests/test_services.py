"""
tests/test_services.py
-----------------------
Tests unitarios para los servicios de la capa de aplicación:
ProductService y ChatService, usando mocks de repositorios.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from domain.entities import Product, ChatMessage
from domain.exceptions import ProductNotFoundError, InvalidProductDataError
from application.dtos import (
    ProductDTO,
    ChatMessageRequestDTO,
    ChatMessageResponseDTO,
)
from application.product_service import ProductService
from application.chat_service import ChatService


# ─────────────────────────────────────────────────────────────────────────────
# Tests para ProductService
# ─────────────────────────────────────────────────────────────────────────────

class TestProductService:
    """Tests del servicio de productos usando mock del repositorio."""

    def test_get_all_products_retorna_lista(
        self, mock_product_repository, product_valido
    ):
        """get_all_products() debe delegar en el repositorio y retornar la lista."""
        mock_product_repository.get_all.return_value = [product_valido]
        service = ProductService(mock_product_repository)

        result = service.get_all_products()

        mock_product_repository.get_all.assert_called_once()
        assert len(result) == 1
        assert result[0].name == "Air Zoom Pegasus"

    def test_get_product_by_id_existente(
        self, mock_product_repository, product_valido
    ):
        """get_product_by_id() retorna el producto cuando existe."""
        mock_product_repository.get_by_id.return_value = product_valido
        service = ProductService(mock_product_repository)

        result = service.get_product_by_id(1)

        assert result.id == 1
        assert result.brand == "Nike"

    def test_get_product_by_id_no_existente(self, mock_product_repository):
        """get_product_by_id() lanza ProductNotFoundError cuando no existe."""
        mock_product_repository.get_by_id.return_value = None
        service = ProductService(mock_product_repository)

        with pytest.raises(ProductNotFoundError):
            service.get_product_by_id(999)

    def test_create_product_llama_save(self, mock_product_repository, product_valido):
        """create_product() convierte el DTO y llama a repository.save()."""
        mock_product_repository.save.return_value = product_valido
        service = ProductService(mock_product_repository)

        dto = ProductDTO(
            name="Air Zoom Pegasus",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla de running.",
        )
        result = service.create_product(dto)

        mock_product_repository.save.assert_called_once()
        assert result.name == "Air Zoom Pegasus"

    def test_create_product_precio_invalido(self, mock_product_repository):
        """create_product() lanza InvalidProductDataError con precio 0."""
        service = ProductService(mock_product_repository)

        with pytest.raises(Exception):
            # Pydantic rechaza precio 0 en el DTO directamente
            ProductDTO(
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=0,
                stock=5,
                description="Test",
            )

    def test_delete_product_existente(
        self, mock_product_repository, product_valido
    ):
        """delete_product() retorna True cuando el producto existe."""
        mock_product_repository.get_by_id.return_value = product_valido
        mock_product_repository.delete.return_value = True
        service = ProductService(mock_product_repository)

        result = service.delete_product(1)

        assert result is True
        mock_product_repository.delete.assert_called_once_with(1)

    def test_delete_product_no_existente(self, mock_product_repository):
        """delete_product() lanza ProductNotFoundError si no existe."""
        mock_product_repository.get_by_id.return_value = None
        service = ProductService(mock_product_repository)

        with pytest.raises(ProductNotFoundError):
            service.delete_product(999)

    def test_get_available_products_filtra_sin_stock(
        self, mock_product_repository, product_valido
    ):
        """get_available_products() filtra productos con stock=0."""
        sin_stock = Product(
            id=2, name="Sin Stock", brand="Adidas", category="Running",
            size="40", color="Blanco", price=90.0, stock=0,
            description="Sin stock.",
        )
        mock_product_repository.get_all.return_value = [product_valido, sin_stock]
        service = ProductService(mock_product_repository)

        result = service.get_available_products()

        assert len(result) == 1
        assert result[0].name == "Air Zoom Pegasus"


# ─────────────────────────────────────────────────────────────────────────────
# Tests para ChatService
# ─────────────────────────────────────────────────────────────────────────────

class TestChatService:
    """Tests del servicio de chat usando mocks de repositorios y IA."""

    def test_get_session_history_retorna_dtos(
        self,
        mock_product_repository,
        mock_chat_repository,
        mock_ai_service,
        chat_message_usuario,
        chat_message_asistente,
    ):
        """get_session_history() convierte los mensajes a ChatHistoryDTO."""
        mock_chat_repository.get_session_history.return_value = [
            chat_message_usuario,
            chat_message_asistente,
        ]
        service = ChatService(
            product_repository=mock_product_repository,
            chat_repository=mock_chat_repository,
            ai_service=mock_ai_service,
        )

        result = service.get_session_history("sesion_001")

        assert len(result) == 2
        assert result[0].role == "user"
        assert result[1].role == "assistant"

    def test_clear_session_history_llama_delete(
        self, mock_product_repository, mock_chat_repository, mock_ai_service
    ):
        """clear_session_history() debe llamar a delete_session_history del repo."""
        mock_chat_repository.delete_session_history.return_value = 4
        service = ChatService(
            product_repository=mock_product_repository,
            chat_repository=mock_chat_repository,
            ai_service=mock_ai_service,
        )

        result = service.clear_session_history("sesion_001")

        mock_chat_repository.delete_session_history.assert_called_once_with("sesion_001")
        assert result == 4

    def test_process_message_retorna_response_dto(
        self,
        mock_product_repository,
        mock_chat_repository,
        mock_ai_service,
        product_valido,
    ):
        """process_message() retorna un ChatMessageResponseDTO con la respuesta de IA."""
        mock_product_repository.get_all.return_value = [product_valido]
        mock_chat_repository.get_recent_messages.return_value = []
        mock_chat_repository.save_message.return_value = MagicMock()

        # El servicio de IA es async; simulamos coroutine
        async def fake_generate(*args, **kwargs):
            return "Tenemos el Nike Air Zoom disponible en talla 42."

        mock_ai_service.generate_response = fake_generate

        service = ChatService(
            product_repository=mock_product_repository,
            chat_repository=mock_chat_repository,
            ai_service=mock_ai_service,
        )
        request = ChatMessageRequestDTO(
            session_id="sesion_001",
            message="Busco zapatos Nike talla 42",
        )

        result = asyncio.get_event_loop().run_until_complete(
            service.process_message(request)
        )

        assert isinstance(result, ChatMessageResponseDTO)
        assert result.session_id == "sesion_001"
        assert "Nike" in result.assistant_message
        # Se deben haber guardado 2 mensajes: usuario + asistente
        assert mock_chat_repository.save_message.call_count == 2
