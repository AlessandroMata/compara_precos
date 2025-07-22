"""
Sistema de autenticação simples para acesso interno
"""
from ..database import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import secrets

class User(db.Model):
    """
    Usuário do sistema (apenas um usuário admin)
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Define senha com hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica senha"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Atualiza último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'

class Session(db.Model):
    """
    Sessões de usuário
    """
    __tablename__ = 'sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    
    user = db.relationship('User', backref='sessions')
    
    @staticmethod
    def generate_token():
        """Gera token de sessão"""
        return secrets.token_urlsafe(32)
    
    def is_expired(self):
        """Verifica se sessão expirou"""
        return datetime.utcnow() > self.expires_at
    
    def invalidate(self):
        """Invalida sessão"""
        self.is_active = False
        db.session.commit()
    
    def __repr__(self):
        return f'<Session {self.session_token[:8]}...>'

def create_default_user():
    """
    Cria usuário padrão se não existir
    """
    try:
        # Verifica se já existe usuário
        existing_user = User.query.first()
        if existing_user:
            return existing_user
        
        # Cria usuário padrão
        default_user = User(
            username='admin',
            email='admin@paraguai-extractor.com'
        )
        default_user.set_password('admin123')  # Senha padrão - MUDE EM PRODUÇÃO
        
        db.session.add(default_user)
        db.session.commit()
        
        print("✅ Usuário padrão criado:")
        print("   Username: admin")
        print("   Password: admin123")
        print("   ⚠️  ALTERE A SENHA EM PRODUÇÃO!")
        
        return default_user
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário padrão: {str(e)}")
        db.session.rollback()
        return None

