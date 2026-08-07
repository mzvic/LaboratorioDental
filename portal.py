# portal.py — Portal exclusivo para clínicas/dentistas.
import streamlit as st
from datetime import date, timedelta
import database as db
import os

NOMBRE_LABORATORIO = "Laboratorio OdontoMax"

st.set_page_config(
    page_title="Sincrodent — Portal del Dentista",
    page_icon="Sincrodent.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

db.inicializar_db()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

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
    background: #0F2A4A !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: .5rem 1rem !important;
    transition: background .15s !important;
}
.stButton > button:hover { 
    background: #1E3A5F !important; 
}
.stButton > button[kind="secondary"] {
    background: white !important;
    color: #1E3A5F !important;
    border: 1px solid #CBD5E1 !important;
}

/* Inputs y Selectbox */
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #008B8B !important;
    box-shadow: 0 0 0 3px rgba(0,139,139,.08) !important;
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
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=55)
    else:
        st.markdown("🏢", unsafe_allow_html=True)

with col_titulo:
    st.markdown(
        "<div style='text-align: center;'>"
        "<h3 class='portal-header-title' style='margin-bottom:0; color:#1E3A5F; font-size:19px; font-weight:700; line-height: 1.2;'>Sincrodent</h3>"
        "<p class='portal-header-sub' style='color:#94A3B8; font-size:11px; margin:2px 0 0 0;'>Portal de Solicitudes para Clínicas y Dentistas</p>"
        "</div>",
        unsafe_allow_html=True
    )

with col_logo_app:
    st.markdown("<div style='display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
    if os.path.exists("Sincrodent.png"):
        st.image("Sincrodent.png", width=55)
    else:
        st.markdown("🦷", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Bienvenida personalizada
st.markdown(
    f'<h1 style="color:#1E3A5F; font-size:22px; font-weight:700; margin-bottom:4px">Hola, {cliente["nombre"]} 👋</h1>'
    f'<p style="color:#94A3B8; font-size:13px; margin-bottom:1.5rem">'
    f'Complete el formulario a continuación para enviar una nueva orden directamente al laboratorio.</p>',
    unsafe_allow_html=True,
)

st.markdown('<p style="font-size:0.85rem; color:#64748B;">Los campos marcados con <span style="color:#008B8B; font-weight:bold;">*</span> son obligatorios.</p>', unsafe_allow_html=True)

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
    col1, col2 = st.columns(2)

    GUIA_VITA = [
        "A1", "A2", "A3", "A3.5", "A4",
        "B1", "B2", "B3", "B4",
        "C1", "C2", "C3", "C4",
        "D2", "D3", "D4",
        "Otro / No aplica",
    ]
    color = col1.selectbox("Color (guía VITA) *", GUIA_VITA)
    diente = col2.text_input("Número(s) de pieza(s) *", placeholder="Ej: 14, 15-17")

    material = st.selectbox("Material preferido", [
        "Sin preferencia",
        "Metal-porcelana",
        "Zirconio",
        "Acrílico",
        "Cromo-cobalto",
        "Otro",
    ])

    descripcion = st.text_area(
        "Instrucciones adicionales",
        placeholder="Detalles de oclusión, forma, referencias, etc.",
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
    st.markdown('<div class="section-label">Fotografía (opcional)</div>', unsafe_allow_html=True)
    foto = st.file_uploader(
        "Adjuntar foto del caso (impresión, foto clínica, etc.)",
        type=["jpg", "jpeg", "png"],
    )

    st.divider()
    enviado = st.form_submit_button(f"📤 Enviar orden a {NOMBRE_LABORATORIO}", type="primary", use_container_width=True)

# ── Procesar envío ──────────────────────────────────────────────────────────────
if enviado:
    errores = []
    if not paciente.strip():
        errores.append("El nombre del paciente es obligatorio.")
    if not nombre_trabajo.strip():
        errores.append("La descripción del trabajo es obligatoria.")
    if not diente.strip():
        errores.append("El número de pieza(s) es obligatorio.")

    if errores:
        for e in errores:
            st.error(e)
    else:
        descripcion_completa = (
            f"Color: {color} | Pieza(s): {diente} | Material: {material}"
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

        if foto:
            ext = foto.name.rsplit(".", 1)[-1].lower()
            db.guardar_foto(trabajo_id, foto.read(), ext)

        ot = db.numero_ot(trabajo_id)

        st.success(f"✅ Orden enviada correctamente a {NOMBRE_LABORATORIO}. Su número de seguimiento asignado es **{ot}**.")
        st.info(
            f"El laboratorio revisará su solicitud y confirmará la recepción para la fecha estimada del **{fecha_entrega.strftime('%d/%m/%Y')}**."
        )
        st.balloons()

# ── MIS ÓRDENES ────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<h2 style="color:#1E3A5F;font-size:20px;font-weight:700;margin-bottom:4px">Mis órdenes</h2>'
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
                st.image(t["foto_path"], width=200)

            st.divider()
            
           
