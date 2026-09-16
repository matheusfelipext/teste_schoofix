"""
Popula o banco com dados mínimos pra testar: as 5 áreas do relatório,
1 diretor, 1 coordenador e 1 gestor de teste.
Rodar com:  flask shell < seed.py   OU   python seed.py  (com o app context)
"""
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models import Usuario, Area, Canal, Chamado, Conversa, MensagemDireta

app = create_app()

with app.app_context():
    db.create_all()

    if Usuario.query.filter_by(email="diretora@schoolfix.com").first():
        print("Seed já foi rodado antes — nada a fazer.")
    else:
        diretora = Usuario(
            nome="Maria Oliveira",
            email="diretora@schoolfix.com",
            senha_hash=generate_password_hash("123456"),
            perfil="diretor",
        )
        coordenador = Usuario(
            nome="Marcos Souza",
            email="coordenador@schoolfix.com",
            senha_hash=generate_password_hash("123456"),
            perfil="coordenador",
        )
        gestor = Usuario(
            nome="Carlos Lima",
            email="gestor.infra@schoolfix.com",
            senha_hash=generate_password_hash("123456"),
            perfil="gestor",
        )
        professor = Usuario(
            nome="Alberto Silva",
            email="professor@schoolfix.com",
            senha_hash=generate_password_hash("123456"),
            perfil="professor",
        )
        db.session.add_all([diretora, coordenador, gestor, professor])
        db.session.flush()  # garante que os IDs já existem antes de usar no gestor_id

        areas = [
            Area(nome="Infraestrutura", gestor_id=gestor.id),
            Area(nome="Eletrica"),
            Area(nome="Limpeza"),
            Area(nome="Seguranca"),
            Area(nome="TI"),
        ]
        db.session.add_all(areas)
        db.session.flush()
        gestor.area_id = areas[0].id  # Carlos Lima gerencia Infraestrutura

        # Canais do Chat Geral — sem isso a tela de Chat fica vazia
        canais = [
            Canal(nome="geral", descricao="Canal aberto para todos", privado=False),
            Canal(nome="professores", descricao="Canal de docentes", privado=False),
            Canal(nome="gestao", descricao="Canal exclusivo da administração", privado=True,
                  perfis_permitidos="diretor,coordenador,gestor"),
        ]
        db.session.add_all(canais)

        # Um chamado de exemplo — sem isso Início/Reclamações/Relatórios ficam vazios
        chamado_exemplo = Chamado(
            titulo="Infiltração no teto do Laboratório de Química",
            descricao="Durante as chuvas de ontem, formou-se uma goteira considerável logo acima da bancada principal.",
            categoria="Infraestrutura",
            area_id=areas[0].id,
            status="pendente",
            prioridade="urgente",
            autor_id=professor.id,
        )
        db.session.add(chamado_exemplo)

        # Uma conversa de exemplo — sem isso Mensagens Diretas fica vazia
        conversa_exemplo = Conversa(participante1_id=diretora.id, participante2_id=gestor.id)
        db.session.add(conversa_exemplo)
        db.session.flush()
        db.session.add(MensagemDireta(
            conversa_id=conversa_exemplo.id,
            autor_id=gestor.id,
            texto="Diretora, o técnico já terminou a vistoria do teto do laboratório de química.",
        ))
        conversa_exemplo.ultima_mensagem = "Diretora, o técnico já terminou a vistoria do teto do laboratório de química."

        db.session.commit()

        print("Seed concluído!")
        print("Login de teste -> diretora@schoolfix.com / 123456")
        print("Login de teste -> coordenador@schoolfix.com / 123456")
        print("Login de teste -> gestor.infra@schoolfix.com / 123456")
        print("Login de teste -> professor@schoolfix.com / 123456")

