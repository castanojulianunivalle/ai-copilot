FROM python:3.11-slim

# Logs sin bufer, para que Render los muestre en vivo, y sin .pyc dentro de la imagen
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY main.py version.py /app/
# Paquete del componente inteligente (Sprint 5): cliente LLM, prompts y parser
COPY ai /app/ai

# HU-10: la API no necesita privilegios de root dentro del contenedor
RUN useradd --create-home --uid 10001 api
USER api

# PORT puede venir de Render o del .env local
ENV PORT=8001

# Usar PORT desde variable de entorno (Render lo inyecta automáticamente)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"
