"""
Modelos de banco de dados para configurações de busca e produtos salvos
"""
from ..database import db
from datetime import datetime

class SearchConfig(db.Model):
    """
    Configuração de busca salva e aprovada
    """
    __tablename__ = 'search_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    query = db.Column(db.String(500), nullable=False)
    min_price_usd = db.Column(db.Float, nullable=True)
    max_price_usd = db.Column(db.Float, nullable=True)
    categories = db.Column(db.Text, nullable=True)  # JSON string
    brands = db.Column(db.Text, nullable=True)      # JSON string
    in_stock_only = db.Column(db.Boolean, default=True)
    sort_by = db.Column(db.String(50), default='price_asc')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com produtos salvos
    saved_products = db.relationship('SavedProduct', backref='search_config', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SearchConfig {self.name}>'

class SavedProduct(db.Model):
    """
    Produto salvo de uma busca específica
    """
    __tablename__ = 'saved_products'
    
    id = db.Column(db.Integer, primary_key=True)
    search_config_id = db.Column(db.Integer, db.ForeignKey('search_configs.id'), nullable=False)
    product_data = db.Column(db.Text, nullable=False)  # JSON string com dados do produto
    image_urls = db.Column(db.Text, nullable=True)     # JSON string com URLs das imagens
    downloaded_images = db.Column(db.Text, nullable=True)  # JSON string com paths das imagens baixadas
    social_posts = db.Column(db.Text, nullable=True)   # JSON string com posts gerados
    is_favorite = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SavedProduct {self.id}>'

class MonitoringLog(db.Model):
    """
    Log de execução de monitoramento de buscas
    """
    __tablename__ = 'monitoring_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    search_config_id = db.Column(db.Integer, db.ForeignKey('search_configs.id'), nullable=False)
    execution_time = db.Column(db.DateTime, default=datetime.utcnow)
    products_found = db.Column(db.Integer, default=0)
    new_products = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='success')  # success, error, warning
    message = db.Column(db.Text, nullable=True)
    execution_duration = db.Column(db.Float, nullable=True)  # em segundos
    
    def __repr__(self):
        return f'<MonitoringLog {self.id}>'

class ImageDownload(db.Model):
    """
    Registro de downloads de imagens
    """
    __tablename__ = 'image_downloads'
    
    id = db.Column(db.Integer, primary_key=True)
    saved_product_id = db.Column(db.Integer, db.ForeignKey('saved_products.id'), nullable=False)
    original_url = db.Column(db.String(1000), nullable=False)
    local_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    image_width = db.Column(db.Integer, nullable=True)
    image_height = db.Column(db.Integer, nullable=True)
    download_status = db.Column(db.String(50), default='pending')  # pending, success, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ImageDownload {self.id}>'

class SocialPost(db.Model):
    """
    Posts gerados para redes sociais
    """
    __tablename__ = 'social_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    saved_product_id = db.Column(db.Integer, db.ForeignKey('saved_products.id'), nullable=False)
    platform = db.Column(db.String(50), nullable=False)  # instagram, facebook, twitter, etc
    template = db.Column(db.String(100), nullable=False)
    post_text = db.Column(db.Text, nullable=False)
    hashtags = db.Column(db.Text, nullable=True)  # JSON string
    image_path = db.Column(db.String(500), nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialPost {self.platform} - {self.id}>'

