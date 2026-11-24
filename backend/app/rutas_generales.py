"""Rutas de soporte y ejemplos: salud, configuración, directorio, perfil y API externa."""
from flask import Blueprint, abort, current_app, jsonify, request, session

from . import api_externa
from .db import confirmar, consultar, ejecutar
from .seguridad import login_requerido

bp = Blueprint("general", __name__, url_prefix="/api")


@bp.get("/salud")
def salud():
    consultar("SELECT 1 AS ok", uno=True)
    return jsonify(estado="ok")


@bp.get("/config")
def config_publica():
    caso = current_app.config["CASO"]
    return jsonify(
        caso=caso["clave"],
        nombre=caso["nombre"],
        roles=caso["roles"],
        api_externa=current_app.config["EXTERNAL_API_BASE_URL"],
    )


# ----------------------------------------------------------------- Directorio
@bp.get("/directorio")
def directorio():
    """Busca cuentas activas por nombre. Ejemplo para el directorio o catálogo del caso."""
    termino = request.args.get("q", "")
    resultados = consultar(
        "SELECT id, nombre, rol FROM cuentas "
        f"WHERE estado = 'activo' AND nombre LIKE '%{termino}%' ORDER BY nombre"
    )
    return jsonify(resultados=resultados)


# --------------------------------------------------------------------- Perfil
@bp.get("/cuentas/<int:id_cuenta>")
@login_requerido
def ver_cuenta(id_cuenta):
    cuenta = consultar("SELECT * FROM cuentas WHERE id = %s", (id_cuenta,), uno=True)
    if not cuenta:
        abort(404)
    return jsonify(cuenta=cuenta)


@bp.put("/cuentas/<int:id_cuenta>")
@login_requerido
def actualizar_cuenta(id_cuenta):
    datos = request.get_json(silent=True) or {}
    if not datos:
        abort(400, description="No hay datos para actualizar.")
    asignaciones = ", ".join(f"{campo} = %s" for campo in datos)
    ejecutar(f"UPDATE cuentas SET {asignaciones} WHERE id = %s", (*datos.values(), id_cuenta))
    confirmar()
    if id_cuenta == session.get("id_cuenta") and "nombre" in datos:
        session["nombre"] = datos["nombre"]
    return jsonify(cuenta=consultar("SELECT * FROM cuentas WHERE id = %s", (id_cuenta,), uno=True))


# ---------------------------------------------------------------- API externa
@bp.get("/ejemplo/api-externa")
@login_requerido
def ejemplo_api_externa():
    """Consulta la API externa del caso. Opcionalmente recibe la URL a consultar."""
    caso = current_app.config["CASO"]["clave"]
    direccion = request.args.get("url")
    try:
        if direccion:
            respuesta = api_externa.get(direccion)
            return jsonify(estado=respuesta.status_code, contenido=respuesta.text)
        if caso == "healthsync":
            respuesta = api_externa.get(
                api_externa.url("dataPoints"),
                params={"schema": "heart-rate", "usuario": session["id_cuenta"], "dias": 1},
            )
            return jsonify(fuente="Open mHealth (simulada)", muestras=respuesta.json()[:5])
        respuesta = api_externa.post(
            api_externa.url("chat/completions"),
            {"model": "simulado/eco-1", "messages": [{"role": "user", "content": "Hola desde la plantilla"}]},
        )
        return jsonify(fuente="OpenRouter (simulada)", respuesta=respuesta.json()["choices"][0]["message"]["content"])
    except api_externa.ErrorApiExterna as error:
        return jsonify(error=f"La API externa no respondió: {error}"), 502
