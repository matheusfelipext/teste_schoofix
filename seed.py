"""
Script de seed para popular o banco de dados SchoolFix.
Compatível com a estrutura de UUIDs e perfis do models.py.

Executar com: python seed.py
"""
import uuid
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import Usuario, Area, Canal, Chamado, Conversa, MensagemDireta

app = create_app()

with app.app_context():
    # 1. Apaga e recria todas as tabelas para garantir a estrutura correta do models.py
    print("Recriando a estrutura do banco de dados...")
    db.drop_all()
    db.create_all()

    # 2. Instancia Usuários com UUIDs explicitados
    diretor = Usuario(
        id=str(uuid.uuid4()),
        nome="Matheus Felipe",
        email="diretor@schoolfix.com",
        senha_hash=generate_password_hash("123456"),
        perfil="diretor",
        ativo=True,
    )

    coordenador = Usuario(
        id=str(uuid.uuid4()),
        nome="Marcos Souza",
        email="coordenador@schoolfix.com",
        senha_hash=generate_password_hash("123456"),
        perfil="coordenador",
        ativo=True,
    )

    gestor = Usuario(
        id=str(uuid.uuid4()),
        nome="Carlos Lima",
        email="gestor.infra@schoolfix.com",
        senha_hash=generate_password_hash("123456"),
        perfil="gestor",
        ativo=True,
    )

    professor = Usuario(
        id=str(uuid.uuid4()),
        nome="Alberto Silva",
        email="professor@schoolfix.com",
        senha_hash=generate_password_hash("123456"),
        perfil="professor",
        ativo=True,
    )

    aluno = Usuario(
        id=str(uuid.uuid4()),
        nome="Lucas Andrade",
        email="aluno@schoolfix.com",
        senha_hash=generate_password_hash("123456"),
        perfil="aluno",
        ativo=True,
    )

    db.session.add_all([diretor, coordenador, gestor, professor, aluno])

    # 3. Instancia Áreas
    area_infra = Area(id=str(uuid.uuid4()), nome="Infraestrutura", gestor_id=gestor.id)
    area_eletrica = Area(id=str(uuid.uuid4()), nome="Eletrica")
    area_limpeza = Area(id=str(uuid.uuid4()), nome="Limpeza")
    area_seguranca = Area(id=str(uuid.uuid4()), nome="Seguranca")
    area_ti = Area(id=str(uuid.uuid4()), nome="TI")

    db.session.add_all([area_infra, area_eletrica, area_limpeza, area_seguranca, area_ti])

    # Vincula o gestor à sua área
    gestor.area_id = area_infra.id

    # 4. Instancia Canais de Chat
    canal_geral = Canal(
        id=str(uuid.uuid4()),
        nome="geral",
        descricao="Canal aberto para todos",
        privado=False,
    )
    canal_professores = Canal(
        id=str(uuid.uuid4()),
        nome="professores",
        descricao="Canal de docentes",
        privado=False,
    )
    canal_gestao = Canal(
        id=str(uuid.uuid4()),
        nome="gestao",
        descricao="Canal exclusivo da administração",
        privado=True,
        perfis_permitidos="diretor,coordenador,gestor",
    )

    db.session.add_all([canal_geral, canal_professores, canal_gestao])

    # 5. Instancia Chamado Exemplo
    chamado_exemplo = Chamado(
        id=str(uuid.uuid4()),
        titulo="Infiltração no teto do Laboratório de Química",
        descricao="Durante as chuvas de ontem, formou-se uma goteira considerável logo acima da bancada principal.",
        categoria="Infraestrutura",
        area_id=area_infra.id,
        status="pendente",
        prioridade="urgente",
        autor_id=professor.id,
        anonimo=False,
    )
    db.session.add(chamado_exemplo)

    # 6. Instancia Conversa e Mensagem Direta
    conversa_exemplo = Conversa(
        id=str(uuid.uuid4()),
        participante1_id=diretor.id,
        participante2_id=gestor.id,
        ultima_mensagem="diretor, o técnico já terminou a vistoria do teto do laboratório de química.",
    )
    db.session.add(conversa_exemplo)

    msg_exemplo = MensagemDireta(
        id=str(uuid.uuid4()),
        conversa_id=conversa_exemplo.id,
        autor_id=gestor.id,
        texto="diretor, o técnico já terminou a vistoria do teto do laboratório de química.",
    )
    db.session.add(msg_exemplo)

    # Persiste todas as alterações
    db.session.commit()

    print("\n==================================================")
    print("  SEED EXECUTADO COM SUCESSO!")
    print("==================================================")
    print("Contas para teste (Senha: 123456):")
    print(" - Diretor:    diretor@schoolfix.com")
    print(" - Coordenador: coordenador@schoolfix.com")
    print(" - Gestor:      gestor.infra@schoolfix.com")
    print(" - Professor:   professor@schoolfix.com")
    print(" - Aluno:       aluno@schoolfix.com")
    print("==================================================\n")