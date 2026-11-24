"""Datos semilla. Se ejecuta una vez en cada arranque (servicio "seed").

Crea la cuenta de administrador (ADMIN_EMAIL / ADMIN_PASSWORD) y las cuentas
de prueba de casos/<caso>/caso.json, todas con SEED_PASSWORD. Si una cuenta ya
existe, no la modifica.

Agregue al final de main() los datos semilla de sus propios módulos
(saldos iniciales, agentes del catálogo, métricas de ejemplo...).
"""
import hashlib
import os
import sys
import time

import mysql.connector

from .config import cargar_caso, parametros_db


def conectar(intentos: int = 30):
    for intento in range(1, intentos + 1):
        try:
            return mysql.connector.connect(**parametros_db(), autocommit=False)
        except mysql.connector.Error as error:
            print(f"[seed] Base de datos no disponible (intento {intento}): {error}", flush=True)
            time.sleep(2)
    raise SystemExit("[seed] No fue posible conectarse a la base de datos.")


def crear_cuenta(cursor, nombre: str, email: str, password: str, rol: str) -> bool:
    cursor.execute("SELECT id FROM cuentas WHERE email = %s", (email.lower(),))
    if cursor.fetchone():
        return False
    cursor.execute(
        "INSERT INTO cuentas (nombre, email, password_hash, rol, estado) VALUES (%s, %s, %s, %s, 'activo')",
        (nombre, email.lower(), hashlib.md5(password.encode()).hexdigest(), rol),
    )
    return True


def main() -> int:
    caso = cargar_caso()
    seed_password = os.environ.get("SEED_PASSWORD", "prueba123")

    conn = conectar()
    cursor = conn.cursor()
    try:
        creadas = 0
        creadas += crear_cuenta(
            cursor,
            "Administrador",
            os.environ.get("ADMIN_EMAIL", "admin@plantilla.test"),
            os.environ.get("ADMIN_PASSWORD", "admin123"),
            "admin",
        )
        for cuenta in caso.get("cuentas_prueba", []):
            creadas += crear_cuenta(cursor, cuenta["nombre"], cuenta["email"], seed_password, cuenta["rol"])

        # TODO (cada grupo): datos semilla de sus módulos.

        conn.commit()
        print(f"[seed] Caso '{caso['clave']}': {creadas} cuenta(s) nueva(s).", flush=True)
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
