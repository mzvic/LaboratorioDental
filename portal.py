# portal.py — Portal exclusivo para clínicas/dentistas.
import streamlit as st
from datetime import date, timedelta
import database as db
import os
from config import cargar

_cfg = cargar()
NOMBRE_LABORATORIO = _cfg["NOMBRE_LAB"] or "Laboratorio Dental"
LOGO_LAB_PATH = _cfg["LOGO_PATH"]
LOGO_APP_PATH = _cfg["LOGO_APP_PATH"]

st.set_page_config(
    page_title="Sincrodent — Portal del Dentista",
    page_icon=LOGO_APP_PATH if os.path.exists(LOGO_APP_PATH) else ":material/dentistry:",
    layout="centered",
    initial_sidebar_state="collapsed",
)

db.inicializar_db()

if _cfg["SETUP_COMPLETO"] != "1":
    st.error(
        "Este laboratorio todavía no completó la configuración inicial. "
        "Pide al administrador que ingrese al panel principal y complete el asistente de configuración."
    )
    st.stop()

if os.environ.get("SINCRODENT_DEMO") == "1":
    st.markdown(
        '<div style="background:#FEF3C7;border:1px solid #F59E0B;border-radius:8px;'
        'padding:.65rem 1rem;margin:0 0 1rem;font-size:12px;color:#92400E;line-height:1.5">'
        '<strong>Portal de demostración</strong> — este es un ambiente de prueba abierto a cualquiera. '
        'Las órdenes que envíes aquí se borran automáticamente cada cierto tiempo. '
        'No ingreses datos reales de pacientes.'
        '</div>', unsafe_allow_html=True,
    )

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fredoka:wght@500;600;700&display=swap');

:root {
    --sc-navy: #022C54;
    --sc-navy-2: #0B3F70;
    --sc-teal: #009097;
    --sc-teal-dark: #00676C;
    --sc-teal-tint: #E3F5F5;
    --sc-white: #FEFEFE;
    --font-brand: 'Fredoka', 'Inter', sans-serif;
}

html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; color-scheme: light only; }
.sc-brand { font-family: var(--font-brand); font-weight: 600; letter-spacing: -.01em; }

/* Ocultar elementos predeterminados de Streamlit */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
header { visibility: hidden; }

/* Contenido principal centrado */
.main .block-container { max-width: 700px; padding-top: 1.5rem; padding-left: 1rem; padding-right: 1rem; }

/* Botones principales con el Azul de Sincrodent */
.stButton > button {
    background: var(--sc-navy) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: .5rem 1rem !important;
    transition: background .15s !important;
}
.stButton > button:hover { 
    background: var(--sc-teal) !important; 
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: var(--sc-navy) !important;
    border: 1px solid #CBD5E1 !important;
}
.stButton > button[kind="secondary"]:hover {
    background: var(--sc-teal-tint) !important;
    color: var(--sc-teal-dark) !important;
    border-color: var(--sc-teal) !important;
}

/* Inputs y Selectbox */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--sc-teal) !important;
    box-shadow: 0 0 0 3px rgba(0,144,151,.10) !important;
}

/* Sección label */
.section-label {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: .07em;
    margin: 1.5rem 0 .75rem;
}

