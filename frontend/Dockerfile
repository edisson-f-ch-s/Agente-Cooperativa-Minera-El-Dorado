FROM python:3.11-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY streamlit_app.py .

# Puerto del servidor
EXPOSE 8501

# Comando de inicio
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
