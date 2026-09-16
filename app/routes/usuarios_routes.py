from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models import Usuario, PERFIS
from app.auth import perfil_requerido

bp = Blueprint("usuarios", __name__, url_prefix="/api/usuarios")


@bp.get("")
@perfil_requerido("diretor")
def listar_usuarios():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return jsonify([u.to_dict() for u in usuarios])


@bp.post("")
@perfil_requerido("diretor")
def criar_usuario():
    dados = request.get_json() or {}
    if dados.get("perfil") not in PERFIS:
        return jsonify({"erro": f"perfil inválido. Use um de: {PERFIS}"}), 400
    if Usuario.query.filter_by(email=dados.get("email")).first():
        return jsonify({"erro": "Já existe um usuário com esse e-mail."}), 409

    usuario = Usuario(
        nome=dados.get("nome"),
        email=dados.get("email"),
        senha_hash=generate_password_hash(dados.get("senha", "mudar123")),
        perfil=dados.get("perfil"),
        area_id=dados.get("area_id") if dados.get("perfil") == "gestor" else None,
    )
    db.session.add(usuario)
    db.session.commit()
    return jsonify(usuario.to_dict()), 201


@bp.put("/<usuario_id>")
@perfil_requerido("diretor")
def atualizar_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    dados = request.get_json() or {}

    for campo in ("nome", "email", "ativo", "area_id"):
        if campo in dados:
            setattr(usuario, campo, dados[campo])

    db.session.commit()
    return jsonify(usuario.to_dict())


@bp.delete("/<usuario_id>")
@perfil_requerido("diretor")
def remover_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    db.session.delete(usuario)
    db.session.commit()
    return "", 204
