from flask import Blueprint, request, jsonify
from app.extensions import db

config_bp = Blueprint('configuracoes', __name__, url_prefix='/api/configuracoes')

@config_bp.route('/perfil', methods=['GET', 'PUT'])
def gerenciar_perfil():
    if request.method == 'GET':
        # Retorna configurações do usuário logado
        return jsonify({
            "nome": "Usuário Teste",
            "email": "usuario@escola.com",
            "notificacoes_email": True,
            "tema": "escuro"
        }), 200

    data = request.get_json()
    # Lógica de atualização no banco de dados
    return jsonify({"message": "Configurações atualizadas com sucesso!"}), 200

@config_bp.route('/alterar-senha', methods=['POST'])
def alterar_senha():
    data = request.get_json()
    senha_atual = data.get('senha_atual')
    nova_senha = data.get('nova_senha')
    
    if not senha_atual or not nova_senha:
        return jsonify({"error": "Preencha todos os campos"}), 400
        
    return jsonify({"message": "Senha alterada com sucesso!"}), 200