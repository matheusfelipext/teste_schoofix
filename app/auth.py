from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request


def perfil_requerido(*perfis_permitidos):
    """Decorator para proteger rotas por perfil de usuário."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("perfil") not in perfis_permitidos:
                return jsonify({"erro": "Você não tem permissão para acessar este recurso."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def login_requerido(fn):
    """Decorator para exigir autenticação JWT."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        return fn(*args, **kwargs)
    return wrapper