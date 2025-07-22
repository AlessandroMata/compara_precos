"""
Extrator específico para o site Mega Eletrônicos (megaeletronicos.com)
"""
import re
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse, parse_qs
from .base_extractor import BaseExtractor

logger = logging.getLogger(__name__)

class MegaEletronicosExtractor(BaseExtractor):
    """Extrator específico para Mega Eletrônicos"""
    
    def get_site_name(self) -> str:
        return "Mega Eletrônicos"
    
    def get_base_url(self) -> str:
        return "https://www.megaeletronicos.com"
    
    def get_current_exchange_rate(self) -> Optional[float]:
        """
        Extrai a cotação atual do dólar do site Mega Eletrônicos
        """
        try:
            logger.info("Extracting current USD exchange rate from Mega Eletrônicos")
            
            # Acessa a página inicial para obter a cotação
            home_data = self.crawl_page(self.get_base_url(), {
                'includeTags': ['div', 'span', 'p', 'header', 'nav'],
                'excludeTags': ['script', 'style', 'footer'],
                'waitFor': 2000
            })
            
            if not home_data:
                logger.error("Failed to crawl home page for exchange rate")
                return None
            
            # Prompt específico para extrair cotação do dólar
            exchange_prompt = """
Analise esta página do Mega Eletrônicos e encontre a cotação atual do dólar (USD).

Procure por:
- "Dólar hoje"
- "USD"
- "Cotação"
- "Câmbio"
- Valores no formato "1 USD = X.XX BRL" ou similar

RETORNE apenas um número (a cotação):
{
    "usd_to_brl": número_da_cotação
}

IMPORTANTE:
- Extraia apenas o valor numérico da cotação
- Se não encontrar, retorne null
- Formato esperado: 5.45 (exemplo)
"""
            
            # Usa IA para extrair cotação
            exchange_data = self.extract_with_ai(
                home_data.get('markdown', '') + '\n\n' + home_data.get('html', ''),
                exchange_prompt
            )
            
            if exchange_data and exchange_data.get('usd_to_brl'):
                rate = float(exchange_data['usd_to_brl'])
                logger.info(f"Found exchange rate: 1 USD = {rate} BRL")
                return rate
            
            logger.warning("Exchange rate not found on page")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting exchange rate: {str(e)}")
            return None
    
    def extract_product_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um produto específico do Mega Eletrônicos
        """
        try:
            logger.info(f"Extracting product data from: {url}")
            
            # Primeiro, obtém a cotação atual do dólar
            current_exchange_rate = self.get_current_exchange_rate()
            
            # Usa Firecrawl para obter o conteúdo da página
            page_data = self.crawl_page(url, {
                'includeTags': ['title', 'h1', 'h2', 'h3', 'p', 'span', 'div', 'img', 'meta'],
                'excludeTags': ['script', 'style', 'nav', 'footer', 'header', 'aside'],
                'waitFor': 3000
            })
            
            if not page_data:
                logger.error(f"Failed to crawl product page: {url}")
                return None
            
            # Prompt específico para extração de dados do Mega Eletrônicos
            extraction_prompt = f"""
Analise esta página de produto do Mega Eletrônicos e extraia as seguintes informações:

PRODUTO: {url}

EXTRAIR:
{{
    "codigo": "código do produto (ex: 1486179)",
    "nome": "nome completo do produto",
    "marca": "marca do produto",
    "modelo": "modelo específico",
    "categoria": "categoria do produto",
    "preco_usd": número do preço em USD,
    "preco_brl": número do preço em BRL,
    "estoque": "status do estoque (Em estoque, Fora de estoque, etc)",
    "url": "{url}",
    "especificacoes": {{
        "tela": "informações da tela",
        "memoria_ram": "quantidade de RAM",
        "memoria_interna": "armazenamento interno",
        "camera": "especificações da câmera",
        "bateria": "capacidade da bateria",
        "sistema": "sistema operacional",
        "processador": "processador/CPU",
        "gpu": "placa de vídeo/GPU",
        "conectividade": "Wi-Fi, Bluetooth, etc",
        "dimensoes": "dimensões físicas",
        "peso": "peso do produto"
    }},
    "dimensoes_embalagem": "dimensões da embalagem",
    "peso_bruto": "peso bruto em gramas",
    "garantia": "informações de garantia",
    "observacoes": "observações importantes"
}}

