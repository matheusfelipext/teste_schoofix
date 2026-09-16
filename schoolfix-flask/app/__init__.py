from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configuração correta do CORS para liberar todas as rotas e credenciais:
    cors.init_app(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    from app.routes import auth_routes, chamados_routes, usuarios_routes, areas_routes, chat_routes, notificacoes_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(chamados_routes.bp)
    app.register_blueprint(usuarios_routes.bp)
    app.register_blueprint(areas_routes.bp)
    app.register_blueprint(chat_routes.bp)
    app.register_blueprint(notificacoes_routes.bp)

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado."}), 404

    return app