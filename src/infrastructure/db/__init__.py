"""
src/infrastructure/db/__init__.py
----------------------------------
Inicialización de la capa de base de datos.
Exporta las utilidades principales de acceso a datos y ejecuta
la creación de tablas y carga de datos iniciales al arrancar.
"""

from .database import engine, Base, SessionLocal, get_db, init_db
from .models import ProductModel, ChatMemoryModel


def load_initial_data() -> None:
    """
    Carga datos iniciales de productos en la base de datos.

    Verifica si ya existen productos antes de insertar.
    Se llama automáticamente desde init_db() si la tabla está vacía.
    """
    db = SessionLocal()
    try:
        if db.query(ProductModel).count() > 0:
            print("Datos iniciales ya cargados, no se insertarán de nuevo.")
            return

        products = [
            ProductModel(name="Air Jordan 3 Retro", brand="Nike", category="Basketball",
                         size="11", color="White", price=200.0, stock=5,
                         description="Classic Air Jordan 3 Retro sneakers with iconic design."),
            ProductModel(name="Yeezy Boost 350 V2", brand="Adidas", category="Casual",
                         size="10", color="Black", price=220.0, stock=3,
                         description="Popular Yeezy Boost 350 V2 sneakers with comfortable fit."),
            ProductModel(name="Adidas Jellyfish", brand="Adidas", category="Casual",
                         size="9", color="Blue", price=50.0, stock=10,
                         description="Trendy Adidas Jellyfish sneakers perfect for summer."),
            ProductModel(name="Nike Mind", brand="Nike", category="Casual",
                         size="11", color="White", price=150.0, stock=7,
                         description="Comfortable Nike Mind sandals for everyday wear."),
            ProductModel(name="Adidas Adilette", brand="Adidas", category="Casual",
                         size="10", color="Black", price=60.0, stock=8,
                         description="Classic Adidas Adilette slides with iconic three stripes design."),
            ProductModel(name="Air Jordan 1 Low Travis Scott", brand="Nike", category="Basketball",
                         size="9", color="Pink", price=250.0, stock=4,
                         description="Exclusive Air Jordan 1 Low Travis Scott with unique design."),
            ProductModel(name="Adidas Yeezy Slide", brand="Adidas", category="Casual",
                         size="10", color="Brown", price=80.0, stock=6,
                         description="Comfortable Adidas Yeezy Slide sandals with minimalist design."),
            ProductModel(name="Nike Air Force 1", brand="Nike", category="Casual",
                         size="11", color="White", price=120.0, stock=9,
                         description="Classic Nike Air Force 1 sneakers with timeless design."),
            ProductModel(name="Adidas Superstar", brand="Adidas", category="Casual",
                         size="10", color="Black", price=100.0, stock=5,
                         description="Iconic Adidas Superstar with shell toe design and leather upper."),
            ProductModel(name="Asics Gel-Kayano 14", brand="Asics", category="Running",
                         size="9", color="Blue", price=160.0, stock=4,
                         description="High-performance running shoes with advanced cushioning."),
        ]

        db.add_all(products)
        db.commit()
        print(f"✅ {len(products)} productos iniciales cargados correctamente.")
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas y cargando datos.

    Debe ejecutarse una única vez al arrancar la aplicación.
    Crea las tablas si no existen y llama a load_initial_data() si
    la tabla de productos está vacía.
    """
    # Importar modelos para que Base los conozca antes del create_all
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    load_initial_data()