IMPORTANTE:
- Extraia apenas informações que estão claramente visíveis na página
- Para preços, use apenas números (ex: 84.50, não "U$ 84.50")
- Se alguma informação não estiver disponível, use null
- Mantenha o formato JSON válido
- Foque em produtos eletrônicos (celulares, tablets, notebooks, etc)
"""
            
            # Usa IA para extrair dados estruturados
            extracted_data = self.extract_with_ai(
                page_data.get('markdown', '') + '\n\n' + page_data.get('html', ''),
                extraction_prompt
            )
            
            if not extracted_data:
                logger.error("Failed to extract data with AI")
                return None
            
            # Adiciona cotação do dólar aos dados
            if current_exchange_rate:
                extracted_data['cotacao_usd_brl'] = current_exchange_rate
                
                # Recalcula preço BRL se necessário
                if extracted_data.get('preco_usd') and not extracted_data.get('preco_brl'):
                    extracted_data['preco_brl'] = extracted_data['preco_usd'] * current_exchange_rate
            
            # Valida e limpa os dados
            cleaned_data = self._clean_product_data(extracted_data)
            
            if not self.validate_product_data(cleaned_data):
                logger.error("Product data validation failed")
                return None
            
            # Adiciona metadados
            final_data = self.add_metadata(cleaned_data)
            
            logger.info(f"Successfully extracted product: {final_data.get('nome', 'Unknown')}")
            return final_data
            
        except Exception as e:
            logger.error(f"Error extracting product data: {str(e)}")
            return None
    
    def search_products(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """
        Busca produtos no Mega Eletrônicos
        """
        try:
            logger.info(f"Searching products: query='{query}', category='{category}'")
            
            # Constrói URL de busca
            search_url = f"{self.get_base_url()}/"
            if query:
                # Adiciona parâmetros de busca se necessário
                search_url += f"?search={query.replace(' ', '+')}"
            
            # Usa Firecrawl para obter resultados da busca
            search_data = self.crawl_page(search_url, {
                'includeTags': ['a', 'img', 'h1', 'h2', 'h3', 'p', 'span', 'div'],
                'excludeTags': ['script', 'style', 'nav', 'footer', 'header'],
                'waitFor': 3000
            })
            
            if not search_data:
                logger.error("Failed to crawl search page")
                return []
            
            # Prompt para extrair links de produtos
            search_prompt = f"""
Analise esta página do Mega Eletrônicos e extraia todos os links de produtos encontrados.

BUSCA: {query}
CATEGORIA: {category or 'Todas'}

Procure por:
- Links que contenham "/producto/" na URL
- Produtos relacionados à busca "{query}"
- Preços em USD e/ou BRL
- Nomes de produtos

RETORNE uma lista JSON:
[
    {{
        "nome": "nome do produto",
        "url": "URL completa do produto",
        "preco_usd": preço em USD (número),
        "preco_brl": preço em BRL (número),
        "categoria": "categoria do produto",
        "estoque": "status do estoque"
    }}
]

