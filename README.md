## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Frontend / UI:** Streamlit
* **Base de Datos:** SQLite (`data/laboratorio.db`)
* **Generación de Documentos:** ReportLab
* **Configuración:** `python-dotenv`

---

## 📂 Estructura del Proyecto

```text
.
├── app.py              # Dashboard principal (Panel de administración del laboratorio)
├── portal.py           # Portal ligero para clientes/dentistas (Ingreso vía token)
├── database.py         # Conexión, tablas y queries de la base de datos (SQLite)
├── pdfs.py             # Motor de generación de PDFs (OT y Cierres de Cobro)
├── config.py           # Lectura y persistencia de variables de entorno (.env)
├── data/
│   └── laboratorio.db  # Base de datos SQLite
├── uploads/            # Archivos e imágenes adjuntas a las OT
├── .env                # Plantilla de configuración
└── requirements.txt    # Dependencias del proyecto
```

---

## 🗄️ Modelo de Datos

La base de datos SQLite consta de 4 tablas principales:
* **`clientes`:** Registro de clínicas y dentistas. Incluye token único (UUID) para acceso al portal.
* **`trabajos`:** Órdenes de Trabajo (OT), fechas, montos, estados y paciente.
* **`materiales`:** Insumos y costos asociados a cada OT.
* **`pagos`:** Historial de abonos y cancelaciones.

### 🔄 Ciclo de Vida de una Orden de Trabajo (OT)
`pendiente` ➔ `en_proceso` ➔ `listo` ➔ `entregado` ➔ `cobrado`

---

## ⚙️ Instalación y Configuración Local

### 1. Clonar el repositorio e instalar dependencias
```bash
git clone https://github.com/tu-usuario/sincrodent.git
cd sincrodent

# Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Linux/macOS
# venv\Scripts\activate   # En Windows

# Instalar librerías
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
# ── Datos del laboratorio ──────────────────────────────────────────────────────
NOMBRE_LAB=
TELEFONO_LAB=
EMAIL_LAB=
DIRECCION_LAB=

# ── Datos bancarios (para órdenes de cobro PDF) ────────────────────────────────
BANCO=
TIPO_CUENTA=
NUMERO_CUENTA=
RUT_LAB=
NOMBRE_TITULAR=

# ── Configuración del portal ───────────────────────────────────────────────────
PORTAL_BASE=

# ── Logo ───────────────────────────────────────────────────────────────────────
LOGO_PATH=logo.jpeg
LOGO_APP_PATH=Sincrodent.png
```

---

## 🚀 Ejecución

El proyecto consta de dos aplicaciones Streamlit independientes:

### 1. Panel del Laboratorio (`app.py`)
Acceso administrativo para gestión de clientes, estados, KPIs y facturación:
```bash
streamlit run app.py --server.port 8501
```

### 2. Portal del Dentista (`portal.py`)
Interfaz para que las clínicas levanten órdenes directamente utilizando su link único (`http://localhost:8502/?token=TU_TOKEN`):
```bash
streamlit run portal.py --server.port 8502
```

---

## 📝 Reglas de Negocio Destacadas

* **Acceso por Token:** Los clientes acceden a su portal dinámico mediante tokens en la URL, sin necesidad de contraseña.
* **Soporte `[confidencial]`:** Las notas marcadas con la flag `[confidencial]` ocultan el nombre de la clínica/dentista en la vista operativa para mantener la privacidad de trabajos subcontratados.
