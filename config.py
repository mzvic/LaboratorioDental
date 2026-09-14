"""
config.py — Lee y escribe la configuración del laboratorio desde .env
Importar con: from config import cfg
"""

import os
import hashlib
import secrets
from dotenv import dotenv_values, set_key

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

# Valores por defecto (si falta alguna clave en el .env)
DEFAULTS = {
    "SETUP_COMPLETO":    "0",     # "0" = falta completar el asistente de configuración inicial
    "NOMBRE_LAB":        "",
    "TELEFONO_LAB":      "",
    "EMAIL_LAB":         "",
    "DIRECCION_LAB":     "",
    "BANCO":             "",
    "TIPO_CUENTA":       "",
    "NUMERO_CUENTA":     "",
    "RUT_LAB":           "",
    "NOMBRE_TITULAR":    "",
    "PORTAL_BASE":       "http://localhost:8502",
    "LOGO_PATH":         "logo.jpeg",
    "LOGO_APP_PATH":     "Sincrodent.png",

    # ── Cumplimiento Ley 20.584 (privacidad de fichas / datos de pacientes) ──
    "TIPO_ENTIDAD":         "privada",   # "privada" | "publica"
    "ADMIN_PASSWORD_HASH":  "",          # hash sha256("salt:password")
    "ADMIN_PASSWORD_SALT":  "",
}


def cargar():
    """Carga el .env y rellena los valores que falten con defaults."""
    valores = dict(DEFAULTS)
    valores.update({k: v for k, v in dotenv_values(ENV_PATH).items() if v is not None})
    return valores


def guardar(clave: str, valor: str):
    """Escribe una clave al archivo .env."""
    set_key(ENV_PATH, clave, valor)


def guardar_todo(datos: dict):
    """Escribe un diccionario completo al .env."""
    for clave, valor in datos.items():
        set_key(ENV_PATH, clave, valor)


def entidad_es_publica():
    """True si el laboratorio se configuró como entidad/institución pública."""
    return cargar()["TIPO_ENTIDAD"] == "publica"


def establecer_password_admin(password: str):
    """Genera y guarda un hash salteado de la contraseña de administrador."""
    salt = secrets.token_hex(16)
    hash_ = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    guardar_todo({"ADMIN_PASSWORD_SALT": salt, "ADMIN_PASSWORD_HASH": hash_})


def verificar_password_admin(password: str) -> bool:
    """Compara una contraseña ingresada contra el hash guardado."""
    valores = cargar()
    salt = valores.get("ADMIN_PASSWORD_SALT", "")
    hash_guardado = valores.get("ADMIN_PASSWORD_HASH", "")
    if not hash_guardado:
        return False
    intento = hashlib.sha256(f"{salt}:{password}".encode("utf-8")).hexdigest()
    return secrets.compare_digest(intento, hash_guardado)


def hay_password_admin() -> bool:
    return bool(cargar().get("ADMIN_PASSWORD_HASH"))


def anonimizar_nombre(nombre: str) -> str:
    """Reduce un nombre a sus iniciales, p. ej. 'María González' -> 'M. G.'"""
    if not nombre or not nombre.strip():
        return "—"
    partes = [p for p in nombre.strip().split() if p]
    return " ".join(f"{p[0].upper()}." for p in partes)


# Acceso directo — usar cfg["NOMBRE_LAB"] en cualquier archivo
cfg = cargar()
