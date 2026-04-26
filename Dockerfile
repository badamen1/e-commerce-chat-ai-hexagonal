# ─────────────────────────────────────────────────────────────
# Dockerfile — E-commerce Chat AI
# Imagen base: Python 3.11 slim para reducir tamaño
# ─────────────────────────────────────────────────────────────

FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements primero para aprovechar el cache de layers de Docker
COPY requirements.txt .

# Instalar dependencias sin caché para mantener la imagen pequeña
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente al contenedor
COPY . .

# Crear el directorio de datos para SQLite (persiste a través de volúmenes)
RUN mkdir -p /app/data

# Exponer el puerto de la aplicación
EXPOSE 8000

# Variable de entorno para que Python encuentre los módulos bajo src/
ENV PYTHONPATH=/app/src

# Comando de inicio: uvicorn apuntando al módulo de FastAPI
CMD ["uvicorn", "infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]