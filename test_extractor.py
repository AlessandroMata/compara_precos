#!/usr/bin/env python3
"""
Script de teste para o extrator do Mega Eletrônicos com busca avançada
"""
import os
import sys
import json
import logging
from dotenv import load_dotenv

# Adiciona o diretório app ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from extractors.mega_eletronicos_extractor import MegaEletronicosExtractor
from extractors.advanced_search import AdvancedProductSearch, SearchFilters

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def load_environment():
    """Carrega variáveis de ambiente"""
    # Carrega do .env se existir
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
    
    # Define valores padrão se não estiverem definidos
    if not os.getenv('OPENROUTER_API_KEY'):
        os.environ['OPENROUTER_API_KEY'] = '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'
    
    if not os.getenv('OPENROUTER_BASE_URL'):
        os.environ['OPENROUTER_BASE_URL'] = 'https://openrouter.ai/api/v1'
    
    if not os.getenv('OPENROUTER_MODEL'):
        os.environ['OPENROUTER_MODEL'] = 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free'
    
    if not os.getenv('SITE_URL'):
        os.environ['SITE_URL'] = 'https://paraguai-price-extractor.com'
    
    if not os.getenv('SITE_NAME'):
        os.environ['SITE_NAME'] = 'Paraguai Price Extractor'

def test_product_extraction():
    """Testa extração de produto específico"""
    print("\\n=== TESTE: Extração de Produto Específico ===")
    
    extractor = MegaEletronicosExtractor()
    
    # URL do produto Xiaomi POCO C75 fornecida pelo usuário
    product_url = "https://www.megaeletronicos.com/producto/1486179/cel-xiaomi-poco-c75-dual-6-88-6gb-128gb-lte-50mp-13mp-cx-slim-preto-2"
    
    print(f"Extraindo dados de: {product_url}")
    
    try:
        product_data = extractor.extract_product_data(product_url)
        
        if product_data:
            print("\\n✅ Extração bem-sucedida!")
            print(json.dumps(product_data, indent=2, ensure_ascii=False))
        else:
            print("\\n❌ Falha na extração")
            
    except Exception as e:
        print(f"\\n❌ Erro durante extração: {str(e)}")

def test_advanced_search():
    """Testa busca avançada com filtros"""
    print("\\n=== TESTE: Busca Avançada com Filtros ===")
    
    search_engine = AdvancedProductSearch()
    
    # Teste 1: Busca por faixa de preço
    print("\\n1. Buscando produtos entre $50 - $200:")
    try:
        filters = SearchFilters(
            min_price_usd=50,
            max_price_usd=200,
            in_stock_only=True,
            sort_by="price_asc"
        )
        
        products = search_engine.search_with_filters("smartphone", filters)
        
        if products:
            print(f"✅ Encontrados {len(products)} smartphones na faixa $50-$200")
            for i, product in enumerate(products[:3], 1):
                print(f"   {i}. {product.get('nome', 'N/A')} - ${product.get('preco_usd', 'N/A')}")
        else:
            print("❌ Nenhum produto encontrado nesta faixa")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_price_range_search():
    """Testa busca por faixa de preço específica"""
    print("\\n=== TESTE: Busca por Faixa de Preço ===")
    
    search_engine = AdvancedProductSearch()
    
    price_ranges = [
        (0, 100, "Budget (até $100)"),
        (100, 300, "Intermediário ($100-$300)"),
        (300, 500, "Premium ($300-$500)")
    ]
    
    for min_price, max_price, description in price_ranges:
        print(f"\\n🔍 {description}:")
        try:
            products = search_engine.search_by_price_range(min_price, max_price)
            
            if products:
                print(f"   ✅ {len(products)} produtos encontrados")
                # Mostra os 2 primeiros
                for product in products[:2]:
                    print(f"   • {product.get('nome', 'N/A')[:50]}... - ${product.get('preco_usd', 'N/A')}")
            else:
                print("   ❌ Nenhum produto nesta faixa")
                
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")

