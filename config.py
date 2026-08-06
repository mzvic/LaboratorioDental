"""
config.py — Lee y escribe la configuración del laboratorio desde .env
Importar con: from config import cfg
"""

import os
from dotenv import dotenv_values, set_key

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

# Valores por defecto (si falta alguna clave en el .env)
DEFAULTS = {
    "NOMBRE_LAB":      "Laboratorio Dental",
    "TELEFONO_LAB":    "",
    "EMAIL_LAB":       "",
    "DIRECCION_LAB":   "",
    "BANCO":           "",
    "TIPO_CUENTA":     "",
    "NUMERO_CUENTA":   "",
    "RUT_LAB":         "",
    "NOMBRE_TITULAR":  "",
    "PORTAL_BASE":     "http://localhost:8502",
    "LOGO_PATH":       "logo.jpeg",
    "LOGO_APP_PATH":   "Sincrodent.png",
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


# Acceso directo — usar cfg["NOMBRE_LAB"] en cualquier archivo
cfg = cargar()
