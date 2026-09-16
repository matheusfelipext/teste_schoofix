from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Area
from app.auth import login_requerido, perfil_requerido

bp = Blueprint("areas", __name__, url_prefix="/api/areas")


@bp.get("")
@login_requerido
def listar_areas():
    return jsonify([a.to_dict() for a in Area.query.all()])


@bp.post("")
@perfil_requerido("diretor")
def criar_area():
    dados = request.get_json() or {}
    area = Area(nome=dados.get("nome"), gestor_id=dados.get("gestor_id"))
    db.session.add(area)
    db.session.commit()
    return jsonify(area.to_dict()), 201
