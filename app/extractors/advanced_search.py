"""
Módulo de busca avançada com filtros de preço e análise de oportunidades
"""
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from .mega_eletronicos_extractor import MegaEletronicosExtractor

logger = logging.getLogger(__name__)

@dataclass
class SearchFilters:
    """Filtros para busca avançada"""
    min_price_usd: Optional[float] = None
    max_price_usd: Optional[float] = None
    min_price_brl: Optional[float] = None
    max_price_brl: Optional[float] = None
    categories: Optional[List[str]] = None
    brands: Optional[List[str]] = None
    in_stock_only: bool = True
    sort_by: str = "price_asc"  # price_asc, price_desc, name, relevance

@dataclass
class OpportunityAnalysis:
    """Análise de oportunidade de um produto"""
    product: Dict[str, Any]
    opportunity_score: float
    price_category: str  # "budget", "mid_range", "premium"
    value_rating: str   # "excellent", "good", "fair", "poor"
    recommendations: List[str]

class AdvancedProductSearch:
    """Sistema de busca avançada de produtos"""
    
    def __init__(self):
        self.extractor = MegaEletronicosExtractor()
        
    def search_with_filters(self, 
                          query: str, 
                          filters: SearchFilters) -> List[Dict[str, Any]]:
        """
        Busca produtos com filtros avançados
        """
        try:
            logger.info(f"Advanced search: '{query}' with filters")
            
            # Busca inicial
            all_products = self.extractor.search_products(query)
            
            if not all_products:
                logger.warning("No products found in initial search")
                return []
            
            # Aplica filtros
            filtered_products = self._apply_filters(all_products, filters)
            
            # Ordena resultados
            sorted_products = self._sort_products(filtered_products, filters.sort_by)
            
            logger.info(f"Found {len(sorted_products)} products after filtering")
            return sorted_products
            
        except Exception as e:
            logger.error(f"Error in advanced search: {str(e)}")
            return []
    
    def find_best_opportunities(self, 
                              query: str = "", 
                              max_price_usd: float = 500,
                              min_opportunity_score: float = 7.0) -> List[OpportunityAnalysis]:
        """
        Encontra as melhores oportunidades de produtos
        """
        try:
            logger.info(f"Finding best opportunities: query='{query}', max_price=${max_price_usd}")
            
            # Define filtros para oportunidades
            filters = SearchFilters(
                max_price_usd=max_price_usd,
                in_stock_only=True,
                sort_by="price_asc"
            )
            
            # Busca produtos
            if query:
                products = self.search_with_filters(query, filters)
            else:
                # Busca em categorias populares se não há query específica
                products = self._search_popular_categories(filters)
            
            # Analisa oportunidades
            opportunities = []
            for product in products:
                analysis = self._analyze_opportunity(product)
                if analysis.opportunity_score >= min_opportunity_score:
                    opportunities.append(analysis)
            
            # Ordena por score de oportunidade
            opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)
            
            logger.info(f"Found {len(opportunities)} good opportunities")
            return opportunities[:20]  # Retorna top 20
            
        except Exception as e:
            logger.error(f"Error finding opportunities: {str(e)}")
            return []
    
    def search_by_price_range(self, 
                            min_usd: float, 
                            max_usd: float,
                            category: str = None) -> List[Dict[str, Any]]:
        """
        Busca produtos por faixa de preço específica
        """
        try:
            logger.info(f"Searching by price range: ${min_usd} - ${max_usd}")
            
            filters = SearchFilters(
                min_price_usd=min_usd,
                max_price_usd=max_usd,
                categories=[category] if category else None,
                sort_by="price_asc"
            )
            
            # Busca em todas as categorias se não especificada
            if category:
                products = self.search_with_filters("", filters)
            else:
                products = self._search_all_categories(filters)
            
            return products
            
        except Exception as e:
            logger.error(f"Error searching by price range: {str(e)}")
            return []
    
    def get_price_suggestions(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna sugestões de produtos em diferentes faixas de preço
        """
        try:
            logger.info(f"Getting price suggestions for: '{query}'")
            
            price_ranges = {
                "budget": (0, 100),      # Até $100
                "mid_range": (100, 300), # $100 - $300
                "premium": (300, 1000)   # $300 - $1000
            }
            
            suggestions = {}
            
            for range_name, (min_price, max_price) in price_ranges.items():
                filters = SearchFilters(
                    min_price_usd=min_price,
                    max_price_usd=max_price,
                    sort_by="price_asc"
                )
                
                products = self.search_with_filters(query, filters)
                suggestions[range_name] = products[:5]  # Top 5 em cada faixa
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting price suggestions: {str(e)}")
            return {}
    
    def _apply_filters(self, products: List[Dict[str, Any]], filters: SearchFilters) -> List[Dict[str, Any]]:
        """Aplica filtros aos produtos"""
        filtered = products
        
        # Filtro de preço USD
        if filters.min_price_usd is not None:
            filtered = [p for p in filtered if p.get('preco_usd', 0) >= filters.min_price_usd]
        
        if filters.max_price_usd is not None:
            filtered = [p for p in filtered if p.get('preco_usd', 0) <= filters.max_price_usd]
        
        # Filtro de preço BRL
        if filters.min_price_brl is not None:
            filtered = [p for p in filtered if p.get('preco_brl', 0) >= filters.min_price_brl]
        
        if filters.max_price_brl is not None:
            filtered = [p for p in filtered if p.get('preco_brl', 0) <= filters.max_price_brl]
        
        # Filtro de categoria
        if filters.categories:
            filtered = [p for p in filtered if p.get('categoria', '').lower() in 
                       [c.lower() for c in filters.categories]]
        
        # Filtro de marca
        if filters.brands:
            filtered = [p for p in filtered if p.get('marca', '').lower() in 
                       [b.lower() for b in filters.brands]]
        
        # Filtro de estoque
        if filters.in_stock_only:
            filtered = [p for p in filtered if 'estoque' in p.get('estoque', '').lower()]
        
        return filtered
    
    def _sort_products(self, products: List[Dict[str, Any]], sort_by: str) -> List[Dict[str, Any]]:
        """Ordena produtos conforme critério"""
        if sort_by == "price_asc":
            return sorted(products, key=lambda x: x.get('preco_usd', 0))
        elif sort_by == "price_desc":
            return sorted(products, key=lambda x: x.get('preco_usd', 0), reverse=True)
        elif sort_by == "name":
            return sorted(products, key=lambda x: x.get('nome', ''))
        else:  # relevance (default order)
            return products
    
    def _search_popular_categories(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Busca em categorias populares"""
        popular_categories = ["smartphone", "tablet", "notebook", "smartwatch", "fone"]
        all_products = []
        
        for category in popular_categories:
            try:
                products = self.search_with_filters(category, filters)
                all_products.extend(products[:10])  # Top 10 de cada categoria
            except Exception as e:
                logger.warning(f"Error searching category {category}: {str(e)}")
        
        return all_products
    
    def _search_all_categories(self, filters: SearchFilters) -> List[Dict[str, Any]]:
        """Busca em todas as categorias disponíveis"""
        try:
            categories = self.extractor.get_categories()
            all_products = []
            
            for category in categories:
                try:
                    # Busca produtos da categoria
                    products = self.search_with_filters("", filters)
                    all_products.extend(products)
                except Exception as e:
                    logger.warning(f"Error searching category {category}: {str(e)}")
            
            return all_products
            
        except Exception as e:
            logger.error(f"Error searching all categories: {str(e)}")
            return []
    
    def _analyze_opportunity(self, product: Dict[str, Any]) -> OpportunityAnalysis:
        """Analisa oportunidade de um produto"""
        try:
            price_usd = product.get('preco_usd', 0)
            price_brl = product.get('preco_brl', 0)
            
            # Calcula score base no preço
            if price_usd <= 50:
                price_score = 10
                price_category = "budget"
            elif price_usd <= 200:
                price_score = 8
                price_category = "mid_range"
            elif price_usd <= 500:
                price_score = 6
                price_category = "premium"
            else:
                price_score = 4
                price_category = "premium"
            
            # Fatores adicionais
            stock_score = 2 if 'estoque' in product.get('estoque', '').lower() else 0
            brand_score = 2 if product.get('marca', '').lower() in ['xiaomi', 'samsung', 'apple', 'lg'] else 1
            
            # Score final
            opportunity_score = price_score + stock_score + brand_score
            
            # Rating de valor
            if opportunity_score >= 12:
                value_rating = "excellent"
            elif opportunity_score >= 10:
                value_rating = "good"
            elif opportunity_score >= 8:
                value_rating = "fair"
            else:
                value_rating = "poor"
            
            # Recomendações
            recommendations = []
            if price_usd < 100:
                recommendations.append("Excelente preço para importação")
            if 'estoque' in product.get('estoque', '').lower():
                recommendations.append("Produto disponível em estoque")
            if price_brl > 0 and price_usd > 0:
                ratio = price_brl / (price_usd * 5.5)  # Estimativa de câmbio
                if ratio < 1.2:
                    recommendations.append("Preço muito competitivo vs Brasil")
            
            return OpportunityAnalysis(
                product=product,
                opportunity_score=opportunity_score,
                price_category=price_category,
                value_rating=value_rating,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error analyzing opportunity: {str(e)}")
            return OpportunityAnalysis(
                product=product,
                opportunity_score=0,
                price_category="unknown",
                value_rating="poor",
                recommendations=[]
            )

