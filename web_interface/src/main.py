import os
import sys
import logging
from logging.handlers import RotatingFileHandler
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, session
from flask_cors import CORS
from src.database import db
from datetime import datetime

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuração de Logging
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Log para arquivo
log_file = 'app.log'
file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 5, backupCount=2) # 5 MB por arquivo
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)

# Log para console
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.DEBUG)

# Adiciona handlers ao logger da aplicação
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.DEBUG)

# Adiciona handlers ao logger raiz para capturar logs de outras bibliotecas
logging.getLogger().addHandler(console_handler)
logging.getLogger().addHandler(file_handler)
logging.getLogger().setLevel(logging.DEBUG)

app.logger.info('Aplicação iniciada com logging configurado.')

CORS(app, origins=["http://localhost:3000"])  # Permite CORS apenas do frontend local
app.config['SECRET_KEY'] = 'paraguai-price-extractor-2024-secret-key'

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração de sessão
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

# Inicializa banco de dados
db.init_app(app)

# Importa rotas
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.search_wizard import search_wizard_bp

# Registra blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(search_wizard_bp, url_prefix='/api/search-wizard')

# Health check endpoint para Docker
@app.route('/api/health')
def health_check():
    try:
        # Verifica se o banco está funcionando
        from src.models.auth import User
        User.query.first()
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}, 200
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500

with app.app_context():
    # Importa e cria modelos
    from src.models.auth import User, Session, create_default_user
    from src.models.search_config import SearchConfig, SavedProduct, MonitoringLog, ImageDownload, SocialPost
    
    # Cria todas as tabelas
    db.create_all()
    
    # Cria usuário padrão
    create_default_user()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.errorhandler(404)
def not_found(error):
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    print("🚀 Iniciando Paraguai Price Extractor")
    print("=" * 50)
    print("📊 Sistema de análise de oportunidades")
    print("🔐 Acesso: http://0.0.0.0:5000")
    print("👤 Login padrão: admin / admin123")
    print("⚠️  ALTERE A SENHA EM PRODUÇÃO!")
    print("=" * 50)
    
    # Configuração para aceitar conexões externas
    import os
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'true').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug, threaded=True)
