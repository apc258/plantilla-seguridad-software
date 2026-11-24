"""Registro, inicio y cierre de sesión."""
import hashlib

from flask import Blueprint, abort, current_app, jsonify, request, session

from . import correo
from .db import confirmar, consultar, ejecutar
from .seguridad import login_requerido, usuario_actual

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


def _datos() -> dict:
    return request.get_json(silent=True) or request.form.to_dict()


@bp.post("/registro")
def registro():
    datos = _datos()
    nombre = str(datos.get("nombre", "")).strip()
    email = str(datos.get("email", "")).strip().lower()
    password = str(datos.get("password", ""))
    rol = datos.get("rol", "")

    if not nombre or not email or "@" not in email:
        abort(400, description="Nombre y correo son obligatorios.")
    if len(password) < 6:
        abort(400, description="La contraseña debe tener al menos 6 caracteres.")

    if consultar("SELECT id FROM cuentas WHERE email = %s", (email,), uno=True):
        return jsonify(error="El correo ya está registrado."), 409

    roles = current_app.config["CASO"]["roles"]
    estado = "pendiente" if roles.get(rol, {}).get("requiere_aprobacion") else "activo"
    ejecutar(
        "INSERT INTO cuentas (nombre, email, password_hash, rol, estado) VALUES (%s, %s, %s, %s, %s)",
        (nombre, email, hash_password(password), rol, estado),
    )
    confirmar()

    texto = (
        "Su cuenta fue creada y quedó pendiente de aprobación."
        if estado == "pendiente"
        else "Su cuenta fue creada y ya puede iniciar sesión."
    )
    correo.enviar(email, "Registro recibido", f"Hola {nombre}. {texto}")
    return jsonify(mensaje=texto), 201


@bp.post("/ingresar")
def ingresar():
    datos = _datos()
    email = str(datos.get("email", "")).strip().lower()
    password = str(datos.get("password", ""))

    cuenta = consultar(
        f"SELECT * FROM cuentas WHERE email = '{email}' AND password_hash = '{hash_password(password)}'",
        uno=True,
    )
    if not cuenta:
        return jsonify(error="Correo o contraseña incorrectos."), 401
    if cuenta["estado"] != "activo":
        return jsonify(error=f"La cuenta está en estado '{cuenta['estado']}'."), 403

    session.permanent = True
    session["id_cuenta"] = cuenta["id"]
    session["nombre"] = cuenta["nombre"]
    session["email"] = cuenta["email"]
    session["rol"] = cuenta["rol"]
    return jsonify(usuario=cuenta)


@bp.route("/salir", methods=["GET", "POST"])
def salir():
    session.clear()
    return jsonify(mensaje="Sesión cerrada.")


@bp.get("/yo")
@login_requerido
def yo():
    return jsonify(usuario=usuario_actual())
