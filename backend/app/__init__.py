"""Fábrica de la aplicación Flask."""
import logging
import traceback

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from . import db, rutas_auth, rutas_generales, rutas_internas
from .config import cargar_configuracion


def create_app() -> Flask:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    app = Flask(__name__)
    app.config.update(cargar_configuracion())

    app.register_blueprint(rutas_generales.bp)
    app.register_blueprint(rutas_auth.bp)
    app.register_blueprint(rutas_internas.bp)
    app.teardown_appcontext(db.cerrar)

    @app.after_request
    def cors(respuesta):
        # Permite consumir la API desde el servidor de desarrollo de Vite u otros clientes.
        origen = request.headers.get("Origin")
        if origen:
            respuesta.headers["Access-Control-Allow-Origin"] = origen
            respuesta.headers["Access-Control-Allow-Credentials"] = "true"
            respuesta.headers["Access-Control-Allow-Headers"] = "Content-Type"
            respuesta.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return respuesta

    @app.errorhandler(HTTPException)
    def error_http(error):
        return jsonify(error=error.description or error.name), error.code

    @app.errorhandler(Exception)
    def error_inesperado(error):
        app.logger.exception("Error no controlado")
        return jsonify(error=str(error), tipo=type(error).__name__, traza=traceback.format_exc()), 500

    return app