def test_best_opportunities():
    """Testa busca por melhores oportunidades"""
    print("\\n=== TESTE: Melhores Oportunidades ===")
    
    search_engine = AdvancedProductSearch()
    
    print("🎯 Buscando melhores oportunidades até $300:")
    try:
        opportunities = search_engine.find_best_opportunities(
            query="",  # Busca geral
            max_price_usd=300,
            min_opportunity_score=7.0
        )
        
        if opportunities:
            print(f"\\n✅ Encontradas {len(opportunities)} oportunidades!")
            
            for i, opp in enumerate(opportunities[:5], 1):  # Top 5
                product = opp.product
                print(f"\\n{i}. {product.get('nome', 'N/A')[:60]}...")
                print(f"   💰 Preço: ${product.get('preco_usd', 'N/A')}")
                print(f"   ⭐ Score: {opp.opportunity_score:.1f}/14")
                print(f"   📊 Categoria: {opp.price_category}")
                print(f"   🏆 Avaliação: {opp.value_rating}")
                if opp.recommendations:
                    print(f"   💡 Recomendação: {opp.recommendations[0]}")
        else:
            print("❌ Nenhuma oportunidade encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_price_suggestions():
    """Testa sugestões por faixa de preço"""
    print("\\n=== TESTE: Sugestões por Faixa de Preço ===")
    
    search_engine = AdvancedProductSearch()
    
    query = "tablet"
    print(f"🔍 Sugestões para '{query}' em diferentes faixas:")
    
    try:
        suggestions = search_engine.get_price_suggestions(query)
        
        if suggestions:
            for range_name, products in suggestions.items():
                print(f"\\n📱 {range_name.upper()}:")
                if products:
                    for product in products[:2]:  # Top 2 de cada faixa
                        print(f"   • {product.get('nome', 'N/A')[:50]}... - ${product.get('preco_usd', 'N/A')}")
                else:
                    print("   Nenhum produto nesta faixa")
        else:
            print("❌ Nenhuma sugestão encontrada")
            
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def interactive_search():
    """Busca interativa personalizada"""
    print("\\n=== BUSCA INTERATIVA ===")
    print("Digite suas preferências:")
    
    try:
        # Coleta preferências do usuário
        query = input("🔍 Produto desejado (ex: smartphone, tablet, notebook): ").strip()
        if not query:
            query = "smartphone"
        
        max_price = input("💰 Preço máximo em USD (ex: 200): ").strip()
        try:
            max_price = float(max_price) if max_price else 300
        except ValueError:
            max_price = 300
        
        print(f"\\n🚀 Buscando '{query}' até ${max_price}...")
        
        search_engine = AdvancedProductSearch()
        
        # Busca com filtros personalizados
        filters = SearchFilters(
            max_price_usd=max_price,
            in_stock_only=True,
            sort_by="price_asc"
        )
        
        products = search_engine.search_with_filters(query, filters)
        
        if products:
            print(f"\\n✅ Encontrados {len(products)} produtos!")
            print("\\n🏆 TOP 5 RESULTADOS:")
            
            for i, product in enumerate(products[:5], 1):
                print(f"\\n{i}. {product.get('nome', 'N/A')}")
                print(f"   💰 Preço: ${product.get('preco_usd', 'N/A')} | R${product.get('preco_brl', 'N/A')}")
                print(f"   🏪 Estoque: {product.get('estoque', 'N/A')}")
                print(f"   🔗 URL: {product.get('url', 'N/A')}")
        else:
            print("❌ Nenhum produto encontrado com esses critérios")
            
    except KeyboardInterrupt:
        print("\\n⏹️ Busca cancelada")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def main():
    """Função principal"""
    print("🚀 Sistema de Extração de Preços - Paraguai")
    print("=" * 60)
    
    # Carrega ambiente
    load_environment()
    
    # Verifica configuração
    required_keys = ['OPENROUTER_API_KEY']
    missing_keys = [key for key in required_keys if not os.getenv(key)]
    
    if missing_keys:
        print(f"❌ Chaves de API faltando: {', '.join(missing_keys)}")
        return
    
    print("✅ Configuração verificada")
    
    # Menu de opções
    while True:
        print("\\n" + "=" * 60)
        print("OPÇÕES DE TESTE:")
        print("1. Extração de produto específico")
        print("2. Busca avançada com filtros")
        print("3. Busca por faixa de preço")
        print("4. Melhores oportunidades")
        print("5. Sugestões por faixa de preço")
        print("6. Busca interativa personalizada")
        print("0. Sair")
        
        try:
            choice = input("\\nEscolha uma opção (0-6): ").strip()
            
            if choice == "0":
                break
            elif choice == "1":
                test_product_extraction()
            elif choice == "2":
                test_advanced_search()
            elif choice == "3":
                test_price_range_search()
            elif choice == "4":
                test_best_opportunities()
            elif choice == "5":
                test_price_suggestions()
            elif choice == "6":
                interactive_search()
            else:
                print("❌ Opção inválida")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
    
    print("\\n🏁 Sistema finalizado")

if __name__ == "__main__":
    main()

