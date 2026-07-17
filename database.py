import sqlite3
import os
import uuid
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "laboratorio.db")
FOTOS_DIR = os.path.join(os.path.dirname(__file__), "fotos")

ESTADOS = ["pendiente", "en_proceso", "listo", "entregado", "cobrado"]

TIPOS_TRABAJO = [
    # --- PRÓTESIS REMOVIBLE ---
    "Prótesis Removible Acrílica (Parcial)",
    "Prótesis Removible Acrílica (Total)",
    "Prótesis Metálica (Esquelético / Cromo)",
    "Prótesis Flexible (Deflex / Valplast)",
    "Provisorio de Acrílico (Removible)",
    
    # --- PRÓTESIS FIJA Y ESTÉTICA ---
    "Corona Metal-Porcelana",
    "Corona Zirconio (Monolítica)",
    "Corona Zirconio (Estratificada)",
    "Corona Disilicato de Litio (e.max)",
    "Carilla de Porcelana / Disilicato",
    "Incrustación (Inlay / Onlay / Overlay)",
    "Puente Fijo (Metal-Porcelana)",
    "Puente Fijo (Zirconio)",
    
    # --- ORTODONCIA, PLANOS Y OTROS ---
    "Plano de Alivio Oclusal (Bruxismo / Miorrelajante)",
    "Aparato de Ortodoncia (Plaquita activa)",
    "Perno Muñón Colado (PPR / Metálico)",
    "Cubeta Individual / Rodete de Cera",
    "Reparación / Rebase / Agregado de Diente",
    "Otro"
]


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def inicializar_db():
    os.makedirs(FOTOS_DIR, exist_ok=True)
    conn = conectar()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            telefono  TEXT,
            notas     TEXT,
            token     TEXT UNIQUE
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS trabajos (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id     INTEGER NOT NULL,
            nombre         TEXT,
            paciente       TEXT,
            tipo_trabajo   TEXT NOT NULL,
            descripcion    TEXT,
            fecha_ingreso  TEXT NOT NULL,
            fecha_entrega  TEXT,
            precio         REAL,
            estado         TEXT NOT NULL DEFAULT 'pendiente',
            foto_path      TEXT,
            notas          TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trabajo_id  INTEGER NOT NULL,
            monto       REAL NOT NULL,
            fecha       TEXT NOT NULL,
            notas       TEXT,
            FOREIGN KEY (trabajo_id) REFERENCES trabajos(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS materiales (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            trabajo_id  INTEGER NOT NULL,
            nombre      TEXT NOT NULL,
            cantidad    REAL,
            unidad      TEXT,
            costo       REAL,
            fecha       TEXT NOT NULL,
            FOREIGN KEY (trabajo_id) REFERENCES trabajos(id)
        )
    """)

    # Migración: columnas nuevas en trabajos
    cols = [r[1] for r in c.execute("PRAGMA table_info(trabajos)").fetchall()]
    for col in ["paciente", "foto_path", "nombre"]:
        if col not in cols:
            c.execute(f"ALTER TABLE trabajos ADD COLUMN {col} TEXT")

    # Migración: token en clientes
    cols_cli = [r[1] for r in c.execute("PRAGMA table_info(clientes)").fetchall()]
    if "token" not in cols_cli:
        c.execute("ALTER TABLE clientes ADD COLUMN token TEXT")

    # Backfill: clientes existentes sin token
    sin_token = c.execute("SELECT id FROM clientes WHERE token IS NULL").fetchall()
    for row in sin_token:
        c.execute("UPDATE clientes SET token = ? WHERE id = ?",
                  (str(uuid.uuid4()), row[0]))

    conn.commit()
    conn.close()


def numero_ot(trabajo_id):
    return f"OT-{trabajo_id:04d}"


# ── CLIENTES ──────────────────────────────────────────────────────────────────

def agregar_cliente(nombre, telefono="", notas=""):
    token = str(uuid.uuid4())
    conn = conectar()
    conn.execute(
        "INSERT INTO clientes (nombre, telefono, notas, token) VALUES (?, ?, ?, ?)",
        (nombre.strip(), telefono.strip(), notas.strip(), token),
    )
    conn.commit()
    conn.close()
    return token


def obtener_clientes():
    conn = conectar()
    rows = conn.execute("SELECT * FROM clientes ORDER BY nombre").fetchall()
    conn.close()
    return rows


def obtener_cliente_por_token(token):
    conn = conectar()
    row = conn.execute(
        "SELECT * FROM clientes WHERE token = ?", (token,)
    ).fetchone()
    conn.close()
    return row


# ── TRABAJOS ──────────────────────────────────────────────────────────────────

def agregar_trabajo(cliente_id, nombre, paciente, tipo, descripcion,
                    fecha_ingreso, fecha_entrega, precio, notas=""):
    conn = conectar()
    conn.execute(
        """INSERT INTO trabajos
           (cliente_id, nombre, paciente, tipo_trabajo, descripcion,
            fecha_ingreso, fecha_entrega, precio, estado, notas)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pendiente', ?)""",
        (cliente_id,
         nombre.strip() if nombre else None,
         paciente.strip() if paciente else None,
         tipo, descripcion.strip() if descripcion else "",
         str(fecha_ingreso),
         str(fecha_entrega) if fecha_entrega else None,
         precio if precio else None,
         notas.strip()),
    )
    trabajo_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return trabajo_id


def obtener_trabajo(trabajo_id):
    conn = conectar()
    row = conn.execute("""
        SELECT t.*, c.nombre AS cliente_nombre
        FROM trabajos t
        JOIN clientes c ON t.cliente_id = c.id
        WHERE t.id = ?
    """, (trabajo_id,)).fetchone()
    conn.close()
    return row


def obtener_trabajos_activos():
    conn = conectar()
    rows = conn.execute("""
        SELECT t.*, c.nombre AS cliente_nombre
        FROM trabajos t
        JOIN clientes c ON t.cliente_id = c.id
        WHERE t.estado != 'cobrado'
        ORDER BY t.fecha_entrega ASC, t.fecha_ingreso ASC
    """).fetchall()
    conn.close()
    return rows


def obtener_todos_trabajos():
    conn = conectar()
    rows = conn.execute("""
        SELECT t.*, c.nombre AS cliente_nombre
        FROM trabajos t
        JOIN clientes c ON t.cliente_id = c.id
        ORDER BY t.fecha_ingreso DESC
    """).fetchall()
    conn.close()
    return rows


def buscar_trabajos(texto):
    conn = conectar()
    texto = texto.strip()
    id_busqueda = None
    if texto.upper().startswith("OT-"):
        try:
            id_busqueda = int(texto[3:])
        except ValueError:
            pass
    else:
        try:
            id_busqueda = int(texto)
        except ValueError:
            pass

    if id_busqueda is not None:
        rows = conn.execute("""
            SELECT t.*, c.nombre AS cliente_nombre
            FROM trabajos t JOIN clientes c ON t.cliente_id = c.id
            WHERE t.id = ?
        """, (id_busqueda,)).fetchall()
    else:
        rows = conn.execute("""
            SELECT t.*, c.nombre AS cliente_nombre
            FROM trabajos t JOIN clientes c ON t.cliente_id = c.id
            WHERE t.paciente LIKE ?
            ORDER BY t.fecha_ingreso DESC
        """, (f"%{texto}%",)).fetchall()

    conn.close()
    return rows


def actualizar_estado(trabajo_id, nuevo_estado):
    conn = conectar()
    conn.execute("UPDATE trabajos SET estado = ? WHERE id = ?", (nuevo_estado, trabajo_id))
    conn.commit()
    conn.close()


def guardar_foto(trabajo_id, archivo_bytes, extension):
    os.makedirs(FOTOS_DIR, exist_ok=True)
    ruta = os.path.join(FOTOS_DIR, f"{trabajo_id}.{extension}")
    with open(ruta, "wb") as f:
        f.write(archivo_bytes)
    conn = conectar()
    conn.execute("UPDATE trabajos SET foto_path = ? WHERE id = ?", (ruta, trabajo_id))
    conn.commit()
    conn.close()
    return ruta


# ── PAGOS ─────────────────────────────────────────────────────────────────────

def registrar_pago(trabajo_id, monto, fecha, notas=""):
    conn = conectar()
    conn.execute(
        "INSERT INTO pagos (trabajo_id, monto, fecha, notas) VALUES (?, ?, ?, ?)",
        (trabajo_id, monto, str(fecha), notas.strip()),
    )
    conn.execute("UPDATE trabajos SET estado = 'cobrado' WHERE id = ?", (trabajo_id,))
    conn.commit()
    conn.close()


def deuda_por_cliente():
    conn = conectar()
    rows = conn.execute("""
        SELECT c.nombre, SUM(t.precio) AS deuda
        FROM trabajos t JOIN clientes c ON t.cliente_id = c.id
        WHERE t.estado = 'entregado'
        GROUP BY c.id HAVING deuda > 0
        ORDER BY deuda DESC
    """).fetchall()
    conn.close()
    return rows


def resumen_general():
    conn = conectar()
    activos = conn.execute(
        "SELECT COUNT(*) FROM trabajos WHERE estado != 'cobrado'"
    ).fetchone()[0]
    listos = conn.execute(
        "SELECT COUNT(*) FROM trabajos WHERE estado = 'listo'"
    ).fetchone()[0]
    deuda = conn.execute(
        "SELECT COALESCE(SUM(precio), 0) FROM trabajos WHERE estado = 'entregado'"
    ).fetchone()[0]
    cobrado_mes = conn.execute("""
        SELECT COALESCE(SUM(p.monto), 0) FROM pagos p
        WHERE strftime('%Y-%m', p.fecha) = strftime('%Y-%m', 'now')
    """).fetchone()[0]
    conn.close()
    return {"activos": activos, "listos_para_entregar": listos,
            "deuda_total": deuda, "cobrado_este_mes": cobrado_mes}


# ── MATERIALES ────────────────────────────────────────────────────────────────

def agregar_material(trabajo_id, nombre, cantidad, unidad, costo, fecha=None):
    conn = conectar()
    conn.execute(
        "INSERT INTO materiales (trabajo_id, nombre, cantidad, unidad, costo, fecha) VALUES (?, ?, ?, ?, ?, ?)",
        (trabajo_id, nombre.strip(), cantidad, unidad,
         costo if costo else None, str(fecha or date.today())),
    )
    conn.commit()
    conn.close()


def obtener_materiales(trabajo_id):
    conn = conectar()
    rows = conn.execute(
        "SELECT * FROM materiales WHERE trabajo_id = ? ORDER BY id", (trabajo_id,)
    ).fetchall()
    conn.close()
    return rows


def eliminar_material(material_id):
    conn = conectar()
    conn.execute("DELETE FROM materiales WHERE id = ?", (material_id,))
    conn.commit()
    conn.close()


def costo_total_materiales(trabajo_id):
    conn = conectar()
    total = conn.execute(
        "SELECT COALESCE(SUM(costo), 0) FROM materiales WHERE trabajo_id = ?",
        (trabajo_id,),
    ).fetchone()[0]
    conn.close()
    return total


# ── COBROS ────────────────────────────────────────────────────────────────────

def trabajos_por_cliente_mes(cliente_id, anio, mes):
    """Trabajos entregados o cobrados de un cliente en un mes dado."""
    conn = conectar()
    rows = conn.execute("""
        SELECT t.*, c.nombre AS cliente_nombre
        FROM trabajos t JOIN clientes c ON t.cliente_id = c.id
        WHERE t.cliente_id = ?
          AND t.estado IN ('entregado', 'cobrado')
          AND strftime('%Y', t.fecha_entrega) = ?
          AND strftime('%m', t.fecha_entrega) = ?
        ORDER BY t.fecha_entrega ASC
    """, (cliente_id, str(anio), f"{mes:02d}")).fetchall()
    conn.close()
    return rows
