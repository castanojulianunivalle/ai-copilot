FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY main.py /app/main.py
COPY notificaciones.py /app/notificaciones.py
# Paquete del componente inteligente (Sprint 5): cliente LLM, prompts y parser
COPY ai /app/ai

# PORT puede venir de Render o del .env local
ENV PORT=8001

# Usar PORT desde variable de entorno (Render lo inyecta automáticamente)
CMD sh -c "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}"
