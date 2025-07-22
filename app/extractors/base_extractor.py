"""
Classe base para extratores de sites paraguaios
"""
import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
from firecrawl import FirecrawlApp
from openai import OpenAI

logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    """Classe base para todos os extratores de sites paraguaios"""
    
    def __init__(self):
        # Configuração para Firecrawl local ou fallback
        firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY', 'local-fallback')
        firecrawl_base_url = os.getenv('FIRECRAWL_BASE_URL', 'http://localhost:3002')
        
        # Inicializa Firecrawl com fallback
        try:
            if firecrawl_base_url and firecrawl_base_url != 'https://api.firecrawl.dev':
                self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key, api_url=firecrawl_base_url)
            else:
                self.firecrawl = FirecrawlApp(api_key=firecrawl_api_key)
            self.firecrawl_available = True
        except Exception as e:
            logger.warning(f"Firecrawl not available: {e}")
            self.firecrawl = None
            self.firecrawl_available = False
            
        # Cliente OpenAI/OpenRouter para análise IA (opcional)
        openai_key = os.getenv('OPENROUTER_API_KEY')
        if openai_key:
            self.openai_client = OpenAI(
                base_url=os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1'),
                api_key=openai_key
            )
        else:
            self.openai_client = None
        self.ai_model = os.getenv('OPENROUTER_MODEL', 'cognitivecomputations/dolphin-mistral-24b-venice-edition:free')
        self.site_url = os.getenv('SITE_URL', 'https://paraguai-price-extractor.com')
        self.site_name = os.getenv('SITE_NAME', 'Paraguai Price Extractor')
        self.delay = int(os.getenv('SCRAPING_DELAY', 1))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
        
    @abstractmethod
    def get_site_name(self) -> str:
        """Retorna o nome do site"""
        pass
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Retorna a URL base do site"""
        pass
    
    @abstractmethod
    def extract_product_data(self, url: str) -> Optional[Dict[str, Any]]:
        """Extrai dados de um produto específico"""
        pass
    
    @abstractmethod
    def search_products(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        """Busca produtos no site"""
        pass
    
    def crawl_page(self, url: str, extract_options: Dict = None) -> Optional[Dict]:
        """
        Usa Firecrawl para extrair dados de uma página, com fallback para requests
        """
        # Se Firecrawl estiver disponível, usar ele
        if self.firecrawl_available:
            try:
                logger.info(f"Crawling page with Firecrawl: {url}")
                
                default_options = {
                    'formats': ['markdown', 'html'],
                    'includeTags': ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'span', 'div', 'img'],
                    'excludeTags': ['script', 'style', 'nav', 'footer', 'header'],
                    'waitFor': 2000,
                    'timeout': self.timeout * 1000
                }
                
                if extract_options:
                    default_options.update(extract_options)
                
                result = self.firecrawl.scrape_url(url, params=default_options)
                
                if result and 'success' in result and result['success']:
                    return result['data']
                else:
                    logger.error(f"Failed to crawl {url} with Firecrawl: {result}")
                    
            except Exception as e:
                logger.warning(f"Firecrawl failed for {url}: {str(e)}")
        
        # Fallback: usar requests + BeautifulSoup
        return self._crawl_with_requests(url)
    
    def _crawl_with_requests(self, url: str) -> Optional[Dict]:
        """
        Fallback para web scraping usando requests + BeautifulSoup
        """
        try:
            logger.info(f"Crawling page with requests fallback: {url}")
            import requests
            from bs4 import BeautifulSoup
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrai URLs de imagens
            image_urls = []
            for img in soup.find_all('img'):
                img_src = img.get('src') or img.get('data-src')
                if img_src:
                    # Converte URLs relativas para absolutas
                    from urllib.parse import urljoin
                    absolute_url = urljoin(url, img_src)
                    image_urls.append(absolute_url)
            
            # Remove elementos desnecessários
            for element in soup(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Extrai texto markdown simplificado
            text_content = soup.get_text(separator='\n', strip=True)
            
            return {
                'markdown': text_content,
                'html': str(soup),
                'images': image_urls[:5],  # Máximo 5 imagens por produto
                'metadata': {
                    'title': soup.title.string if soup.title else '',
                    'url': url,
                    'statusCode': response.status_code
                }
            }
            
        except Exception as e:
            logger.error(f"Error in requests fallback for {url}: {str(e)}")
            return None
    
    def extract_with_ai(self, content: str, extraction_prompt: str) -> Optional[Dict]:
        """
        Usa OpenRouter para extrair dados estruturados do conteúdo
        """
        try:
            logger.info("Using AI to extract structured data")
            
            response = self.openai_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.site_name,
                },
                model=self.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um especialista em extração de dados de e-commerce paraguaio. Extraia informações precisas e retorne sempre em formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": f"{extraction_prompt}\n\nConteúdo da página:\n{content}"
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Tenta extrair JSON do resultado
            import json
            import re
            
            # Procura por JSON no texto
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    logger.error("Failed to parse JSON from AI response")
                    return None
            
            logger.error("No JSON found in AI response")
            return None
            
        except Exception as e:
            logger.error(f"Error in AI extraction: {str(e)}")
            return None
    
    def validate_product_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida se os dados do produto estão completos
        """
        required_fields = ['nome', 'preco_usd', 'url']
        
        for field in required_fields:
            if field not in data or not data[field]:
                logger.warning(f"Missing required field: {field}")
                return False
        
        # Valida se o preço é um número válido
        try:
            float(data['preco_usd'])
        except (ValueError, TypeError):
            logger.warning(f"Invalid price: {data.get('preco_usd')}")
            return False
        
        return True
    
    def add_metadata(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adiciona metadados aos dados extraídos
        """
        data['site'] = self.get_site_name()
        data['data_extracao'] = datetime.now().isoformat()
        data['extrator_versao'] = '1.0'
        
        return data
    
    def download_and_encode_image(self, image_url: str) -> Optional[str]:
        """
        Baixa uma imagem e converte para base64
        """
        try:
            logger.info(f"Downloading image: {image_url}")
            import requests
            import base64
            from PIL import Image
            from io import BytesIO
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Abre e redimensiona a imagem
            image = Image.open(BytesIO(response.content))
            
            # Redimensiona para economizar espaço (máximo 400x400)
            image.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            # Converte para RGB se necessário
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Salva como JPEG em memória
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # Converte para base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            
            logger.info(f"Image downloaded and encoded: {len(image_base64)} characters")
            return f"data:image/jpeg;base64,{image_base64}"
            
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {str(e)}")
            return None
    
    def retry_on_failure(self, func, *args, **kwargs):
        """
        Executa uma função com retry em caso de falha
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Backoff exponencial
        
        return None

