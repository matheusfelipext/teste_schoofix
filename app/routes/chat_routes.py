from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import Canal, MensagemCanal, Conversa, MensagemDireta, Notificacao
from app.auth import login_requerido

bp = Blueprint("chat", __name__, url_prefix="/api")


# ---------- Canais (Chat Geral) ----------

@bp.get("/canais")
@login_requerido
def listar_canais():
    return jsonify([c.to_dict() for c in Canal.query.all()])


@bp.get("/canais/<canal_id>/mensagens")
@login_requerido
def listar_mensagens_canal(canal_id):
    msgs = MensagemCanal.query.filter_by(canal_id=canal_id).order_by(MensagemCanal.criado_em).all()
    return jsonify([m.to_dict() for m in msgs])


@bp.post("/canais/<canal_id>/mensagens")
@login_requerido
def enviar_mensagem_canal(canal_id):
    texto = (request.get_json() or {}).get("texto")
    if not texto:
        return jsonify({"erro": "texto é obrigatório."}), 400

    msg = MensagemCanal(canal_id=canal_id, autor_id=get_jwt_identity(), texto=texto)
    db.session.add(msg)
    db.session.commit()
    return jsonify(msg.to_dict()), 201


# ---------- Conversas (Mensagens Diretas) ----------

@bp.get("/conversas")
@login_requerido
def listar_conversas():
    uid = get_jwt_identity()
    conversas = Conversa.query.filter(
        (Conversa.participante1_id == uid) | (Conversa.participante2_id == uid)
    ).order_by(Conversa.ultima_mensagem_em.desc()).all()
    return jsonify([c.to_dict(uid_atual=uid) for c in conversas])


@bp.post("/conversas")
@login_requerido
def iniciar_conversa():
    uid = get_jwt_identity()
    destinatario_id = (request.get_json() or {}).get("destinatario_id")

    existente = Conversa.query.filter(
        ((Conversa.participante1_id == uid) & (Conversa.participante2_id == destinatario_id))
        | ((Conversa.participante1_id == destinatario_id) & (Conversa.participante2_id == uid))
    ).first()
    if existente:
        return jsonify(existente.to_dict(uid_atual=uid))

    conversa = Conversa(participante1_id=uid, participante2_id=destinatario_id)
    db.session.add(conversa)
    db.session.commit()
    return jsonify(conversa.to_dict(uid_atual=uid)), 201


@bp.get("/conversas/<conversa_id>/mensagens")
@login_requerido
def listar_mensagens_diretas(conversa_id):
    msgs = MensagemDireta.query.filter_by(conversa_id=conversa_id).order_by(MensagemDireta.criado_em).all()
    return jsonify([m.to_dict() for m in msgs])


@bp.post("/conversas/<conversa_id>/mensagens")
@login_requerido
def enviar_mensagem_direta(conversa_id):
    uid = get_jwt_identity()
    texto = (request.get_json() or {}).get("texto")
    if not texto:
        return jsonify({"erro": "texto é obrigatório."}), 400

    msg = MensagemDireta(conversa_id=conversa_id, autor_id=uid, texto=texto)
    db.session.add(msg)

    conversa = Conversa.query.get(conversa_id)
    conversa.ultima_mensagem = texto
    conversa.ultima_mensagem_em = datetime.utcnow()

    destinatario_id = conversa.participante2_id if conversa.participante1_id == uid else conversa.participante1_id
    db.session.add(Notificacao(
        usuario_id=destinatario_id,
        tipo="nova_mensagem",
        titulo="Você recebeu uma nova mensagem direta",
    ))

    db.session.commit()
    return jsonify(msg.to_dict()), 201
