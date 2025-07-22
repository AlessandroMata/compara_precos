"""
Analisador de mercado para comparação de preços e análise de oportunidades
"""
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)

@dataclass
class MarketPrice:
    """Preço encontrado no mercado"""
    source: str
    price_brl: float
    url: str
    seller: str
    condition: str  # "new", "used", "refurbished"
    availability: str  # "in_stock", "out_of_stock", "limited"
    shipping_cost: Optional[float] = None
    found_at: datetime = None

@dataclass
class MarketAnalysis:
    """Análise completa de mercado"""
    product_name: str
    source_price_usd: float
    source_price_brl: float
    
    # Preços de mercado
    official_market: List[MarketPrice]
    gray_market: List[MarketPrice]
    
    # Análise de preços
    official_min_price: Optional[float]
    official_max_price: Optional[float]
    official_avg_price: Optional[float]
    
    gray_min_price: Optional[float]
    gray_max_price: Optional[float]
    gray_avg_price: Optional[float]
    
    # Custos estimados
    import_cost_estimate: float
    total_cost_estimate: float
    
    # Sugestões de preço
    suggested_prices: Dict[str, float]
    
    # Análise de oportunidade
    opportunity_score: float
    market_position: str  # "premium", "competitive", "budget"
    recommendations: List[str]

