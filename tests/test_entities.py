"""
tests/test_entities.py
-----------------------
Tests unitarios para las entidades del dominio:
Product, ChatMessage y ChatContext.
"""

import pytest
from datetime import datetime

from domain.entities import Product, ChatMessage, ChatContext


# ─────────────────────────────────────────────────────────────────────────────
# Tests para Product
# ─────────────────────────────────────────────────────────────────────────────

class TestProduct:
    """Tests para la entidad Product y sus validaciones de negocio."""

    def test_crear_producto_valido(self):
        """Un producto con datos correctos debe crearse sin errores."""
        product = Product(
            id=1,
            name="Air Zoom Pegasus",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla de running.",
        )
        assert product.name == "Air Zoom Pegasus"
        assert product.price == 120.0
        assert product.stock == 5

    def test_precio_negativo_lanza_error(self):
        """El precio no puede ser cero ni negativo."""
        with pytest.raises(ValueError, match="precio"):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=-10.0,
                stock=5,
                description="Test",
            )

    def test_precio_cero_lanza_error(self):
        """El precio igual a cero debe lanzar ValueError."""
        with pytest.raises(ValueError):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=0.0,
                stock=5,
                description="Test",
            )

    def test_stock_negativo_lanza_error(self):
        """El stock no puede ser negativo."""
        with pytest.raises(ValueError, match="stock"):
            Product(
                id=None,
                name="Test",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=100.0,
                stock=-1,
                description="Test",
            )

    def test_nombre_vacio_lanza_error(self):
        """El nombre no puede estar vacío."""
        with pytest.raises(ValueError, match="nombre"):
            Product(
                id=None,
                name="",
                brand="Nike",
                category="Running",
                size="42",
                color="Negro",
                price=100.0,
                stock=5,
                description="Test",
            )

    def test_is_available_con_stock(self, product_valido):
        """is_available() retorna True cuando hay stock."""
        assert product_valido.is_available() is True

    def test_is_available_sin_stock(self, product_valido):
        """is_available() retorna False cuando el stock es 0."""
        product_valido.stock = 0
        assert product_valido.is_available() is False

    def test_reduce_stock_exitoso(self, product_valido):
        """reduce_stock() disminuye el stock correctamente."""
        product_valido.reduce_stock(3)
        assert product_valido.stock == 2

    def test_reduce_stock_cantidad_mayor_al_stock(self, product_valido):
        """reduce_stock() lanza ValueError si la cantidad supera el stock."""
        with pytest.raises(ValueError):
            product_valido.reduce_stock(10)

    def test_reduce_stock_cantidad_negativa(self, product_valido):
        """reduce_stock() lanza ValueError con cantidades negativas."""
        with pytest.raises(ValueError):
            product_valido.reduce_stock(-1)

    def test_increase_stock_exitoso(self, product_valido):
        """increase_stock() incrementa el stock correctamente."""
        product_valido.increase_stock(5)
        assert product_valido.stock == 10

    def test_increase_stock_cantidad_negativa(self, product_valido):
        """increase_stock() lanza ValueError con cantidades negativas."""
        with pytest.raises(ValueError):
            product_valido.increase_stock(-3)


# ─────────────────────────────────────────────────────────────────────────────
# Tests para ChatMessage
# ─────────────────────────────────────────────────────────────────────────────

class TestChatMessage:
    """Tests para la entidad ChatMessage y sus validaciones."""

    def test_crear_mensaje_usuario_valido(self):
        """Un ChatMessage de role 'user' debe crearse correctamente."""
        msg = ChatMessage(
            id=1,
            session_id="sesion_001",
            role="user",
            message="Hola",
            timestamp=datetime.utcnow(),
        )
        assert msg.role == "user"
        assert msg.is_from_user() is True
        assert msg.is_from_assistant() is False

    def test_crear_mensaje_asistente_valido(self):
        """Un ChatMessage de role 'assistant' debe crearse correctamente."""
        msg = ChatMessage(
            id=2,
            session_id="sesion_001",
            role="assistant",
            message="¡Hola! ¿En qué puedo ayudarte?",
            timestamp=datetime.utcnow(),
        )
        assert msg.role == "assistant"
        assert msg.is_from_assistant() is True
        assert msg.is_from_user() is False

    def test_role_invalido_lanza_error(self):
        """Un role distinto de 'user' o 'assistant' debe lanzar ValueError."""
        with pytest.raises(ValueError, match="rol"):
            ChatMessage(
                id=None,
                session_id="s1",
                role="admin",
                message="Hola",
                timestamp=datetime.utcnow(),
            )

    def test_mensaje_vacio_lanza_error(self):
        """Un mensaje vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="mensaje"):
            ChatMessage(
                id=None,
                session_id="s1",
                role="user",
                message="",
                timestamp=datetime.utcnow(),
            )

    def test_session_id_vacio_lanza_error(self):
        """Un session_id vacío debe lanzar ValueError."""
        with pytest.raises(ValueError, match="session_id"):
            ChatMessage(
                id=None,
                session_id="",
                role="user",
                message="Hola",
                timestamp=datetime.utcnow(),
            )


# ─────────────────────────────────────────────────────────────────────────────
# Tests para ChatContext
# ─────────────────────────────────────────────────────────────────────────────

class TestChatContext:
    """Tests para el value object ChatContext."""

    def _make_messages(self, n: int) -> list:
        """Crea N mensajes alternados user/assistant para tests."""
        msgs = []
        for i in range(n):
            role = "user" if i % 2 == 0 else "assistant"
            msgs.append(
                ChatMessage(
                    id=i + 1,
                    session_id="s1",
                    role=role,
                    message=f"Mensaje {i + 1}",
                    timestamp=datetime.utcnow(),
                )
            )
        return msgs

    def test_get_recent_messages_retorna_ultimos_n(self):
        """get_recent_messages() retorna solo los últimos max_messages."""
        msgs = self._make_messages(10)
        ctx = ChatContext(messages=msgs, max_messages=6)
        recientes = ctx.get_recent_messages()
        assert len(recientes) == 6
        assert recientes[-1].message == "Mensaje 10"

    def test_get_recent_messages_menos_que_max(self):
        """Si hay menos mensajes que max_messages, retorna todos."""
        msgs = self._make_messages(3)
        ctx = ChatContext(messages=msgs, max_messages=6)
        assert len(ctx.get_recent_messages()) == 3

    def test_format_for_prompt_formato_correcto(self):
        """format_for_prompt() genera el texto con roles en español."""
        msgs = [
            ChatMessage(id=1, session_id="s1", role="user",
                        message="Busco zapatos", timestamp=datetime.utcnow()),
            ChatMessage(id=2, session_id="s1", role="assistant",
                        message="Tengo varios modelos", timestamp=datetime.utcnow()),
        ]
        ctx = ChatContext(messages=msgs)
        resultado = ctx.format_for_prompt()
        assert "Usuario: Busco zapatos" in resultado
        assert "Asistente: Tengo varios modelos" in resultado

    def test_format_for_prompt_sin_mensajes(self):
        """format_for_prompt() retorna string vacío si no hay mensajes."""
        ctx = ChatContext(messages=[])
        assert ctx.format_for_prompt() == ""
