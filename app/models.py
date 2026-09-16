import uuid
from datetime import datetime
from app.extensions import db

# Listas de valores válidos (documentação viva — use nas validações das rotas)
PERFIS = ["aluno", "professor", "gestor", "coordenador", "diretor"]
STATUS_CHAMADO = ["pendente", "em_analise", "resolvido"]
PRIORIDADES = ["baixa", "media", "alta", "urgente"]
TIPOS_NOTIFICACAO = ["novo_chamado", "status_atualizado", "nova_mensagem"]


def gerar_uuid():
    return str(uuid.uuid4())


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)  # ver PERFIS
    area_id = db.Column(db.String(36), db.ForeignKey("areas.id"), nullable=True)  # só p/ gestor
    ativo = db.Column(db.Boolean, default=True)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    area = db.relationship("Area", foreign_keys=[area_id])

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "perfil": self.perfil,
            "area_id": self.area_id,
            "area_nome": self.area.nome if self.area else None,
            "ativo": self.ativo,
            "criado_em": self.criado_em.isoformat(),
        }


class Area(db.Model):
    __tablename__ = "areas"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    nome = db.Column(db.String(60), unique=True, nullable=False)  # Infraestrutura, Eletrica, Limpeza, Seguranca, TI
    gestor_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=True)

    gestor = db.relationship("Usuario", foreign_keys=[gestor_id])

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "gestor_id": self.gestor_id,
            "gestor_nome": self.gestor.nome if self.gestor else None,
        }


class Chamado(db.Model):
    __tablename__ = "chamados"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    categoria = db.Column(db.String(60), nullable=False)
    area_id = db.Column(db.String(36), db.ForeignKey("areas.id"), nullable=False)
    status = db.Column(db.String(20), default="pendente")  # ver STATUS_CHAMADO
    prioridade = db.Column(db.String(20), default="media")  # ver PRIORIDADES
    anonimo = db.Column(db.Boolean, default=False)
    autor_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    canal_prioridade_pedagogica = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    area = db.relationship("Area", foreign_keys=[area_id])
    autor = db.relationship("Usuario", foreign_keys=[autor_id])
    respostas = db.relationship("Resposta", backref="chamado", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "categoria": self.categoria,
            "area": self.area.nome if self.area else None,
            "status": self.status,
            "prioridade": self.prioridade,
            "anonimo": self.anonimo,
            "autor_nome": None if self.anonimo else self.autor.nome,
            "autor_perfil": self.autor.perfil,
            "canal_prioridade_pedagogica": self.canal_prioridade_pedagogica,
            "criado_em": self.criado_em.isoformat(),
            "atualizado_em": self.atualizado_em.isoformat(),
        }


class Resposta(db.Model):
    __tablename__ = "respostas"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    chamado_id = db.Column(db.String(36), db.ForeignKey("chamados.id"), nullable=False)
    autor_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    autor = db.relationship("Usuario", foreign_keys=[autor_id])

    def to_dict(self):
        return {
            "id": self.id,
            "chamado_id": self.chamado_id,
            "autor_nome": self.autor.nome,
            "texto": self.texto,
            "criado_em": self.criado_em.isoformat(),
        }


class Canal(db.Model):
    __tablename__ = "canais"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    nome = db.Column(db.String(60), nullable=False)
    descricao = db.Column(db.String(255))
    privado = db.Column(db.Boolean, default=False)
    perfis_permitidos = db.Column(db.String(255), default="")  # ex: "diretor,coordenador,gestor"

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "privado": self.privado,
            "perfis_permitidos": self.perfis_permitidos.split(",") if self.perfis_permitidos else [],
        }


class MensagemCanal(db.Model):
    __tablename__ = "mensagens_canal"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    canal_id = db.Column(db.String(36), db.ForeignKey("canais.id"), nullable=False)
    autor_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    autor = db.relationship("Usuario", foreign_keys=[autor_id])

    def to_dict(self):
        return {
            "id": self.id,
            "canal_id": self.canal_id,
            "autor_nome": self.autor.nome,
            "autor_perfil": self.autor.perfil,
            "texto": self.texto,
            "criado_em": self.criado_em.isoformat(),
        }


class Conversa(db.Model):
    __tablename__ = "conversas"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    participante1_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    participante2_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    ultima_mensagem = db.Column(db.String(255))
    ultima_mensagem_em = db.Column(db.DateTime)

    participante1 = db.relationship("Usuario", foreign_keys=[participante1_id])
    participante2 = db.relationship("Usuario", foreign_keys=[participante2_id])

    def to_dict(self, uid_atual=None):
        outro = self.participante2 if uid_atual == self.participante1_id else self.participante1
        return {
            "id": self.id,
            "participantes": [self.participante1_id, self.participante2_id],
            "outro_nome": outro.nome if outro else None,
            "outro_perfil": outro.perfil if outro else None,
            "ultima_mensagem": self.ultima_mensagem,
            "ultima_mensagem_em": self.ultima_mensagem_em.isoformat() if self.ultima_mensagem_em else None,
        }


class MensagemDireta(db.Model):
    __tablename__ = "mensagens_diretas"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    conversa_id = db.Column(db.String(36), db.ForeignKey("conversas.id"), nullable=False)
    autor_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversa_id": self.conversa_id,
            "autor_id": self.autor_id,
            "texto": self.texto,
            "lida": self.lida,
            "criado_em": self.criado_em.isoformat(),
        }


class Notificacao(db.Model):
    __tablename__ = "notificacoes"

    id = db.Column(db.String(36), primary_key=True, default=gerar_uuid)
    usuario_id = db.Column(db.String(36), db.ForeignKey("usuarios.id"), nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # ver TIPOS_NOTIFICACAO
    chamado_id = db.Column(db.String(36), db.ForeignKey("chamados.id"), nullable=True)
    titulo = db.Column(db.String(255), nullable=False)
    lida = db.Column(db.Boolean, default=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "usuario_id": self.usuario_id,
            "tipo": self.tipo,
            "chamado_id": self.chamado_id,
            "titulo": self.titulo,
            "lida": self.lida,
            "criado_em": self.criado_em.isoformat(),
        }
