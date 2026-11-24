"""Envío de correo. En la plantilla todo correo llega a Mailpit (http://localhost:8025)."""
import logging
import smtplib
from email.message import EmailMessage

from flask import current_app

log = logging.getLogger(__name__)


def enviar(destinatario: str, asunto: str, cuerpo: str) -> bool:
    mensaje = EmailMessage()
    mensaje["From"] = current_app.config["MAIL_FROM"]
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    mensaje.set_content(cuerpo)
    try:
        with smtplib.SMTP(current_app.config["SMTP_HOST"], current_app.config["SMTP_PORT"], timeout=5) as smtp:
            smtp.send_message(mensaje)
        return True
    except (OSError, smtplib.SMTPException):
        log.exception("No se pudo enviar el correo '%s'", asunto)
        return False
