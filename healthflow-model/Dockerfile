FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Change le port selon le service (8082, 8083...)
EXPOSE 8085
# Commande de lancement
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8085"]
