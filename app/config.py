import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-troque-em-producao")

    # Em dev usa SQLite (arquivo local, zero configuração).
    # Em produção, defina DATABASE_URL apontando pro PostgreSQL do seu provedor.
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'schoolfix.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-troque-em-producao")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
