"""
Rotas para o wizard de busca e gerenciamento de buscas fixas
"""
import os
import sys
import json
import uuid
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# Adiciona o diretório pai ao path para importar os extractors
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from app.extractors.mega_eletronicos_extractor import MegaEletronicosExtractor
from app.extractors.advanced_search import AdvancedProductSearch, SearchFilters
from src.models.search_config import db, SearchConfig, SavedProduct

search_wizard_bp = Blueprint('search_wizard', __name__)

# Instância global do extrator
extractor = MegaEletronicosExtractor()
advanced_search = AdvancedProductSearch()

@search_wizard_bp.route('/wizard/step1', methods=['POST'])
def wizard_step1():
    """
    Passo 1: Configuração básica da busca
    """
    try:
        data = request.get_json()
        
        # Validação dos dados
        required_fields = ['search_name', 'product_query']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Cria configuração temporária
        temp_config = {
            'id': str(uuid.uuid4()),
            'search_name': data['search_name'],
            'product_query': data['product_query'],
            'min_price_usd': data.get('min_price_usd'),
            'max_price_usd': data.get('max_price_usd'),
            'categories': data.get('categories', []),
            'brands': data.get('brands', []),
            'in_stock_only': data.get('in_stock_only', True),
            'sort_by': data.get('sort_by', 'price_asc'),
            'status': 'draft'
        }
        
        return jsonify({
            'success': True,
            'config': temp_config,
            'message': 'Configuração inicial salva. Prossiga para o teste.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/wizard/step2/test', methods=['POST'])
def wizard_step2_test():
    """
    Passo 2: Testa a busca com os parâmetros configurados
    """
    try:
        data = request.get_json()
        config = data.get('config')
        
        if not config:
            return jsonify({'error': 'Configuração não fornecida'}), 400
        
        # Cria filtros baseados na configuração
        filters = SearchFilters(
            min_price_usd=config.get('min_price_usd'),
            max_price_usd=config.get('max_price_usd'),
            categories=config.get('categories'),
            brands=config.get('brands'),
            in_stock_only=config.get('in_stock_only', True),
            sort_by=config.get('sort_by', 'price_asc')
        )
        
        # Executa a busca
        products = advanced_search.search_with_filters(
            config['product_query'], 
            filters
        )
        
        # Limita a 20 produtos para o teste
        test_products = products[:20]
        
        # Calcula estatísticas
        stats = {
            'total_found': len(products),
            'showing': len(test_products),
            'price_range': {
                'min': min([p.get('preco_usd', 0) for p in test_products]) if test_products else 0,
                'max': max([p.get('preco_usd', 0) for p in test_products]) if test_products else 0
            },
            'categories': list(set([p.get('categoria', 'N/A') for p in test_products])),
            'brands': list(set([p.get('marca', 'N/A') for p in test_products]))
        }
        
        return jsonify({
            'success': True,
            'products': test_products,
            'stats': stats,
            'message': f'Encontrados {len(products)} produtos. Mostrando os primeiros {len(test_products)}.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/wizard/step3/approve', methods=['POST'])
def wizard_step3_approve():
    """
    Passo 3: Aprova a busca e cria monitoramento fixo
    """
    try:
        data = request.get_json()
        config = data.get('config')
        approved_products = data.get('approved_products', [])
        
        if not config:
            return jsonify({'error': 'Configuração não fornecida'}), 400
        
        # Cria registro no banco de dados
        search_config = SearchConfig(
            name=config['search_name'],
            query=config['product_query'],
            min_price_usd=config.get('min_price_usd'),
            max_price_usd=config.get('max_price_usd'),
            categories=json.dumps(config.get('categories', [])),
            brands=json.dumps(config.get('brands', [])),
            in_stock_only=config.get('in_stock_only', True),
            sort_by=config.get('sort_by', 'price_asc'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(search_config)
        db.session.flush()  # Para obter o ID
        
        # Salva produtos aprovados
        for product_data in approved_products:
            saved_product = SavedProduct(
                search_config_id=search_config.id,
                product_data=json.dumps(product_data),
                created_at=datetime.utcnow()
            )
            db.session.add(saved_product)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'search_id': search_config.id,
            'message': f'Busca "{config["search_name"]}" aprovada e ativada! {len(approved_products)} produtos salvos.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/searches', methods=['GET'])
def get_saved_searches():
    """
    Lista todas as buscas salvas
    """
    try:
        searches = SearchConfig.query.all()
        
        search_list = []
        for search in searches:
            # Conta produtos salvos
            product_count = SavedProduct.query.filter_by(search_config_id=search.id).count()
            
            search_data = {
                'id': search.id,
                'name': search.name,
                'query': search.query,
                'min_price_usd': search.min_price_usd,
                'max_price_usd': search.max_price_usd,
                'is_active': search.is_active,
                'created_at': search.created_at.isoformat(),
                'product_count': product_count
            }
            search_list.append(search_data)
        
        return jsonify({
            'success': True,
            'searches': search_list
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/searches/<int:search_id>/products', methods=['GET'])
def get_search_products(search_id):
    """
    Obtém produtos de uma busca específica
    """
    try:
        search_config = SearchConfig.query.get_or_404(search_id)
        saved_products = SavedProduct.query.filter_by(search_config_id=search_id).all()
        
        products = []
        for saved_product in saved_products:
            product_data = json.loads(saved_product.product_data)
            product_data['saved_at'] = saved_product.created_at.isoformat()
            product_data['saved_id'] = saved_product.id
            products.append(product_data)
        
        return jsonify({
            'success': True,
            'search_name': search_config.name,
            'products': products
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/searches/<int:search_id>/toggle', methods=['POST'])
def toggle_search_status(search_id):
    """
    Ativa/desativa uma busca
    """
    try:
        search_config = SearchConfig.query.get_or_404(search_id)
        search_config.is_active = not search_config.is_active
        db.session.commit()
        
        status = "ativada" if search_config.is_active else "desativada"
        
        return jsonify({
            'success': True,
            'is_active': search_config.is_active,
            'message': f'Busca "{search_config.name}" {status}.'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/products/<int:product_id>/download-image', methods=['POST'])
def download_product_image(product_id):
    """
    Baixa imagem de um produto
    """
    try:
        saved_product = SavedProduct.query.get_or_404(product_id)
        product_data = json.loads(saved_product.product_data)
        
        # Extrai URL da imagem do produto
        product_url = product_data.get('url')
        if not product_url:
            return jsonify({'error': 'URL do produto não encontrada'}), 400
        
        # Usa o extrator para obter dados completos com imagens
        full_product_data = extractor.extract_product_data(product_url)
        
        if not full_product_data:
            return jsonify({'error': 'Não foi possível extrair dados do produto'}), 400
        
        # Aqui você implementaria a lógica para extrair URLs de imagens
        # Por enquanto, retorna dados do produto
        return jsonify({
            'success': True,
            'product': full_product_data,
            'message': 'Dados do produto extraídos. Implementar download de imagem.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_wizard_bp.route('/products/<int:product_id>/create-post', methods=['POST'])
def create_social_post(product_id):
    """
    Cria post para redes sociais
    """
    try:
        data = request.get_json()
        platform = data.get('platform', 'instagram')  # instagram, facebook, twitter
        template = data.get('template', 'default')
        
        saved_product = SavedProduct.query.get_or_404(product_id)
        product_data = json.loads(saved_product.product_data)
        
        # Gera texto do post baseado no produto
        post_text = generate_post_text(product_data, platform)
        
        # Gera hashtags
        hashtags = generate_hashtags(product_data)
        
        return jsonify({
            'success': True,
            'post_text': post_text,
            'hashtags': hashtags,
            'platform': platform,
            'product': product_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_post_text(product_data, platform):
    """
    Gera texto para post em redes sociais
    """
    nome = product_data.get('nome', 'Produto')
    preco_usd = product_data.get('preco_usd', 0)
    marca = product_data.get('marca', '')
    
    if platform == 'instagram':
        return f"🔥 {nome}\n\n💰 Apenas ${preco_usd}!\n\n✨ {marca} original com garantia\n📦 Pronta entrega\n🚚 Entrega em todo Brasil"
    
    elif platform == 'facebook':
        return f"Oportunidade imperdível! {nome} por apenas ${preco_usd}. Produto original {marca} com garantia. Aproveite esta oferta!"
    
    elif platform == 'twitter':
        return f"🔥 {nome} - ${preco_usd}\n{marca} original 📦\nOferta especial! 🛒"
    
    return f"{nome} - ${preco_usd}"

def generate_hashtags(product_data):
    """
    Gera hashtags baseadas no produto
    """
    hashtags = ['#oferta', '#promocao', '#eletronicos', '#desconto']
    
    marca = product_data.get('marca', '').lower()
    if marca:
        hashtags.append(f'#{marca}')
    
    categoria = product_data.get('categoria', '').lower()
    if 'smartphone' in categoria or 'celular' in categoria:
        hashtags.extend(['#smartphone', '#celular', '#android'])
    elif 'tablet' in categoria:
        hashtags.extend(['#tablet', '#ipad'])
    elif 'notebook' in categoria:
        hashtags.extend(['#notebook', '#laptop'])
    
    return hashtags

