FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .
COPY web_interface/requirements.txt ./web_interface/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r web_interface/requirements.txt
RUN pip install --no-cache-dir Pillow beautifulsoup4 pymongo

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p logs web_interface/src/database

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=web_interface/src/main.py
ENV FLASK_ENV=development

# Expor porta
EXPOSE 5000

# Comando para iniciar a aplicação
CMD ["python", "web_interface/src/main.py"]