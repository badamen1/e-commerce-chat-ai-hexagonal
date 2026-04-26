"""
src/infrastructure/db/init_data.py
------------------------------------
Carga el catálogo inicial de productos en la base de datos.
Solo inserta datos si la tabla de productos está vacía.
"""

from sqlalchemy.orm import Session

from infrastructure.db.models import ProductModel


def load_initial_data(db: Session) -> None:
    """
    Inserta 10 productos de ejemplo si la base de datos está vacía.

    Verifica el conteo de registros antes de insertar para evitar
    duplicados en reinicios del servidor.

    Args:
        db (Session): Sesión activa de SQLAlchemy.
    """
    if db.query(ProductModel).count() > 0:
        return  # La BD ya tiene datos; no hacer nada

    productos_iniciales = [
        ProductModel(
            name="Air Zoom Pegasus 40",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro/Blanco",
            price=120.00,
            stock=5,
            description="Zapatilla de running con amortiguación Zoom Air. Ideal para largas distancias.",
        ),
        ProductModel(
            name="Ultraboost 23",
            brand="Adidas",
            category="Running",
            size="41",
            color="Blanco",
            price=150.00,
            stock=3,
            description="Máxima energía con suela Boost. Perfecta para corredores exigentes.",
        ),
        ProductModel(
            name="Suede Classic XXI",
            brand="Puma",
            category="Casual",
            size="40",
            color="Azul marino",
            price=80.00,
            stock=10,
            description="Clásico urbano con cuero genuino. Estilo retro para el día a día.",
        ),
        ProductModel(
            name="Chuck Taylor All Star",
            brand="Converse",
            category="Casual",
            size="43",
            color="Rojo",
            price=65.00,
            stock=8,
            description="El ícono de la cultura urbana. Lona resistente y suela vulcanizada.",
        ),
        ProductModel(
            name="Old Skool",
            brand="Vans",
            category="Casual",
            size="42",
            color="Negro/Blanco",
            price=70.00,
            stock=12,
            description="Skate shoe clásica con la característica franja lateral. Muy versátil.",
        ),
        ProductModel(
            name="990v6",
            brand="New Balance",
            category="Running",
            size="44",
            color="Gris",
            price=175.00,
            stock=4,
            description="Rendimiento superior con tecnología ENCAP y ABZORB. Amortiguación premium.",
        ),
        ProductModel(
            name="RS-X³ Puzzle",
            brand="Puma",
            category="Casual",
            size="41",
            color="Blanco/Amarillo",
            price=95.00,
            stock=6,
            description="Diseño chunky de los 90s con capas de materiales y colores vibrantes.",
        ),
        ProductModel(
            name="Air Force 1 '07",
            brand="Nike",
            category="Casual",
            size="43",
            color="Blanco",
            price=110.00,
            stock=7,
            description="El clásico de la cancha ahora en las calles. Cuero premium, look limpio.",
        ),
        ProductModel(
            name="Stan Smith",
            brand="Adidas",
            category="Formal",
            size="40",
            color="Blanco/Verde",
            price=90.00,
            stock=9,
            description="Elegancia minimalista. El zapato de tenis más icónico del mundo.",
        ),
        ProductModel(
            name="Oxford Clásico",
            brand="Clarks",
            category="Formal",
            size="42",
            color="Marrón",
            price=140.00,
            stock=4,
            description="Zapato formal de cuero genuino con suela de goma. Ideal para oficina.",
        ),
    ]

    db.add_all(productos_iniciales)
    db.commit()
