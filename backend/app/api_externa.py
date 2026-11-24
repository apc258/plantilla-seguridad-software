"""Cliente HTTP para la API externa del caso (simulada o real)."""
import requests
from flask import current_app


class ErrorApiExterna(RuntimeError):
    pass


def _encabezados() -> dict:
    encabezados = {"Accept": "application/json"}
    llave = current_app.config["EXTERNAL_API_KEY"]
    if llave:
        encabezados["Authorization"] = f"Bearer {llave}"
    return encabezados


def url(ruta: str) -> str:
    return f"{current_app.config['EXTERNAL_API_BASE_URL']}/{ruta.lstrip('/')}"


def get(direccion: str, params: dict | None = None) -> requests.Response:
    try:
        return requests.get(direccion, params=params, headers=_encabezados(), timeout=15)
    except requests.RequestException as error:
        raise ErrorApiExterna(str(error)) from error


def post(direccion: str, cuerpo: dict) -> requests.Response:
    try:
        return requests.post(direccion, json=cuerpo, headers=_encabezados(), timeout=15)
    except requests.RequestException as error:
        raise ErrorApiExterna(str(error)) from error
