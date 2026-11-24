"""Carga de configuración desde variables de entorno."""
import json
import os
from datetime import timedelta
from pathlib import Path

RAIZ_CASOS = Path(__file__).resolve().parents[2] / "casos"


def cargar_caso() -> dict:
    """Lee casos/<caso>/caso.json: roles, cuentas de prueba y API externa."""
    caso = os.environ.get("CASO", "healthsync").lower()
    with open(RAIZ_CASOS / caso / "caso.json", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    datos["clave"] = caso
    return datos


def parametros_db() -> dict:
    return {
        "host": os.environ.get("DB_HOST", "db"),
        "port": int(os.environ.get("DB_PORT", "3306")),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("MYSQL_ROOT_PASSWORD", "root"),
        "database": os.environ.get("MYSQL_DATABASE", "app"),
        "connection_timeout": 5,
    }


def cargar_configuracion() -> dict:
    caso = cargar_caso()
    url_externa = os.environ.get("EXTERNAL_API_BASE_URL", "").strip() or caso["api_externa"]["url_simulador"]
    return {
        "SECRET_KEY": os.environ.get("SECRET_KEY", "plantilla-secreta"),
        "SESSION_COOKIE_NAME": "sesion",
        # El frontend revisa la cookie para saber si hay una sesión abierta.
        "SESSION_COOKIE_HTTPONLY": False,
        "PERMANENT_SESSION_LIFETIME": timedelta(days=30),
        "CASO": caso,
        "DB": parametros_db(),
        "WORKER_TOKEN": os.environ.get("WORKER_TOKEN", "worker-token"),
        "SMTP_HOST": os.environ.get("SMTP_HOST", "mailpit"),
        "SMTP_PORT": int(os.environ.get("SMTP_PORT", "1025")),
        "MAIL_FROM": os.environ.get("MAIL_FROM", f"no-responder@{caso['clave']}.test"),
        "EXTERNAL_API_BASE_URL": url_externa.rstrip("/"),
        "EXTERNAL_API_KEY": os.environ.get("EXTERNAL_API_KEY", ""),
    }
