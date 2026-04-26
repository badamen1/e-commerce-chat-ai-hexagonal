"""
tests/conftest.py
------------------
Fixtures compartidas entre todos los módulos de test.
"""

import sys
import os
import pytest
from datetime import datetime
from unittest.mock import MagicMock

# Agrega src/ al path para que los imports funcionen sin instalar el paquete
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from domain.entities import Product, ChatMessage, ChatContext


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures de entidades del dominio
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def product_valido():
    """Retorna un Product con datos válidos para usar en tests."""
    return Product(
        id=1,
        name="Air Zoom Pegasus",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla de running con amortiguación Zoom Air.",
    )


@pytest.fixture
def chat_message_usuario():
    """Retorna un ChatMessage de tipo 'user' para usar en tests."""
    return ChatMessage(
        id=1,
        session_id="sesion_001",
        role="user",
        message="Hola, busco zapatos para correr",
        timestamp=datetime(2024, 1, 15, 10, 30, 0),
    )


@pytest.fixture
def chat_message_asistente():
    """Retorna un ChatMessage de tipo 'assistant' para usar en tests."""
    return ChatMessage(
        id=2,
        session_id="sesion_001",
        role="assistant",
        message="Tengo varias opciones de running disponibles.",
        timestamp=datetime(2024, 1, 15, 10, 30, 2),
    )


@pytest.fixture
def mock_product_repository():
    """Retorna un mock de IProductRepository."""
    return MagicMock()


@pytest.fixture
def mock_chat_repository():
    """Retorna un mock de IChatRepository."""
    return MagicMock()


@pytest.fixture
def mock_ai_service():
    """Retorna un mock del servicio de IA."""
    return MagicMock()
