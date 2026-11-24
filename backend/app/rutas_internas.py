"""Endpoints internos para el robot C++ (servicio "worker").

Cada petición debe traer el encabezado X-Internal-Token con el valor de WORKER_TOKEN.
Agregue aquí los endpoints que necesiten sus robots.
"""
from flask import Blueprint, Response, abort, current_app, request

from .db import consultar

bp = Blueprint("interno", __name__, url_prefix="/api/internal")


@bp.before_request
def verificar_token():
    if request.headers.get("X-Internal-Token") != current_app.config["WORKER_TOKEN"]:
        abort(401)


@bp.get("/pendientes")
def pendientes():
    """Cuentas pendientes de aprobación, una por línea: id|nombre|email."""
    cuentas = consultar("SELECT id, nombre, email FROM cuentas WHERE estado = 'pendiente' ORDER BY id")
    lineas = [f"{c['id']}|{c['nombre']}|{c['email']}" for c in cuentas]
    return Response("\n".join(lineas) + ("\n" if lineas else ""), mimetype="text/plain")
