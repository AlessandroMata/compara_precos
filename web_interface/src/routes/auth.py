"""
Rotas de autenticação
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime, timedelta
from src.models.auth import db, User, Session
import secrets

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Faz login do usuário
    """
    try:
        data = request.get_json()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        # Busca usuário
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuário inativo'}), 401
        
        # Cria sessão
        session_token = Session.generate_token()
        expires_at = datetime.utcnow() + timedelta(days=7)  # 7 dias
        
        user_session = Session(
            user_id=user.id,
            session_token=session_token,
            expires_at=expires_at,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')
        )
        
        db.session.add(user_session)
        
        # Atualiza último login
        user.update_last_login()
        
        db.session.commit()
        
        # Define sessão no Flask
        session['user_id'] = user.id
        session['session_token'] = session_token
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'session_token': session_token
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Faz logout do usuário
    """
    try:
        session_token = session.get('session_token')
        
        if session_token:
            # Invalida sessão no banco
            user_session = Session.query.filter_by(session_token=session_token).first()
            if user_session:
                user_session.invalidate()
        
        # Limpa sessão do Flask
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Verifica se usuário está autenticado
    """
    try:
        user_id = session.get('user_id')
        session_token = session.get('session_token')
        
        if not user_id or not session_token:
            return jsonify({'authenticated': False}), 401
        
        # Verifica sessão no banco
        user_session = Session.query.filter_by(
            session_token=session_token,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not user_session or user_session.is_expired():
            session.clear()
            return jsonify({'authenticated': False}), 401
        
        # Busca dados do usuário
        user = User.query.get(user_id)
        if not user or not user.is_active:
            session.clear()
            return jsonify({'authenticated': False}), 401
        
        return jsonify({
            'authenticated': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'last_login': user.last_login.isoformat() if user.last_login else None
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    Altera senha do usuário
    """
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Não autenticado'}), 401
        
        data = request.get_json()
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Senhas são obrigatórias'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        # Busca usuário
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Verifica senha atual
        if not user.check_password(current_password):
            return jsonify({'error': 'Senha atual incorreta'}), 400
        
        # Atualiza senha
        user.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Senha alterada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def require_auth(f):
    """
    Decorator para rotas que requerem autenticação
    """
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        session_token = session.get('session_token')
        
        if not user_id or not session_token:
            return jsonify({'error': 'Autenticação necessária'}), 401
        
        # Verifica sessão
        user_session = Session.query.filter_by(
            session_token=session_token,
            user_id=user_id,
            is_active=True
        ).first()
        
        if not user_session or user_session.is_expired():
            session.clear()
            return jsonify({'error': 'Sessão expirada'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