class MarketAnalyzer:
    """Analisador de mercado brasileiro"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Sites para busca de preços oficiais
        self.official_sites = [
            'mercadolivre.com.br',
            'americanas.com.br',
            'casasbahia.com.br',
            'extra.com.br',
            'magazineluiza.com.br',
            'submarino.com.br'
        ]
        
        # Sites para mercado cinza
        self.gray_market_sites = [
            'aliexpress.com',
            'shopee.com.br',
            'wish.com'
        ]
    
    def analyze_product_market(self, product_data: Dict[str, Any]) -> MarketAnalysis:
        """
        Analisa o mercado para um produto específico
        """
        try:
            logger.info(f"Analyzing market for: {product_data.get('nome', 'Unknown')}")
            
            product_name = product_data.get('nome', '')
            source_price_usd = product_data.get('preco_usd', 0)
            source_price_brl = product_data.get('preco_brl', 0)
            
            # Busca preços no mercado oficial
            official_prices = self._search_official_market(product_name)
            
            # Busca preços no mercado cinza
            gray_prices = self._search_gray_market(product_name)
            
            # Calcula estatísticas de preços
            official_stats = self._calculate_price_stats(official_prices)
            gray_stats = self._calculate_price_stats(gray_prices)
            
            # Estima custos de importação
            import_costs = self._estimate_import_costs(source_price_usd)
            
            # Sugere preços de venda
            suggested_prices = self._suggest_selling_prices(
                source_price_usd, 
                import_costs,
                official_stats,
                gray_stats
            )
            
            # Calcula score de oportunidade
            opportunity_score = self._calculate_opportunity_score(
                source_price_usd,
                import_costs,
                official_stats,
                gray_stats
            )
            
            # Determina posicionamento de mercado
            market_position = self._determine_market_position(
                import_costs['total_cost'],
                official_stats,
                gray_stats
            )
            
            # Gera recomendações
            recommendations = self._generate_recommendations(
                opportunity_score,
                market_position,
                official_stats,
                gray_stats,
                import_costs
            )
            
            return MarketAnalysis(
                product_name=product_name,
                source_price_usd=source_price_usd,
                source_price_brl=source_price_brl,
                official_market=official_prices,
                gray_market=gray_prices,
                official_min_price=official_stats.get('min'),
                official_max_price=official_stats.get('max'),
                official_avg_price=official_stats.get('avg'),
                gray_min_price=gray_stats.get('min'),
                gray_max_price=gray_stats.get('max'),
                gray_avg_price=gray_stats.get('avg'),
                import_cost_estimate=import_costs['import_cost'],
                total_cost_estimate=import_costs['total_cost'],
                suggested_prices=suggested_prices,
                opportunity_score=opportunity_score,
                market_position=market_position,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing market: {str(e)}")
            return None
    
    def _search_official_market(self, product_name: str) -> List[MarketPrice]:
        """
        Busca preços no mercado oficial brasileiro
        """
        prices = []
        
        try:
            # Busca no Mercado Livre (principal)
            ml_prices = self._search_mercadolivre(product_name)
            prices.extend(ml_prices)
            
            # Busca em outros sites (simulado por enquanto)
            # Em implementação real, você faria scraping de cada site
            
            return prices[:10]  # Limita a 10 resultados
            
        except Exception as e:
            logger.error(f"Error searching official market: {str(e)}")
            return []
    
    def _search_gray_market(self, product_name: str) -> List[MarketPrice]:
        """
        Busca preços no mercado cinza
        """
        prices = []
        
        try:
            # Simulação de busca no mercado cinza
            # Em implementação real, buscaria em AliExpress, Shopee, etc.
            
            # Por enquanto, retorna preços estimados baseados no produto
            estimated_prices = self._estimate_gray_market_prices(product_name)
            prices.extend(estimated_prices)
            
            return prices
            
        except Exception as e:
            logger.error(f"Error searching gray market: {str(e)}")
            return []
    
    def _search_mercadolivre(self, product_name: str) -> List[MarketPrice]:
        """
        Busca específica no Mercado Livre
        """
        prices = []
        
        try:
            # Limpa o nome do produto para busca
            search_query = self._clean_product_name(product_name)
            
            # URL de busca do Mercado Livre
            url = f"https://lista.mercadolivre.com.br/{search_query.replace(' ', '-')}"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extrai produtos (estrutura simplificada)
                products = soup.find_all('div', class_='ui-search-result__wrapper')
                
                for product in products[:5]:  # Primeiros 5 resultados
                    try:
                        # Extrai preço
                        price_elem = product.find('span', class_='price-tag-fraction')
                        if price_elem:
                            price_text = price_elem.get_text().strip()
                            price = float(re.sub(r'[^\d,]', '', price_text).replace(',', '.'))
                            
                            # Extrai título
                            title_elem = product.find('h2', class_='ui-search-item__title')
                            title = title_elem.get_text().strip() if title_elem else "Produto"
                            
                            # Extrai URL
                            link_elem = product.find('a', class_='ui-search-link')
                            product_url = link_elem.get('href') if link_elem else ""
                            
                            prices.append(MarketPrice(
                                source="Mercado Livre",
                                price_brl=price,
                                url=product_url,
                                seller="Mercado Livre",
                                condition="new",
                                availability="in_stock",
                                found_at=datetime.now()
                            ))
                            
                    except Exception as e:
                        logger.warning(f"Error parsing ML product: {str(e)}")
                        continue
            
            time.sleep(1)  # Rate limiting
            
        except Exception as e:
            logger.error(f"Error searching Mercado Livre: {str(e)}")
        
        return prices
    
    def _estimate_gray_market_prices(self, product_name: str) -> List[MarketPrice]:
        """
        Estima preços do mercado cinza baseado em padrões conhecidos
        """
        prices = []
        
        # Estimativas baseadas em categorias
        if any(term in product_name.lower() for term in ['smartphone', 'celular']):
            base_prices = [299, 399, 499, 599, 799]
        elif any(term in product_name.lower() for term in ['tablet']):
            base_prices = [199, 299, 399, 499]
        elif any(term in product_name.lower() for term in ['notebook', 'laptop']):
            base_prices = [899, 1299, 1599, 1999]
        else:
            base_prices = [99, 199, 299, 499]
        
        sources = ['AliExpress', 'Shopee', 'Wish']
        
        for i, price in enumerate(base_prices[:3]):
            prices.append(MarketPrice(
                source=sources[i % len(sources)],
                price_brl=price,
                url=f"https://example.com/product-{i}",
                seller=sources[i % len(sources)],
                condition="new",
                availability="in_stock",
                found_at=datetime.now()
            ))
        
        return prices
    
    def _calculate_price_stats(self, prices: List[MarketPrice]) -> Dict[str, float]:
        """
        Calcula estatísticas de preços
        """
        if not prices:
            return {'min': None, 'max': None, 'avg': None, 'count': 0}
        
        price_values = [p.price_brl for p in prices]
        
        return {
            'min': min(price_values),
            'max': max(price_values),
            'avg': sum(price_values) / len(price_values),
            'count': len(price_values)
        }
    
    def _estimate_import_costs(self, price_usd: float, exchange_rate: float = None) -> Dict[str, float]:
        """
        Estima custos de importação usando cotação real ou estimada
        """
        # Usa cotação fornecida ou estimativa
        if exchange_rate is None:
            exchange_rate = 5.5  # Fallback
        
        # Preço em BRL
        price_brl = price_usd * exchange_rate
        
        # Impostos e taxas (estimativa)
        import_tax = price_brl * 0.60  # 60% de impostos
        shipping = 50  # Frete estimado
        handling = 30  # Taxa de manuseio
        
        import_cost = import_tax + shipping + handling
        total_cost = price_brl + import_cost
        
        return {
            'exchange_rate': exchange_rate,
            'price_brl': price_brl,
            'import_tax': import_tax,
            'shipping': shipping,
            'handling': handling,
            'import_cost': import_cost,
            'total_cost': total_cost
        }
    
    def _suggest_selling_prices(self, 
                              source_price_usd: float,
                              import_costs: Dict[str, float],
                              official_stats: Dict[str, float],
                              gray_stats: Dict[str, float]) -> Dict[str, float]:
        """
        Sugere preços de venda baseado na análise de mercado
        """
        total_cost = import_costs['total_cost']
        
        suggestions = {}
        
        # Preço competitivo (margem de 30%)
        suggestions['competitive'] = total_cost * 1.30
        
        # Preço premium (margem de 50%)
        suggestions['premium'] = total_cost * 1.50
        
        # Preço agressivo (margem de 20%)
        suggestions['aggressive'] = total_cost * 1.20
        
        # Baseado no mercado oficial
        if official_stats.get('avg'):
            suggestions['market_based'] = official_stats['avg'] * 0.85  # 15% abaixo da média
        
        # Baseado no mercado cinza
        if gray_stats.get('avg'):
            suggestions['gray_competitive'] = gray_stats['avg'] * 1.10  # 10% acima do mercado cinza
        
        return suggestions
    
    def _calculate_opportunity_score(self,
                                   source_price_usd: float,
                                   import_costs: Dict[str, float],
                                   official_stats: Dict[str, float],
                                   gray_stats: Dict[str, float]) -> float:
        """
        Calcula score de oportunidade (0-10)
        """
        score = 0
        
        total_cost = import_costs['total_cost']
        
        # Score baseado na margem potencial
        if official_stats.get('avg'):
            potential_margin = (official_stats['avg'] - total_cost) / total_cost
            if potential_margin > 1.0:  # Margem > 100%
                score += 4
            elif potential_margin > 0.5:  # Margem > 50%
                score += 3
            elif potential_margin > 0.3:  # Margem > 30%
                score += 2
            elif potential_margin > 0.1:  # Margem > 10%
                score += 1
        
        # Score baseado na competitividade
        if gray_stats.get('avg'):
            if total_cost < gray_stats['avg'] * 0.8:  # 20% mais barato que mercado cinza
                score += 3
            elif total_cost < gray_stats['avg']:
                score += 2
        
        # Score baseado no preço fonte
        if source_price_usd < 100:
            score += 2  # Produtos mais baratos são mais fáceis de vender
        elif source_price_usd < 300:
            score += 1
        
        # Score baseado na disponibilidade de dados
        if official_stats.get('count', 0) > 0:
            score += 1
        
        return min(score, 10)  # Máximo 10
    
    def _determine_market_position(self,
                                 total_cost: float,
                                 official_stats: Dict[str, float],
                                 gray_stats: Dict[str, float]) -> str:
        """
        Determina posicionamento de mercado
        """
        if not official_stats.get('avg'):
            return "unknown"
        
        avg_official = official_stats['avg']
        
        if total_cost * 1.3 < avg_official * 0.7:  # Muito abaixo do mercado
            return "budget"
        elif total_cost * 1.3 < avg_official:  # Abaixo do mercado
            return "competitive"
        else:  # Acima do mercado
            return "premium"
    
    def _generate_recommendations(self,
                                opportunity_score: float,
                                market_position: str,
                                official_stats: Dict[str, float],
                                gray_stats: Dict[str, float],
                                import_costs: Dict[str, float]) -> List[str]:
        """
        Gera recomendações baseadas na análise
        """
        recommendations = []
        
        if opportunity_score >= 8:
            recommendations.append("🟢 Excelente oportunidade! Alta margem de lucro.")
        elif opportunity_score >= 6:
            recommendations.append("🟡 Boa oportunidade com margem interessante.")
        elif opportunity_score >= 4:
            recommendations.append("🟠 Oportunidade moderada. Analise custos adicionais.")
        else:
            recommendations.append("🔴 Baixa margem. Considere outros produtos.")
        
        if market_position == "budget":
            recommendations.append("💰 Posicionamento competitivo no mercado.")
        elif market_position == "premium":
            recommendations.append("⚠️ Preço alto comparado ao mercado. Justifique o valor.")
        
        if official_stats.get('count', 0) == 0:
            recommendations.append("🔍 Produto com pouca concorrência no mercado oficial.")
        
        if import_costs['total_cost'] > 1000:
            recommendations.append("📊 Produto de alto valor. Considere estratégia de marketing premium.")
        
        return recommendations
    
    def _clean_product_name(self, name: str) -> str:
        """
        Limpa nome do produto para busca
        """
        # Remove caracteres especiais e normaliza
        cleaned = re.sub(r'[^\w\s-]', '', name)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove palavras muito específicas que podem atrapalhar a busca
        stop_words = ['cel', 'smartphone', 'dual', 'sim', 'lte', 'cx', 'slim']
        words = cleaned.split()
        filtered_words = [w for w in words if w.lower() not in stop_words]
        
        return ' '.join(filtered_words[:5])  # Máximo 5 palavras

