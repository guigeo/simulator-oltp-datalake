FROM python:3.10-slim

WORKDIR /app

# Para evitar erros de certificado e instalar libs necessárias
RUN apt-get update && apt-get install -y \
    gcc \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o consumer
COPY consumer_universal.py .

CMD ["python", "consumer_universal.py"]
