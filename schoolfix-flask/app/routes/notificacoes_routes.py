from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import Notificacao
from app.auth import login_requerido

bp = Blueprint("notificacoes", __name__, url_prefix="/api/notificacoes")


@bp.get("")
@login_requerido
def listar_notificacoes():
    uid = get_jwt_identity()
    notifs = Notificacao.query.filter_by(usuario_id=uid).order_by(Notificacao.criado_em.desc()).all()
    return jsonify([n.to_dict() for n in notifs])


@bp.put("/<notificacao_id>/lida")
@login_requerido
def marcar_como_lida(notificacao_id):
    notif = Notificacao.query.get_or_404(notificacao_id)
    notif.lida = True
    db.session.commit()
    return jsonify(notif.to_dict())
