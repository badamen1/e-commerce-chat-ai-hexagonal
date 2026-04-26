# E-commerce Chat AI — Universidad EAFIT

API REST de e-commerce de zapatos con asistente conversacional potenciado por Google Gemini AI, construida con arquitectura hexagonal en Python usando FastAPI.

## Características Principales

- Catálogo de productos con filtros por marca y categoría
- Chat inteligente con memoria conversacional (Google Gemini)
- Arquitectura en 3 capas: Domain, Application, Infrastructure
- Persistencia con SQLite + SQLAlchemy
- Containerización con Docker
- Documentación automática con Swagger UI

## Tecnologías

| Tecnología | Propósito |
|---|---|
| Python 3.11 | Lenguaje principal |
| FastAPI | Framework web REST |
| SQLAlchemy | ORM + acceso a datos |
| SQLite | Base de datos |
| Google Gemini AI | Modelo de lenguaje conversacional |
| Pydantic | Validación de datos (DTOs) |
| Docker | Containerización |
| Pytest | Tests unitarios |

## Arquitectura

```
src/
├── domain/          # Entidades, interfaces y excepciones (lógica de negocio pura)
├── application/     # Servicios y DTOs (casos de uso)
└── infrastructure/  # FastAPI, SQLAlchemy, Gemini (detalles técnicos)
```

## Requisitos Previos

- Python 3.10+
- Docker y Docker Compose
- API Key de Google Gemini ([obtener aquí](https://aistudio.google.com/app/apikey))

## Instalación Local

```bash
# 1. Clonar el repositorio
git clone <url-del-repo>
cd e-commerce-chat-ai

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tu GEMINI_API_KEY real

# 5. Crear carpeta de datos
mkdir data

# 6. Ejecutar la aplicación
cd src
uvicorn infrastructure.api.main:app --reload
```

La API estará disponible en `http://localhost:8000`.

## Ejecución con Docker

```bash
# Construir y levantar los contenedores
docker compose up --build

# Correr en segundo plano
docker compose up -d --build

# Ver logs
docker compose logs -f

# Detener
docker compose down
```

## Configuración (.env)

```env
GEMINI_API_KEY=tu_api_key_de_gemini
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/` | Información básica de la API |
| `GET` | `/health` | Health check |
| `GET` | `/products` | Lista todos los productos |
| `GET` | `/products/{id}` | Obtiene un producto por ID |
| `POST` | `/chat` | Envía mensaje al asistente de IA |
| `GET` | `/chat/history/{session_id}` | Historial de una sesión |
| `DELETE` | `/chat/history/{session_id}` | Elimina historial de una sesión |

### Documentación Interactiva

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Ejemplos de Uso

**Listar productos:**
```bash
curl http://localhost:8000/products
```

**Enviar mensaje al chat:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "usuario_01", "message": "Busco zapatos Nike para correr talla 42"}'
```

**Ver historial de conversación:**
```bash
curl http://localhost:8000/chat/history/usuario_01
```

## Tests

```bash
# Desde la raíz del proyecto
pytest

# Con reporte de cobertura
pip install pytest-cov
pytest --cov=src tests/
```

## Estructura de Directorios

```
e-commerce-chat-ai/
├── src/
│   ├── config.py
│   ├── domain/
│   │   ├── entities.py        # Product, ChatMessage, ChatContext
│   │   ├── repositories.py    # IProductRepository, IChatRepository
│   │   └── exceptions.py      # Excepciones del dominio
│   ├── application/
│   │   ├── dtos.py            # DTOs con validación Pydantic
│   │   ├── product_service.py # Servicio de productos
│   │   └── chat_service.py    # Servicio de chat con IA
│   └── infrastructure/
│       ├── api/main.py        # Endpoints FastAPI
│       ├── db/                # Base de datos SQLAlchemy
│       ├── repositories/      # Implementaciones concretas
│       └── llm_providers/     # Integración con Gemini
├── tests/
│   ├── conftest.py
│   ├── test_entities.py
│   └── test_services.py
├── data/                      # Base de datos SQLite (auto-generada)
├── evidencias/                # Screenshots de evidencia
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Evidencias

Las capturas de pantalla de evidencia se encuentran en la carpeta `evidencias/`:

| Archivo | Contenido |
|---------|-----------|
| `01-swagger-ui.png` | Swagger UI mostrando todos los endpoints |
| `02-docker-logs.png` | Logs de Docker con la aplicación corriendo |
| `03-docker-running.png` | Docker Desktop / `docker ps` con contenedor activo |
| `04-api-call-products.png` | GET /products desde Postman/Insomnia |
| `05-api-call-chat.png` | POST /chat con respuesta del asistente de IA |
| `06-database.png` | Base de datos SQLite con productos cargados |

## Autor

Universidad EAFIT — Taller: Construcción de E-commerce con Chat IA
