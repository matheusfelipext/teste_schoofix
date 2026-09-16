from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt
from app.extensions import db
from app.models import Usuario, PERFIS
from app.auth import login_requerido

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    dados = request.get_json() or {}
    nome = dados.get("nome")
    email = dados.get("email")
    senha = dados.get("senha")
    perfil = dados.get("perfil")
    area_id = dados.get("area_id")  # obrigatório só se perfil == "gestor"

    if not all([nome, email, senha, perfil]):
        return jsonify({"erro": "nome, email, senha e perfil são obrigatórios."}), 400

    if perfil not in PERFIS:
        return jsonify({"erro": f"perfil inválido. Use um de: {PERFIS}"}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"erro": "Já existe um usuário com esse e-mail."}), 409

    usuario = Usuario(
        nome=nome,
        email=email,
        senha_hash=generate_password_hash(senha),
        perfil=perfil,
        area_id=area_id if perfil == "gestor" else None,
    )
    db.session.add(usuario)
    db.session.commit()

    return jsonify(usuario.to_dict()), 201


@bp.post("/login")
def login():
    dados = request.get_json() or {}
    email = dados.get("email")
    senha = dados.get("senha")

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha_hash, senha or ""):
        return jsonify({"erro": "E-mail ou senha inválidos."}), 401

    if not usuario.ativo:
        return jsonify({"erro": "Este usuário está inativo."}), 403

    # claims extras ficam disponíveis em get_jwt() nas rotas protegidas
    token = create_access_token(
        identity=usuario.id,
        additional_claims={"perfil": usuario.perfil, "area_id": usuario.area_id, "nome": usuario.nome},
    )

    return jsonify({"access_token": token, "usuario": usuario.to_dict()})


@bp.get("/me")
@login_requerido
def me():
    usuario = Usuario.query.get(get_jwt_identity())
    if not usuario:
        return jsonify({"erro": "Usuário não encontrado."}), 404
    return jsonify(usuario.to_dict())
