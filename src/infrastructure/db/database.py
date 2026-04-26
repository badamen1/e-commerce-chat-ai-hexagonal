from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """
    Generador que provee una sesión de base de datos por request.

    Garantiza que la sesión se cierre al finalizar el request,
    incluso si ocurre una excepción.

    Yields:
        Session: Sesión activa de SQLAlchemy.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Inicializa la base de datos creando todas las tablas y cargando datos iniciales.

    Crea las tablas definidas en los modelos ORM y, si la BD está vacía,
    carga el catálogo inicial de productos. Se ejecuta una vez al arrancar.
    """
    # Los modelos deben estar importados antes de llamar create_all.
    # main.py los importa explícitamente para garantizar el registro en Base.metadata.
    Base.metadata.create_all(bind=engine)

    # Cargar datos iniciales si la BD está vacía
    from infrastructure.db.init_data import load_initial_data
    db = SessionLocal()
    try:
        load_initial_data(db)
    finally:
        db.close()