FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación y datos
COPY app/ ./app/
COPY data/ ./data/

# Puerto del servidor
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
