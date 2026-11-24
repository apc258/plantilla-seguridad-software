"""Acceso a la base de datos.

    consultar("SELECT * FROM cuentas WHERE id = %s", (id_cuenta,), uno=True)
    ejecutar("UPDATE cuentas SET nombre = %s WHERE id = %s", (nombre, id_cuenta))
    confirmar()
"""
import mysql.connector
from flask import current_app, g


def conexion():
    if "db" not in g:
        g.db = mysql.connector.connect(**current_app.config["DB"], autocommit=False)
    return g.db


def cerrar(_excepcion=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def consultar(sql: str, parametros: tuple = (), uno: bool = False):
    cursor = conexion().cursor(dictionary=True)
    try:
        cursor.execute(sql, parametros)
        return cursor.fetchone() if uno else cursor.fetchall()
    finally:
        cursor.close()


def ejecutar(sql: str, parametros: tuple = ()) -> int:
    """Ejecuta INSERT/UPDATE/DELETE. Devuelve el id insertado (si aplica)."""
    cursor = conexion().cursor()
    try:
        cursor.execute(sql, parametros)
        return cursor.lastrowid
    finally:
        cursor.close()


def confirmar():
    conexion().commit()
