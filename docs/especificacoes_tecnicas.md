# Especificações Técnicas - Sistema de Extração de Preços Paraguai

## Visão Geral
Sistema inteligente para extrair preços de produtos do Paraguai (foco no Mega Eletrônicos) e calcular preços otimizados para revenda no Brasil.

## Site Principal: Mega Eletrônicos
- **URL**: https://www.megaeletronicos.com/
- **Estrutura identificada**:
  - Produtos com URLs padrão: `/producto/{id}/{nome-produto}`
  - Preços em USD e BRL
  - Informações de estoque
  - Especificações detalhadas
  - Código do produto
  - Categorias: Eletrônicos, Telefonia, Casa & Cozinha, Perfumaria

## Estrutura de Dados Extraídos

### Produto
```json
{
    "codigo": "1486179",
    "nome": "Celular Xiaomi POCO C75 NFC Dual SIM...",
    "marca": "Xiaomi",
    "modelo": "POCO C75",
    "categoria": "Smartphone",
    "preco_usd": 84.50,
    "preco_brl": 481.65,
    "estoque": "Em estoque",
    "url": "https://www.megaeletronicos.com/producto/1486179/...",
    "especificacoes": {
        "tela": "LCD de 6.88\" HD",
        "memoria_ram": "6GB",
        "memoria_interna": "128GB",
        "camera": "Principal: 50MP, Frontal: 13MP",
        "bateria": "5.160 mAh",
        "sistema": "Android 14 + HyperOS 1.0"
    },
    "dimensoes_embalagem": "9.2 x 3.7 x 18.6 cm",
    "peso": "358g",
    "data_extracao": "2025-07-21T00:00:00Z"
}
```

## Arquitetura do Sistema

### Módulos Principais

1. **Extrator (app/extractors/)**
   - `mega_eletronicos_extractor.py` - Extrator específico do Mega Eletrônicos
   - `base_extractor.py` - Classe base para outros sites
   - `product_parser.py` - Parser de dados de produtos

2. **Calculadora (app/calculators/)**
   - `price_calculator.py` - Cálculos de importação e margem
   - `currency_converter.py` - Conversão USD/PYG/BRL
   - `profit_optimizer.py` - Otimização de preços

3. **API (app/api/)**
   - `main.py` - FastAPI principal
   - `endpoints.py` - Endpoints da API
   - `models.py` - Modelos Pydantic

4. **Utilitários (app/utils/)**
   - `database.py` - Conexão com banco de dados
   - `cache.py` - Sistema de cache
   - `logger.py` - Sistema de logs

## Tecnologias

### Backend
- **Python 3.11+**
- **FastAPI** - API REST
- **BeautifulSoup4** - Web scraping
- **Requests** - HTTP requests
- **SQLAlchemy** - ORM
- **Redis** - Cache
- **Celery** - Tasks assíncronas

### Frontend (Dashboard)
- **React** - Interface
- **Material-UI** - Componentes
- **Chart.js** - Gráficos
- **Axios** - HTTP client

### Banco de Dados
- **PostgreSQL** - Dados principais
- **Redis** - Cache e sessões

## APIs Externas

### Conversão de Moedas
- **AwesomeAPI** (docs.awesomeapi.com.br)
  - Endpoint: `https://economia.awesomeapi.com.br/json/USD-BRL,USD-PYG`
  - Gratuita com limite de requests
  - Dados em tempo real

### Backup APIs
- **ExchangeRate-API**
- **Fixer.io**
- **CurrencyAPI**

## Estrutura de Dados

### Tabelas Principais

1. **produtos**
   - id, codigo, nome, marca, modelo, categoria
   - preco_usd, preco_brl, estoque, url
   - especificacoes (JSON), created_at, updated_at

2. **precos_historicos**
   - id, produto_id, preco_usd, preco_brl
   - data_coleta, fonte

3. **cotacoes**
   - id, moeda_origem, moeda_destino, taxa
   - data_cotacao, fonte

4. **calculos_importacao**
   - id, produto_id, custo_total_brl, margem_sugerida
   - preco_venda_otimo, viabilidade, created_at

## Endpoints da API

### Produtos
- `GET /api/produtos` - Lista produtos
- `GET /api/produtos/{id}` - Detalhes do produto
- `POST /api/produtos/buscar` - Busca produtos por termo
- `GET /api/produtos/categoria/{categoria}` - Produtos por categoria

### Extração
- `POST /api/extrair/mega-eletronicos` - Extrai produtos do Mega Eletrônicos
- `GET /api/extrair/status/{task_id}` - Status da extração

### Cálculos
- `POST /api/calcular/viabilidade` - Calcula viabilidade de importação
- `POST /api/calcular/preco-venda` - Calcula preço de venda otimizado
- `GET /api/cotacoes/atual` - Cotações atuais

### Oportunidades
- `GET /api/oportunidades` - Melhores oportunidades do dia
- `POST /api/monitorar` - Monitora produto específico

## Configurações

### Variáveis de Ambiente
```env
DATABASE_URL=postgresql://user:pass@localhost/paraguai_db
REDIS_URL=redis://localhost:6379
API_SECRET_KEY=your-secret-key
CURRENCY_API_KEY=your-currency-api-key
LOG_LEVEL=INFO
```

### Configuração de Scraping
```python
SCRAPING_CONFIG = {
    "delay_between_requests": 1,  # segundos
    "max_retries": 3,
    "timeout": 30,
    "user_agent": "Mozilla/5.0 (compatible; ParaguaiBot/1.0)",
    "headers": {
        "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8"
    }
}
```

## Fluxo de Funcionamento

1. **Extração**
   - Sistema acessa Mega Eletrônicos
   - Extrai dados de produtos
   - Salva no banco de dados
   - Atualiza cache

2. **Processamento**
   - Converte moedas em tempo real
   - Calcula custos de importação
   - Determina preços de venda otimizados
   - Identifica oportunidades

3. **API**
   - Serve dados via REST API
   - Fornece endpoints para integração
   - Retorna dados em JSON

4. **Dashboard**
   - Interface web para visualização
   - Gráficos e relatórios
   - Configurações do sistema

## Próximos Passos
1. Implementar extrator do Mega Eletrônicos
2. Desenvolver sistema de conversão de moedas
3. Criar API REST
4. Implementar dashboard
5. Testes e deploy

