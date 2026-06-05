FROM python:3.11-slim

# Crear usuario no-root por seguridad
RUN useradd -m zenituser

WORKDIR /app

# Copiar dependencias
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copiar el proyecto completo
COPY . .

# Cambiar permisos
RUN chown -R zenituser:zenituser /app

USER zenituser

# Exponer el puerto interno
EXPOSE 8000

# Comando de arranque
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
