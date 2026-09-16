from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity
from app.extensions import db
from app.models import Chamado, Resposta, Area, Usuario, Notificacao, STATUS_CHAMADO, PRIORIDADES
from app.auth import login_requerido

bp = Blueprint("chamados", __name__, url_prefix="/api/chamados")


def notificar(usuario_id, tipo, titulo, chamado_id=None):
    db.session.add(Notificacao(usuario_id=usuario_id, tipo=tipo, titulo=titulo, chamado_id=chamado_id))


def rotear_chamado(chamado):
    """
    Equivalente à Cloud Function onChamadoCriado do desenho anterior (Firebase):
    acha o gestor da área e cria a notificação. Se for urgente, notifica a diretoria também.
    """
    area = Area.query.get(chamado.area_id)
    if area and area.gestor_id:
        notificar(
            area.gestor_id,
            "novo_chamado",
            f"Novo chamado ({chamado.prioridade}) em {area.nome}: {chamado.titulo}",
            chamado.id,
        )

    if chamado.prioridade == "urgente":
        diretores = Usuario.query.filter_by(perfil="diretor").all()
        for d in diretores:
            notificar(d.id, "novo_chamado", f"URGENTE em {area.nome if area else '?'}: {chamado.titulo}", chamado.id)

    db.session.commit()


@bp.post("")
@login_requerido
def criar_chamado():
    dados = request.get_json() or {}
    claims = get_jwt()
    autor_id = get_jwt_identity()

    area = Area.query.filter_by(nome=dados.get("area")).first()
    if not area:
        return jsonify({"erro": f"Área '{dados.get('area')}' não encontrada."}), 400

    if dados.get("prioridade") and dados["prioridade"] not in PRIORIDADES:
        return jsonify({"erro": f"prioridade inválida. Use um de: {PRIORIDADES}"}), 400

    chamado = Chamado(
        titulo=dados.get("titulo"),
        descricao=dados.get("descricao"),
        categoria=dados.get("categoria"),
        area_id=area.id,
        prioridade=dados.get("prioridade", "media"),
        anonimo=bool(dados.get("anonimo", False)),
        autor_id=autor_id,
        canal_prioridade_pedagogica=bool(dados.get("canal_prioridade_pedagogica", False)) and claims.get("perfil") == "professor",
    )
    db.session.add(chamado)
    db.session.commit()

    rotear_chamado(chamado)  # cria as notificações — "roteamento automático" do relatório

    return jsonify(chamado.to_dict()), 201


@bp.get("")
@login_requerido
def listar_chamados():
    claims = get_jwt()
    perfil = claims.get("perfil")
    uid = get_jwt_identity()

    query = Chamado.query

    if perfil == "gestor":
        query = query.filter_by(area_id=claims.get("area_id"))
    elif perfil in ("aluno", "professor"):
        query = query.filter_by(autor_id=uid)
    # coordenador e diretor veem tudo — sem filtro

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    chamados = query.order_by(Chamado.criado_em.desc()).all()
    return jsonify([c.to_dict() for c in chamados])


@bp.get("/<chamado_id>")
@login_requerido
def obter_chamado(chamado_id):
    chamado = Chamado.query.get_or_404(chamado_id)
    dados = chamado.to_dict()
    dados["respostas"] = [r.to_dict() for r in chamado.respostas]
    return jsonify(dados)


@bp.put("/<chamado_id>/status")
@login_requerido
def atualizar_status(chamado_id):
    claims = get_jwt()
    chamado = Chamado.query.get_or_404(chamado_id)

    # só o gestor da própria área ou a diretoria podem mudar status
    if claims.get("perfil") == "gestor" and chamado.area_id != claims.get("area_id"):
        return jsonify({"erro": "Você só pode atualizar chamados da sua área."}), 403
    if claims.get("perfil") not in ("gestor", "diretor"):
        return jsonify({"erro": "Sem permissão para atualizar status."}), 403

    novo_status = (request.get_json() or {}).get("status")
    if novo_status not in STATUS_CHAMADO:
        return jsonify({"erro": f"status inválido. Use um de: {STATUS_CHAMADO}"}), 400

    chamado.status = novo_status
    chamado.atualizado_em = datetime.utcnow()
    db.session.commit()

    notificar(chamado.autor_id, "status_atualizado", f'Seu chamado "{chamado.titulo}" mudou para: {novo_status}', chamado.id)
    db.session.commit()

    return jsonify(chamado.to_dict())


@bp.post("/<chamado_id>/respostas")
@login_requerido
def responder_chamado(chamado_id):
    chamado = Chamado.query.get_or_404(chamado_id)
    texto = (request.get_json() or {}).get("texto")
    if not texto:
        return jsonify({"erro": "texto é obrigatório."}), 400

    resposta = Resposta(chamado_id=chamado.id, autor_id=get_jwt_identity(), texto=texto)
    db.session.add(resposta)
    db.session.commit()

    return jsonify(resposta.to_dict()), 201
