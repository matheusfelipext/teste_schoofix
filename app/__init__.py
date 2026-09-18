from flask import Flask, jsonify, request
from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # 1. Ativa o Flask-CORS globalmente
    cors.init_app(app, resources={r"/*": {"origins": "*"}})

    # 2. Força respostas 200 OK em todas as requisições OPTIONS (Preflight)
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = app.make_default_options_response()
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response, 200

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response

    # 3. Registra os Blueprints
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