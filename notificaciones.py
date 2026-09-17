"""
notificaciones.py — Avisa por correo al laboratorio cuando llega una orden
nueva desde el portal del dentista.

El correo se envía siempre desde la cuenta centralizada de Sincrodent
(notificaciones@sincrodent.com), no desde el correo del laboratorio — así
ningún laboratorio necesita configurar su propio servidor SMTP. Las
credenciales de esa cuenta viven en variables de entorno del servidor
(ver deploy/smtp.env.example), nunca en el .env de cada instancia ni en
la interfaz de Perfil.

Diseñado para fallar en silencio: si el correo no se puede enviar, la
orden del dentista igual debe quedar guardada. Nunca debe interrumpir
el flujo del portal.
"""

import os
import smtplib
from email.mime.text import MIMEText

from config import cargar

REMITENTE_NOMBRE = "Sincrodent"


def notificar_orden_nueva(cliente_nombre, tipo_trabajo, nombre_trabajo, ot_str):
    """Envía el aviso. Retorna (enviado: bool, error: str|None)."""
    cfg = cargar()

    if cfg.get("NOTIF_EMAIL_ACTIVO") != "1":
        return False, None  # notificaciones desactivadas, no es un error

    destino = cfg.get("NOTIF_EMAIL_DESTINO") or cfg.get("EMAIL_LAB")
    if not destino:
        return False, "Falta el correo de destino (Perfil > Notificaciones)."

    host    = os.environ.get("SINCRODENT_SMTP_HOST")
    puerto  = os.environ.get("SINCRODENT_SMTP_PORT", "587")
    usuario = os.environ.get("SINCRODENT_SMTP_USER", "notificaciones@sincrodent.com")
    clave   = os.environ.get("SINCRODENT_SMTP_PASS")

    if not (host and clave):
        return False, "SMTP central no configurado (variables SINCRODENT_SMTP_* del servidor)."

    cuerpo = (
        f"Llegó una nueva orden desde el portal.\n\n"
        f"OT: {ot_str}\n"
        f"Cliente: {cliente_nombre}\n"
        f"Tipo de trabajo: {tipo_trabajo}\n"
        f"Nombre del trabajo: {nombre_trabajo}\n\n"
        f"Revisa el detalle completo en el panel del laboratorio."
    )
    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["From"] = f"{REMITENTE_NOMBRE} <{usuario}>"
    msg["To"] = destino
    msg["Subject"] = f"Nueva orden {ot_str} — {cliente_nombre}"

    try:
        if str(puerto) == "465":
            with smtplib.SMTP_SSL(host, int(puerto), timeout=3) as server:
                server.login(usuario, clave)
                server.sendmail(usuario, [destino], msg.as_string())
        else:
            with smtplib.SMTP(host, int(puerto), timeout=3) as server:
                server.starttls()
                server.login(usuario, clave)
                server.sendmail(usuario, [destino], msg.as_string())
        return True, None
    except Exception as e:
        return False, str(e)