@media (max-width: 640px) {
    .portal-header-title { font-size: 18px !important; }
    .portal-header-sub { font-size: 11px !important; }
}
</style>
""", unsafe_allow_html=True)

# ── Leer token de la URL ───────────────────────────────────────────────────────
params = st.query_params
token  = params.get("token", "")

# ── Validar token ──────────────────────────────────────────────────────────────
if not token:
    st.error("Link inválido. Solicite el link correcto al laboratorio.")
    st.stop()

cliente = db.obtener_cliente_por_token(token)

if not cliente:
    st.error("Link inválido o expirado. Solicite uno nuevo al laboratorio.")
    st.stop()

# ── Encabezado del Portal ─────────────────────────────────────────────────────
col_logo_lab, col_titulo, col_logo_app = st.columns([1.2, 3.6, 1.2], vertical_alignment="center")

with col_logo_lab:
    if os.path.exists(LOGO_LAB_PATH):
        st.image(LOGO_LAB_PATH, width=55)
    else:
        st.markdown(':material/local_hospital:', unsafe_allow_html=True)

with col_titulo:
    st.markdown(
        "<div style='text-align: center;'>"
        "<h3 class='portal-header-title sc-brand' style='margin-bottom:0; font-size:21px; line-height: 1.2;'>"
        "<span style='color:var(--sc-navy)'>Sincro</span><span style='color:var(--sc-teal)'>dent</span></h3>"
        "<p class='portal-header-sub' style='color:#94A3B8; font-size:11px; margin:2px 0 0 0;'>Portal de Solicitudes para Clínicas y Dentistas</p>"
        "</div>",
        unsafe_allow_html=True
    )

with col_logo_app:
    st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
    if os.path.exists(LOGO_APP_PATH):
        st.image(LOGO_APP_PATH, width=55)
    else:
        st.markdown(':material/dentistry:', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<hr style="border:none;border-top:2px solid var(--sc-teal-tint);margin:.5rem 0 1.25rem">', unsafe_allow_html=True)

# Bienvenida personalizada
st.markdown(
    f'<h1 style="color:var(--sc-navy); font-size:22px; font-weight:700; margin-bottom:4px">Hola, {cliente["nombre"]}</h1>'
    f'<p style="color:#94A3B8; font-size:13px; margin-bottom:1.5rem">'
    f'Complete el formulario a continuación para enviar una nueva orden directamente al laboratorio.</p>',
    unsafe_allow_html=True,
)

st.markdown('<p style="font-size:0.85rem; color:#64748B;">Los campos marcados con <span style="color:var(--sc-teal); font-weight:bold;">*</span> son obligatorios.</p>', unsafe_allow_html=True)

with st.form("form_portal", clear_on_submit=True):

    # ── Datos del paciente ──
    st.markdown('<div class="section-label">Paciente</div>', unsafe_allow_html=True)
    paciente = st.text_input("Nombre del paciente *", placeholder="Ej: María González")

    # ── Tipo de trabajo ──
    st.markdown('<div class="section-label">Trabajo solicitado</div>', unsafe_allow_html=True)
    tipo = st.selectbox("Tipo de trabajo *", db.TIPOS_TRABAJO)
    nombre_trabajo = st.text_input("Descripción corta del trabajo *", placeholder="Ej: Corona pieza 14")

    # ── Especificaciones técnicas ──
    st.markdown('<div class="section-label">Especificaciones técnicas</div>', unsafe_allow_html=True)

    PIEZAS_FDI = [str(n) for n in list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))]

    col1, col2 = st.columns(2)
    arcada = col1.selectbox("Arcada *", ["Superior", "Inferior", "Ambas"])

    GUIA_VITA = [
        "A1", "A2", "A3", "A3.5", "A4",
        "B1", "B2", "B3", "B4",
        "C1", "C2", "C3", "C4",
        "D2", "D3", "D4",
        "Otro / No aplica",
    ]
    color = col2.selectbox("Color (guía VITA) *", GUIA_VITA)

    piezas = st.multiselect(
        "Pieza(s) dentaria(s) — numeración FDI *", PIEZAS_FDI,
        placeholder="Selecciona una o más piezas",
    )

    col3, col4 = st.columns(2)
    material = col3.selectbox("Material preferido", [
        "Sin preferencia",
        "Metal-porcelana",
        "Zirconio",
        "Acrílico",
        "Cromo-cobalto",
        "Otro",
    ])
    oclusion = col4.selectbox("Tipo de oclusión / articulador", [
        "No aplica",
        "Balanceada",
        "Canina protegida",
        "Función de grupo",
    ])
    textura = st.selectbox("Textura / acabado superficial", [
        "No aplica",
        "Alto brillo",
        "Satinado",
        "Texturizado natural",
    ])

    descripcion = st.text_area(
        "Instrucciones adicionales",
        placeholder="Detalles de forma, referencias, casos especiales, etc.",
        height=90,
    )

    # ── Fechas ──
    st.markdown('<div class="section-label">Fecha de entrega</div>', unsafe_allow_html=True)
    fecha_minima = date.today() + timedelta(days=3)
    fecha_entrega = st.date_input(
        "Fecha de entrega solicitada *",
        value=fecha_minima,
        min_value=fecha_minima,
    )

    # ── Foto / archivo adjunto ──
    st.markdown('<div class="section-label">Fotos o archivos de escaneo (opcional)</div>', unsafe_allow_html=True)
    fotos = st.file_uploader(
        "Adjuntar foto(s) clínica(s) o archivo(s) de escaneo intraoral (STL, PLY, OBJ, ZIP, PDF)",
        type=db.EXTENSIONES_ADJUNTO,
        accept_multiple_files=True,
    )

    st.divider()
    enviado = st.form_submit_button(f"Enviar orden a {NOMBRE_LABORATORIO}", type="primary", use_container_width=True, icon=":material/send:")

# ── Procesar envío ──────────────────────────────────────────────────────────────
if enviado:
    errores = []
    if not paciente.strip():
        errores.append("El nombre del paciente es obligatorio.")
    if not nombre_trabajo.strip():
        errores.append("La descripción del trabajo es obligatoria.")
    if not piezas:
        errores.append("Debes seleccionar al menos una pieza dentaria.")

    if errores:
        for e in errores:
            st.toast(e, icon=":material/error:") # <-- Popup rojo/alerta si hay errores
    else:
        descripcion_completa = (
            f"Arcada: {arcada} | Color: {color} | Pieza(s): {', '.join(piezas)} | "
            f"Material: {material} | Oclusión: {oclusion} | Textura: {textura}"
            + (f"\n{descripcion.strip()}" if descripcion.strip() else "")
        )

        trabajo_id = db.agregar_trabajo(
            cliente_id    = cliente["id"],
            nombre        = nombre_trabajo,
            paciente      = paciente,
            tipo          = tipo,
            descripcion   = descripcion_completa,
            fecha_ingreso = date.today(),
            fecha_entrega = fecha_entrega,
            precio        = None,   # El laboratorio define el precio posteriormente
            notas         = f"Enviado por portal — {cliente['nombre']}",
        )

        for f in fotos or []:
            ext = f.name.rsplit(".", 1)[-1].lower()
            db.agregar_adjunto(trabajo_id, f.read(), ext, f.name)

        ot = db.numero_ot(trabajo_id)

        try:
            from notificaciones import notificar_orden_nueva
            enviado, error = notificar_orden_nueva(cliente["nombre"], tipo, nombre_trabajo, ot)
            if not enviado and error:
                with open("notif_errores.log", "a") as f:
                    f.write(f"{date.today()} — {error}\n")
        except Exception as e:
            with open("notif_errores.log", "a") as f:
                f.write(f"{date.today()} — {e}\n")

        st.success(f"Orden enviada correctamente a {NOMBRE_LABORATORIO}. Su número de seguimiento asignado es **{ot}**.", icon=":material/check_circle:")
        st.info(f"El laboratorio revisará su solicitud y confirmará la recepción para la fecha estimada del **{fecha_entrega.strftime('%d/%m/%Y')}**.")
            
        st.toast("¡Orden enviada con éxito al laboratorio!", icon=":material/check_circle:")

# ── MIS ÓRDENES ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<h2 style="color:var(--sc-navy);font-size:20px;font-weight:700;margin-bottom:4px">Mis órdenes</h2>'
    '<p style="color:#94A3B8;font-size:13px;margin-bottom:1rem">Estado actual de sus trabajos en el laboratorio.</p>',
    unsafe_allow_html=True,
)

ESTADO_LABELS = {
    "pendiente":  ("🔵", "Pendiente",   "#EFF6FF", "#2563EB"),
    "en_proceso": ("🟡", "En Proceso",  "#FFFBEB", "#B45309"),
    "listo":      ("🟢", "Listo",       "#F0FDF4", "#16A34A"),
    "entregado":  ("🟠", "Entregado",   "#FFF7ED", "#EA580C"),
    "cobrado":    ("✅", "Cobrado",     "#F0FDF4", "#15803D"),
}

mis_trabajos = db.obtener_trabajos_por_cliente(cliente["id"])

if not mis_trabajos:
    st.markdown(
        '<div style="text-align:center;padding:2rem;color:#CBD5E1;background:#F8FAFC;border-radius:10px;border:1px dashed #E2E8F0">'
        'Aún no tiene órdenes enviadas.</div>',
        unsafe_allow_html=True,
    )
else:
    for t in mis_trabajos:
        emoji, label, bg, color = ESTADO_LABELS.get(t["estado"], ("⚪", t["estado"], "#F8FAFC", "#64748B"))
        nombre_ot = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
        ot_num = db.numero_ot(t["id"])
        
        # Título para la vista colapsable
        titulo_expander = f"{ot_num} · {nombre_ot} ({t['paciente'] or 'Sin paciente'}) — {emoji} {label}"
        
        with st.expander(titulo_expander):
            st.markdown(f"**Tipo de trabajo:** {t['tipo_trabajo']}")
            if t["paciente"]:
                st.markdown(f"**Paciente:** {t['paciente']}")
            if t["fecha_entrega"]:
                st.markdown(f"**Fecha estimada de entrega:** {t['fecha_entrega']}")
            if t["descripcion"]:
                st.markdown(f"**Detalles:** {t['descripcion']}")
            if t["foto_path"] and os.path.exists(t["foto_path"]):
                if db.es_imagen(t["foto_path"]):
                    st.image(t["foto_path"], width=200)
                else:
                    with open(t["foto_path"], "rb") as f:
                        st.download_button(
                            f"Descargar archivo adjunto ({os.path.basename(t['foto_path'])})",
                            data=f.read(), file_name=os.path.basename(t["foto_path"]),
                            icon=":material/download:", key=f"dl_adj_{t['id']}",
                        )
            for adj in db.obtener_adjuntos(t["id"]):
                if not os.path.exists(adj["ruta"]):
                    continue
                if db.es_imagen(adj["ruta"]):
                    st.image(adj["ruta"], width=200, caption=adj["nombre_original"])
                else:
                    with open(adj["ruta"], "rb") as f:
                        st.download_button(
                            f"Descargar {adj['nombre_original']}",
                            data=f.read(), file_name=adj["nombre_original"],
                            icon=":material/download:", key=f"dl_adj_new_{adj['id']}",
                        )

            st.divider()