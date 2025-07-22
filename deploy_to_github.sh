#!/bin/bash

# Script para deploy gradual do projeto no GitHub
# Execute este script para fazer commits organizados

echo "🚀 Preparando deploy do Paraguai Price Extractor para GitHub"
echo "============================================================"

# Verifica se está em um repositório Git
if [ ! -d ".git" ]; then
    echo "📁 Inicializando repositório Git..."
    git init
    echo "✅ Repositório Git inicializado"
fi

# Função para fazer commit com mensagem
commit_changes() {
    local message="$1"
    local files="$2"
    
    echo "📝 Commit: $message"
    git add $files
    git commit -m "$message"
    echo "✅ Commit realizado"
    echo ""
}

# Commit 1: Estrutura base do projeto
echo "🔧 Commit 1: Estrutura base e configurações"
commit_changes "feat: estrutura base do projeto e configurações iniciais" \
    "requirements.txt .env.example docs/ app/__init__.py app/extractors/__init__.py app/analyzers/__init__.py"

# Commit 2: Sistema de extração
echo "🔧 Commit 2: Sistema de extração com Firecrawl e OpenRouter"
commit_changes "feat: implementa extrator base e específico do Mega Eletrônicos" \
    "app/extractors/base_extractor.py app/extractors/mega_eletronicos_extractor.py"

# Commit 3: Busca avançada
echo "🔧 Commit 3: Sistema de busca avançada"
commit_changes "feat: adiciona busca avançada com filtros e análise de oportunidades" \
    "app/extractors/advanced_search.py"

# Commit 4: Análise de mercado
echo "🔧 Commit 4: Analisador de mercado"
commit_changes "feat: implementa análise de mercado e comparação de preços" \
    "app/analyzers/market_analyzer.py"

# Commit 5: Interface web - Backend
echo "🔧 Commit 5: Backend da interface web"
commit_changes "feat: adiciona interface web com autenticação e API" \
    "web_interface/src/models/ web_interface/src/routes/"

# Commit 6: Interface web - Frontend
echo "🔧 Commit 6: Frontend da interface web"
commit_changes "feat: implementa interface web completa com dashboard" \
    "web_interface/src/static/"

# Commit 7: Aplicação Flask principal
echo "🔧 Commit 7: Configuração da aplicação Flask"
commit_changes "feat: configura aplicação Flask principal" \
    "web_interface/src/main.py"

# Commit 8: Scripts de teste
echo "🔧 Commit 8: Scripts de teste e utilitários"
commit_changes "feat: adiciona scripts de teste e utilitários" \
    "test_extractor.py todo.md"

# Commit 9: Documentação técnica
echo "🔧 Commit 9: Documentação técnica"
commit_changes "docs: adiciona especificações técnicas do sistema" \
    "docs/especificacoes_tecnicas.md"

echo "🎉 Todos os commits realizados!"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure o remote do GitHub:"
echo "   git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git"
echo ""
echo "2. Envie para o GitHub:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Para atualizações futuras:"
echo "   git add ."
echo "   git commit -m 'sua mensagem'"
echo "   git push"
echo ""
echo "✅ Deploy preparado com sucesso!"