IMPORTANTE:
- URLs devem começar com https://www.megaeletronicos.com/producto/
- Extraia apenas produtos reais, não navegação ou outros links
- Limite a 20 produtos mais relevantes
- Use null para informações não disponíveis
"""
            
            # Usa IA para extrair lista de produtos
            products_data = self.extract_with_ai(
                search_data.get('markdown', '') + '\n\n' + search_data.get('html', ''),
                search_prompt
            )
            
            if not products_data or not isinstance(products_data, list):
                logger.warning("No products found in search results")
                return []
            
            # Limpa e valida cada produto
            cleaned_products = []
            for product in products_data:
                if isinstance(product, dict) and product.get('url'):
                    cleaned_product = self._clean_product_data(product)
                    if cleaned_product.get('url') and '/producto/' in cleaned_product['url']:
                        cleaned_products.append(self.add_metadata(cleaned_product))
            
            logger.info(f"Found {len(cleaned_products)} products")
            return cleaned_products
            
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
    
    def get_categories(self) -> List[str]:
        """
        Obtém lista de categorias disponíveis no site
        """
        try:
            logger.info("Getting available categories")
            
            home_data = self.crawl_page(self.get_base_url(), {
                'includeTags': ['nav', 'a', 'ul', 'li'],
                'excludeTags': ['script', 'style', 'footer'],
                'waitFor': 2000
            })
            
            if not home_data:
                return ['Eletrônicos', 'Telefonia', 'Casa & Cozinha', 'Perfumaria & Cosméticos']
            
            # Prompt para extrair categorias
            categories_prompt = """
Analise esta página inicial do Mega Eletrônicos e extraia todas as categorias de produtos disponíveis.

Procure por:
- Menu de navegação
- Links de categorias
- Departamentos

RETORNE uma lista JSON simples:
["Categoria 1", "Categoria 2", "Categoria 3"]

IMPORTANTE:
- Extraia apenas categorias de produtos, não links institucionais
- Mantenha nomes originais das categorias
- Limite a categorias principais
"""
            
            categories_data = self.extract_with_ai(
                home_data.get('markdown', ''),
                categories_prompt
            )
            
            if isinstance(categories_data, list):
                return categories_data
            
            # Fallback para categorias conhecidas
            return ['Eletrônicos', 'Telefonia', 'Casa & Cozinha', 'Perfumaria & Cosméticos']
            
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return ['Eletrônicos', 'Telefonia', 'Casa & Cozinha', 'Perfumaria & Cosméticos']
    
    def _clean_product_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Limpa e normaliza dados do produto
        """
        cleaned = {}
        
        # Campos obrigatórios
        cleaned['nome'] = str(data.get('nome', '')).strip()
        cleaned['url'] = str(data.get('url', '')).strip()
        
        # Preços - converte para float
        try:
            cleaned['preco_usd'] = float(data.get('preco_usd', 0))
        except (ValueError, TypeError):
            cleaned['preco_usd'] = 0.0
        
        try:
            cleaned['preco_brl'] = float(data.get('preco_brl', 0))
        except (ValueError, TypeError):
            cleaned['preco_brl'] = 0.0
        
        # Campos opcionais
        cleaned['codigo'] = str(data.get('codigo', '')).strip()
        cleaned['marca'] = str(data.get('marca', '')).strip()
        cleaned['modelo'] = str(data.get('modelo', '')).strip()
        cleaned['categoria'] = str(data.get('categoria', '')).strip()
        cleaned['estoque'] = str(data.get('estoque', '')).strip()
        
        # Especificações
        specs = data.get('especificacoes', {})
        if isinstance(specs, dict):
            cleaned['especificacoes'] = {
                k: str(v).strip() if v else None 
                for k, v in specs.items()
            }
        else:
            cleaned['especificacoes'] = {}
        
        # Outros campos
        cleaned['dimensoes_embalagem'] = str(data.get('dimensoes_embalagem', '')).strip()
        cleaned['peso_bruto'] = str(data.get('peso_bruto', '')).strip()
        cleaned['garantia'] = str(data.get('garantia', '')).strip()
        cleaned['observacoes'] = str(data.get('observacoes', '')).strip()
        
        # Remove campos vazios
        return {k: v for k, v in cleaned.items() if v}
    
    def extract_product_from_url(self, product_url: str) -> Optional[Dict[str, Any]]:
        """
        Método de conveniência para extrair produto de uma URL específica
        """
        if not product_url.startswith('http'):
            product_url = urljoin(self.get_base_url(), product_url)
        
        return self.extract_product_data(product_url)

