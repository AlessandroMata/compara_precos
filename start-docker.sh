#!/bin/bash

echo "🐳 Iniciando Paraguai Price Extractor com Docker..."
echo "=" * 60

# Para qualquer container em execução
docker compose down

# Remove volumes antigos (opcional - descomente se quiser limpar tudo)
# docker compose down -v

# Constrói as imagens
echo "🔨 Construindo imagens..."
docker compose build

# Inicia os serviços
echo "🚀 Iniciando serviços..."
docker compose up -d

echo ""
echo "⏳ Aguardando serviços ficarem prontos..."
sleep 30

# Verifica status dos serviços
echo ""
echo "📊 Status dos serviços:"
docker compose ps

echo ""
echo "🌐 Testando conectividade..."
echo "- Firecrawl: http://localhost:3002"
echo "- MongoDB: localhost:27017" 
echo "- Redis: localhost:6379"
echo "- App Principal: http://localhost:5000"

echo ""
echo "🔍 Testando health check..."
curl -s http://localhost:5000/api/health | jq '.' || echo "Aguardando app inicializar..."

echo ""
echo "📋 Para ver os logs:"
echo "docker compose logs -f paraguai-app"
echo ""
echo "🛑 Para parar tudo:"
echo "docker compose down"
echo ""
echo "🎯 Acesso ao sistema:"
echo "URL: http://localhost:5000"
echo "Login: admin"
echo "Senha: admin123"