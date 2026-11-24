"""Utilidades de autenticación y autorización."""
from functools import wraps

from flask import abort, session


def usuario_actual():
    if "id_cuenta" not in session:
        return None
    return {
        "id": session["id_cuenta"],
        "nombre": session.get("nombre"),
        "email": session.get("email"),
        "rol": session.get("rol"),
    }


def login_requerido(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if usuario_actual() is None:
            abort(401)
        return vista(*args, **kwargs)

    return envoltura


def rol_requerido(*roles):
    """Uso: @rol_requerido("admin") debajo de la definición de la ruta."""

    def decorador(vista):
        @wraps(vista)
        def envoltura(*args, **kwargs):
            usuario = usuario_actual()
            if usuario is None:
                abort(401)
            if usuario["rol"] not in roles:
                abort(403)
            return vista(*args, **kwargs)

        return envoltura

    return decorador
