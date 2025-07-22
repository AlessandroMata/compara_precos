FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Criar diretórios necessários
RUN mkdir -p /app/data /app/logs /app/web_interface/src/database

# Copiar requirements
COPY requirements.txt /app/
COPY web_interface/requirements.txt /app/web_interface/

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r web_interface/requirements.txt
RUN pip install --no-cache-dir Pillow beautifulsoup4 pymongo

# Copiar código da aplicação
COPY . /app/

# Criar usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash appuser
RUN chown -R appuser:appuser /app
USER appuser

# Definir variáveis de ambiente
ENV PYTHONPATH=/app
ENV FLASK_APP=web_interface/src/main.py
ENV PYTHONUNBUFFERED=1

# Health check
COPY --chown=appuser:appuser <<EOF /app/healthcheck.py
import requests
import sys
try:
    response = requests.get('http://localhost:5000/api/health', timeout=5)
    if response.status_code == 200:
        sys.exit(0)
    else:
        sys.exit(1)
except:
    sys.exit(1)
EOF

# Expor porta
EXPOSE 5000

# Comando de inicialização
CMD ["python", "web_interface/src/main.py"]