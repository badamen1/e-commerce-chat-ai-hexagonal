"""
src/config.py
--------------
Configuración global de la aplicación.
Lee las variables de entorno del archivo .env mediante python-dotenv.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Centraliza la configuración de la aplicación leyendo variables de entorno.

    Attributes:
        gemini_api_key (str): Clave de API de Google Gemini.
        database_url (str): URL de conexión a la base de datos SQLite.
        environment (str): Entorno de ejecución ('development' o 'production').
    """

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/ecommerce_chat.db")
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()
