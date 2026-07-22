import streamlit as st
from datetime import date, datetime
import calendar
import os
import database as db
import pdfs

st.set_page_config(
    page_title="Sincrodent — Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

db.inicializar_db()

# ── CSS PERSONALIZADO ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Fuente y base */
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #1E3A5F;
    border-right: none;
}
section[data-testid="stSidebar"] * { color: #E8EEF4 !important; }
section[data-testid="stSidebar"] .stRadio label { 
    font-size: 14px !important; 
    padding: 4px 0;
}
section[data-testid="stSidebar"] hr { border-color: #2D5080 !important; }
section[data-testid="stSidebar"] input {
    background: #2D5080 !important;
    border: 1px solid #3D6090 !important;
    color: white !important;
    border-radius: 6px !important;
}

/* Métricas */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
[data-testid="stMetricLabel"] { 
    font-size: 12px !important; 
    color: #64748B !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: .04em;
}
[data-testid="stMetricValue"] { 
    font-size: 28px !important; 
    font-weight: 600 !important;
    color: #1E3A5F !important;
}

/* Botón primario */
.stButton > button {
    background: #1E3A5F;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
    padding: 0.4rem 1rem;
    transition: background .2s;
}
.stButton > button:hover { background: #2D5080; color: white; }

/* Botón volver */
button[kind="secondary"] {
    background: #F1F5F9 !important;
    color: #1E3A5F !important;
    border: 1px solid #CBD5E1 !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #F8FAFC !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    color: #1E3A5F !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    font-size: 13px;
    font-weight: 500;
    color: #64748B;
}
.stTabs [aria-selected="true"] { color: #1E3A5F !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox select {
    border-radius: 8px !important;
    border: 1px solid #CBD5E1 !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #1E3A5F !important;
    box-shadow: 0 0 0 2px rgba(30,58,95,.1) !important;
}

/* Alertas personalizadas */
.alerta-critica {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #EF4444;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 16px;
}
.alerta-critica .titulo { 
    color: #991B1B; 
    font-weight: 600; 
    font-size: 14px;
    margin-bottom: 4px;
}
.alerta-critica .detalle { color: #7F1D1D; font-size: 13px; }

/* Card de deuda */
.deuda-card {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.deuda-nombre { color: #92400E; font-weight: 500; font-size: 14px; }
.deuda-monto { color: #B45309; font-weight: 700; font-size: 15px; }

/* Fila de trabajo */
.ot-row {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: box-shadow .15s;
}
.ot-row:hover { box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.ot-num { font-weight: 700; color: #1E3A5F; font-size: 13px; min-width: 70px; }
.ot-nombre { font-weight: 500; color: #1A1A2E; font-size: 13px; }
.ot-meta { color: #64748B; font-size: 12px; }
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .04em;
}
.badge-pendiente   { background: #EFF6FF; color: #1D4ED8; }
.badge-en_proceso  { background: #FEFCE8; color: #854D0E; }
.badge-listo       { background: #F0FDF4; color: #166534; }
.badge-entregado   { background: #FFF7ED; color: #9A3412; }
.badge-cobrado     { background: #F0FDF4; color: #166534; }
.badge-atrasado    { background: #FEF2F2; color: #991B1B; }

/* Título de sección */
.section-title {
    font-size: 13px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: .06em;
    margin: 1.5rem 0 .75rem;
    padding-bottom: 6px;
    border-bottom: 1px solid #E2E8F0;
}

/* Sin datos */
.empty-state {
    text-align: center;
    padding: 2rem;
    color: #94A3B8;
    font-size: 14px;
    background: #F8FAFC;
    border-radius: 10px;
    border: 1px dashed #CBD5E1;
}

/* Ocultar solo el branding de Streamlit, NO el toggle del sidebar en móvil */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

/* Sidebar radio — quitar círculos, estilizar como nav */
section[data-testid="stSidebar"] div[data-baseweb="radio"] > div:first-child {
    display: none !important;
}
section[data-testid="stSidebar"] div[data-baseweb="radio"] {
    border-radius: 8px;
    transition: background .15s;
    margin: 1px 0;
}
section[data-testid="stSidebar"] div[data-baseweb="radio"]:hover {
    background: rgba(255,255,255,.1);
}
section[data-testid="stSidebar"] div[data-baseweb="radio"]:has(input:checked) {
    background: rgba(255,255,255,.15) !important;
    border-left: 3px solid #5B9BD5 !important;
    border-radius: 0 8px 8px 0 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="radio"]:has(input:checked) label {
    font-weight: 600 !important;
    color: white !important;
}
section[data-testid="stSidebar"] div[data-baseweb="radio"] label {
    padding: 9px 14px !important;
    font-size: 14px !important;
    cursor: pointer;
    width: 100%;
}

/* Barra nav móvil — visible solo en pantallas pequeñas */
.nav-movil {
    background: #1E3A5F;
    border-radius: 10px;
    padding: 6px 10px;
    margin-bottom: 4px;
}
.nav-movil-widget {
    margin-bottom: 16px;
}
@media (min-width: 768px) {
    .nav-movil,
    .nav-movil-widget {
        display: none !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
BADGE_ESTADO = {
    "pendiente":  '<span class="badge badge-pendiente">Pendiente</span>',
    "en_proceso": '<span class="badge badge-en_proceso">En proceso</span>',
    "listo":      '<span class="badge badge-listo">Listo</span>',
    "entregado":  '<span class="badge badge-entregado">Entregado</span>',
    "cobrado":    '<span class="badge badge-cobrado">✓ Cobrado</span>',
}
EMOJI_ESTADO = {
    "pendiente": "🔵", "en_proceso": "🟡",
    "listo": "🟢", "entregado": "🟠", "cobrado": "✅",
}
MESES_ES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
PORTAL_BASE = "http://portal.odontomax.mzvic.xyz"

if "detalle_id" not in st.session_state:
    st.session_state.detalle_id = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "📊 Dashboard"

NAV_OPCIONES = ["📊 Dashboard","➕ Nueva orden","👥 Clientes","📋 Historial","💰 Cobros"]
# ── HELPERS ────────────────────────────────────────────────────────────────────
def es_atrasado(t):
    return (t["fecha_entrega"]
            and t["fecha_entrega"] < str(date.today())
            and t["estado"] not in ("entregado", "cobrado"))


def fila_trabajo(t):
    nombre = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
    atraso = " ⚠️" if es_atrasado(t) else ""
    emoji  = EMOJI_ESTADO.get(t["estado"], "⚪")
    titulo = f"{emoji} {db.numero_ot(t['id'])} · {nombre} · {t['cliente_nombre']}{atraso}"

    with st.expander(titulo):
        col_datos, col_btn = st.columns([3, 1])
        with col_datos:
            if t["paciente"]:
                st.markdown(f'👤 **{t["paciente"]}**')
            badge = BADGE_ESTADO.get(t["estado"], "")
            badge_atraso = ' <span class="badge badge-atrasado">⚠ Atrasado</span>' if es_atrasado(t) else ""
            st.markdown(f'{badge}{badge_atraso}', unsafe_allow_html=True)
            if t["fecha_entrega"]:
                st.caption(f"Entrega: {t['fecha_entrega']}")
            if t["precio"]:
                st.caption(f"Precio: ${t['precio']:,.0f}")
        with col_btn:
            if st.button("Abrir", key=f"abrir_{t['id']}"):
                st.session_state.detalle_id = t["id"]
                st.rerun()



# ── VISTA DETALLE ──────────────────────────────────────────────────────────────
def vista_detalle(trabajo_id):
    t = db.obtener_trabajo(trabajo_id)
    if not t:
        st.error("Esa orden ya no existe.")
        st.session_state.detalle_id = None
        return

    if st.button("← Volver", type="secondary"):
        st.session_state.detalle_id = None
        st.rerun()

    ot = db.numero_ot(t["id"])
    nombre_mostrar = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
    badge = BADGE_ESTADO.get(t["estado"], "")
    atraso = ' <span class="badge badge-atrasado">⚠ Atrasado</span>' if es_atrasado(t) else ""

    st.markdown(
        f'<h1 style="color:#1E3A5F;margin-bottom:4px">{ot} — {nombre_mostrar}</h1>'
        f'<div style="margin-bottom:1rem">{badge}{atraso}</div>',
        unsafe_allow_html=True,
    )

    tab_info, tab_mat, tab_edit = st.tabs(["📋 Información", "📦 Elementos utilizados", "✏️ Editar Orden"])

    # ─── INFO ──────────────────────────────────────────────────────────────────
    with tab_info:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Cliente", t["cliente_nombre"])
        col2.metric("Paciente", t["paciente"] or "—")
        col3.metric("Ingreso", t["fecha_ingreso"])
        col4.metric("Entrega", t["fecha_entrega"] or "—")

        col5, col6 = st.columns(2)
        col5.metric("Tipo", t["tipo_trabajo"])
        col6.metric("Precio", f"${t['precio']:,.0f}" if t["precio"] else "—")

        if t["descripcion"]:
            st.markdown(f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;padding:12px 16px;margin-top:8px"><span style="font-size:12px;color:#64748B;font-weight:500;text-transform:uppercase;letter-spacing:.04em">Descripción</span><p style="margin:4px 0 0;color:#1A1A2E;font-size:14px">{t["descripcion"]}</p></div>', unsafe_allow_html=True)
        if t["notas"]:
            st.caption(f"📝 {t['notas']}")

        if t["foto_path"] and os.path.exists(t["foto_path"]):
            st.image(t["foto_path"], caption="Foto del trabajo", width=320)

        foto_nueva = st.file_uploader("Subir / reemplazar foto", type=["jpg","jpeg","png"], key=f"foto_{t['id']}")
        if foto_nueva:
            ext = foto_nueva.name.rsplit(".", 1)[-1].lower()
            db.guardar_foto(t["id"], foto_nueva.read(), ext)
            st.success("Foto guardada.")
            st.rerun()

        st.divider()
        col_estado, col_cobro, col_pdf = st.columns(3)

        with col_estado:
            nuevo_estado = st.selectbox("Estado", db.ESTADOS,
                index=db.ESTADOS.index(t["estado"]), key=f"estado_{t['id']}")
            if nuevo_estado != t["estado"]:
                if st.button("Actualizar estado", key=f"btn_estado_{t['id']}"):
                    db.actualizar_estado(t["id"], nuevo_estado)
                    st.rerun()

        with col_cobro:
            if t["estado"] == "entregado" and t["precio"]:
                st.markdown(f'<p style="font-weight:600;color:#166534;margin-bottom:8px">Cobrar ${t["precio"]:,.0f}</p>', unsafe_allow_html=True)
                if st.button("✅ Marcar como cobrado", key=f"cobrar_{t['id']}"):
                    db.registrar_pago(t["id"], t["precio"], date.today())
                    st.success("Pago registrado.")
                    st.rerun()

        with col_pdf:
            materiales = db.obtener_materiales(t["id"])
            pdf_bytes = pdfs.generar_ot(t, materiales if materiales else None)
            st.download_button("📄 Descargar OT en PDF", data=pdf_bytes,
                file_name=f"OT-{t['id']:04d}.pdf", mime="application/pdf",
                key=f"pdf_ot_{t['id']}")

    # ─── MATERIALES ────────────────────────────────────────────────────────────
    with tab_mat:
        st.markdown('<div class="section-title">Elementos / materiales utilizados</div>', unsafe_allow_html=True)
        materiales = db.obtener_materiales(t["id"])
        total = db.costo_total_materiales(t["id"])

        if materiales:
            header = st.columns([3, 1.5, 1.5, 1.5, 1])
            for h, txt in zip(header, ["Material", "Cantidad", "Unidad", "Costo", ""]):
                h.markdown(f'<span style="font-size:11px;color:#64748B;font-weight:600;text-transform:uppercase">{txt}</span>', unsafe_allow_html=True)
            for m in materiales:
                c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1.5, 1.5, 1])
                c1.write(m["nombre"])
                c2.write(f"{m['cantidad']:g}" if m["cantidad"] is not None else "—")
                c3.write(m["unidad"] or "—")
                c4.write(f"${m['costo']:,.0f}" if m["costo"] else "—")
                if c5.button("🗑", key=f"del_mat_{m['id']}"):
                    db.eliminar_material(m["id"])
                    st.rerun()
            st.markdown(f'<div style="text-align:right;font-weight:700;color:#1E3A5F;font-size:15px;margin-top:8px">Total materiales: ${total:,.0f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">Sin materiales registrados para este trabajo.</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown('<div class="section-title">Agregar elemento</div>', unsafe_allow_html=True)
        with st.form(f"form_mat_{t['id']}", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            nom_m   = c1.text_input("Nombre")
            cant    = c2.number_input("Cantidad", min_value=0.0, step=0.5)
            unidad  = c3.selectbox("Unidad", ["g","ml","unidad","kit","otro"])
            costo_m = c4.number_input("Costo ($)", min_value=0, step=500)
            if st.form_submit_button("Agregar"):
                if nom_m.strip():
                    db.agregar_material(t["id"], nom_m, cant, unidad, costo_m)
                    st.rerun()
                else:
                    st.error("El nombre no puede estar vacío.")

    # ─── EDITAR ────────────────────────────────────────────────────────────────
    with tab_edit:
        st.markdown(f'<div class="section-title">Modificar datos de la {ot}</div>', unsafe_allow_html=True)
        fecha_entrega_actual = None
        if t["fecha_entrega"]:
            try:
                fecha_entrega_actual = datetime.strptime(t["fecha_entrega"], "%Y-%m-%d").date()
            except ValueError:
                pass

        with st.form(f"form_editar_ot_{t['id']}", clear_on_submit=False):
            edit_nombre   = st.text_input("Nombre del trabajo", value=t["nombre"] or "")
            edit_paciente = st.text_input("Nombre del paciente", value=t["paciente"] or "")
            idx_tipo = db.TIPOS_TRABAJO.index(t["tipo_trabajo"]) if t["tipo_trabajo"] in db.TIPOS_TRABAJO else 0
            edit_tipo     = st.selectbox("Tipo de trabajo", db.TIPOS_TRABAJO, index=idx_tipo)
            edit_desc     = st.text_area("Descripción", value=t["descripcion"] or "", height=80)
            edit_fecha    = st.date_input("Fecha de entrega", value=fecha_entrega_actual)
            precio_actual = int(t["precio"]) if t["precio"] else 0
            edit_precio   = st.number_input("Precio ($)", min_value=0, step=1000, value=precio_actual)
            idx_estado    = db.ESTADOS.index(t["estado"]) if t["estado"] in db.ESTADOS else 0
            edit_estado   = st.selectbox("Estado", db.ESTADOS, index=idx_estado)
            edit_notas    = st.text_input("Notas internas", value=t["notas"] or "")

            if st.form_submit_button("💾 Guardar cambios"):
                db.actualizar_trabajo(
                    trabajo_id=t["id"], nombre=edit_nombre, paciente=edit_paciente,
                    tipo_trabajo=edit_tipo, descripcion=edit_desc,
                    fecha_entrega=edit_fecha, precio=edit_precio,
                    estado=edit_estado, notas=edit_notas,
                )
                st.success("¡Orden actualizada correctamente!")
                st.rerun()


# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=80)
    st.markdown("## Sincrodent")
    st.markdown("---")
    busqueda = st.text_input("🔍 Buscar OT o paciente",
        placeholder="OT-0003 o García", label_visibility="collapsed")
    st.markdown("---")
    idx_actual = NAV_OPCIONES.index(st.session_state.pagina) if st.session_state.pagina in NAV_OPCIONES else 0
    pagina_sidebar = st.radio("", NAV_OPCIONES, index=idx_actual, label_visibility="collapsed")
    if pagina_sidebar != st.session_state.pagina:
        st.session_state.pagina = pagina_sidebar
        st.session_state.detalle_id = None
        st.rerun()

pagina = st.session_state.pagina

# ── NAV MÓVIL — siempre visible, funciona en celular sin sidebar ───────────────
st.markdown('<div class="nav-movil">', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="nav-movil-widget">', unsafe_allow_html=True)
pagina_movil = st.selectbox("", NAV_OPCIONES,
    index=NAV_OPCIONES.index(pagina),
    label_visibility="collapsed",
    key="nav_movil_sel")
st.markdown('</div>', unsafe_allow_html=True)
if pagina_movil != pagina and not busqueda.strip() and st.session_state.detalle_id is None:
    st.session_state.pagina = pagina_movil
    st.rerun()

# ── ROUTING ────────────────────────────────────────────────────────────────────
if st.session_state.detalle_id is not None:
    vista_detalle(st.session_state.detalle_id)

elif busqueda.strip():
    st.markdown(f'<h1 style="color:#1E3A5F">Resultados para «{busqueda}»</h1>', unsafe_allow_html=True)
    resultados = db.buscar_trabajos(busqueda)
    if resultados:
        st.caption(f"{len(resultados)} orden(es) encontrada(s)")
        for t in resultados:
            fila_trabajo(t)
    else:
        st.markdown('<div class="empty-state">No se encontraron órdenes con ese criterio.</div>', unsafe_allow_html=True)

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
elif pagina == "📊 Dashboard":
    trabajos_activos = db.obtener_trabajos_activos()
    hoy_str = str(date.today())
    atrasados = [t for t in trabajos_activos if es_atrasado(t)]

    # Header
    st.markdown(f'<h1 style="color:#1E3A5F;margin-bottom:4px">Dashboard</h1>'
                f'<p style="color:#64748B;font-size:13px;margin-bottom:1.5rem">{date.today().strftime("%A %d de %B de %Y").capitalize()}</p>',
                unsafe_allow_html=True)

    # Alerta de atraso
    if atrasados:
        n = len(atrasados)
        detalles = "".join([
            f'<div style="margin-top:6px;font-size:13px">• <b>{db.numero_ot(a["id"])}</b> — {a["nombre"] or a["tipo_trabajo"]} '
            f'{"· " + a["paciente"] if a["paciente"] else ""} <span style="color:#B91C1C">Venció: {a["fecha_entrega"]}</span></div>'
            for a in atrasados
        ])
        st.markdown(
            f'<div class="alerta-critica">'
            f'<div class="titulo">⚠ {n} trabajo{"s" if n > 1 else ""} con entrega vencida</div>'
            f'{detalles}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Métricas
    resumen = db.resumen_general()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Órdenes activas",          resumen["activos"])
    col2.metric("Listas para entregar",     resumen["listos_para_entregar"])
    col3.metric("Deuda (entregados)",       f"${resumen['deuda_total']:,.0f}")
    col4.metric("Cobrado este mes",         f"${resumen['cobrado_este_mes']:,.0f}")

    # Deudas
    st.markdown('<div class="section-title">Dentistas con deuda</div>', unsafe_allow_html=True)
    deudas = db.deuda_por_cliente()
    if deudas:
        for row in deudas:
            st.markdown(
                f'<div class="deuda-card">'
                f'<span class="deuda-nombre">🦷 {row["nombre"]}</span>'
                f'<span class="deuda-monto">${row["deuda"]:,.0f}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div style="color:#16A34A;font-size:13px;padding:8px 0">✓ Sin deudas pendientes</div>', unsafe_allow_html=True)

    # Órdenes activas
    st.markdown('<div class="section-title">Órdenes activas</div>', unsafe_allow_html=True)
    if not trabajos_activos:
        st.markdown('<div class="empty-state">No hay órdenes activas en este momento.</div>', unsafe_allow_html=True)
    else:
        for t in trabajos_activos:
            fila_trabajo(t)

# ── NUEVA ORDEN ────────────────────────────────────────────────────────────────
elif pagina == "➕ Nueva orden":
    st.markdown('<h1 style="color:#1E3A5F">Nueva orden de trabajo</h1>', unsafe_allow_html=True)
    clientes = db.obtener_clientes()

    if not clientes:
        st.warning("Primero agrega un cliente en 👥 Clientes.")
    else:
        opciones = {c["nombre"]: c["id"] for c in clientes}
        with st.form("form_nueva_orden", clear_on_submit=True):
            cliente_nombre = st.selectbox("Dentista / Cliente", list(opciones.keys()))
            col_a, col_b  = st.columns(2)
            nombre_trabajo = col_a.text_input("Nombre del trabajo", placeholder="Corona Sra. González")
            paciente       = col_b.text_input("Nombre del paciente")
            tipo           = st.selectbox("Tipo de trabajo", db.TIPOS_TRABAJO)
            descripcion    = st.text_area("Descripción (diente, color, material, instrucciones)", height=80)
            col1, col2    = st.columns(2)
            fecha_ingreso  = col1.date_input("Fecha de ingreso", value=date.today())
            fecha_entrega  = col2.date_input("Fecha de entrega prometida", value=None)
            precio         = st.number_input("Precio ($)", min_value=0, step=1000, value=0)
            notas          = st.text_input("Notas internas (opcional)")
            foto_archivo   = st.file_uploader("Foto del trabajo (opcional)", type=["jpg","jpeg","png"])
            enviado        = st.form_submit_button("💾 Guardar orden")

        if enviado:
            tid = db.agregar_trabajo(
                cliente_id=opciones[cliente_nombre], nombre=nombre_trabajo,
                paciente=paciente, tipo=tipo, descripcion=descripcion,
                fecha_ingreso=fecha_ingreso, fecha_entrega=fecha_entrega,
                precio=precio if precio > 0 else None, notas=notas,
            )
            if foto_archivo:
                ext = foto_archivo.name.rsplit(".", 1)[-1].lower()
                db.guardar_foto(tid, foto_archivo.read(), ext)
            st.success(f"Orden **{db.numero_ot(tid)}** para **{cliente_nombre}** guardada correctamente.")

# ── CLIENTES ───────────────────────────────────────────────────────────────────
elif pagina == "👥 Clientes":
    st.markdown('<h1 style="color:#1E3A5F">Clientes / Dentistas</h1>', unsafe_allow_html=True)

    with st.expander("➕ Agregar nuevo cliente"):
        with st.form("form_cliente", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            nombre   = col_a.text_input("Nombre del dentista o clínica")
            telefono = col_b.text_input("Teléfono (opcional)")
            notas    = st.text_input("Notas (opcional)")
            if st.form_submit_button("Guardar cliente"):
                if nombre.strip():
                    token = db.agregar_cliente(nombre, telefono, notas)
                    st.success(f"Cliente **{nombre}** agregado.")
                    st.info(f"Link del portal: `{PORTAL_BASE}/?token={token}`")
                    st.rerun()
                else:
                    st.error("El nombre no puede estar vacío.")

    st.markdown('<div class="section-title">Clientes registrados</div>', unsafe_allow_html=True)
    for c in db.obtener_clientes():
        with st.expander(f"🦷 {c['nombre']}" + (f"  ·  {c['telefono']}" if c["telefono"] else "")):
            if c["notas"]:
                st.caption(c["notas"])
            link = f"{PORTAL_BASE}/?token={c['token']}"
            st.markdown("**Link del portal:**")
            st.code(link, language=None)
            st.caption("Mándale este link al dentista. Solo esta clínica puede usarlo.")

# ── HISTORIAL ──────────────────────────────────────────────────────────────────
elif pagina == "📋 Historial":
    st.markdown('<h1 style="color:#1E3A5F">Historial de órdenes</h1>', unsafe_allow_html=True)

    clientes      = db.obtener_clientes()
    col_f1, col_f2 = st.columns(2)
    filtro        = col_f1.selectbox("Cliente", ["Todos"] + [c["nombre"] for c in clientes])
    filtro_estado = col_f2.multiselect("Estado", db.ESTADOS, default=db.ESTADOS)

    trabajos = db.obtener_todos_trabajos()
    if filtro != "Todos":
        trabajos = [t for t in trabajos if t["cliente_nombre"] == filtro]
    if filtro_estado:
        trabajos = [t for t in trabajos if t["estado"] in filtro_estado]

    if not trabajos:
        st.markdown('<div class="empty-state">No hay órdenes con esos filtros.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"{len(trabajos)} orden(es)")
        for t in trabajos:
            fila_trabajo(t)

# ── COBROS ─────────────────────────────────────────────────────────────────────
elif pagina == "💰 Cobros":
    st.markdown('<h1 style="color:#1E3A5F">Órdenes de cobro mensual</h1>', unsafe_allow_html=True)
    st.caption("Genera un PDF por dentista con todos los trabajos entregados en el mes.")

    clientes = db.obtener_clientes()
    if not clientes:
        st.info("No hay clientes registrados.")
    else:
        col1, col2, col3 = st.columns(3)
        hoy = date.today()
        cliente_sel = col1.selectbox("Dentista", [c["nombre"] for c in clientes])
        mes_sel     = col2.selectbox("Mes", list(range(1,13)),
                        index=hoy.month-1, format_func=lambda m: MESES_ES[m])
        anio_sel    = col3.number_input("Año", min_value=2020, max_value=2030,
                        value=hoy.year, step=1)

        cliente_obj  = next(c for c in clientes if c["nombre"] == cliente_sel)
        trabajos_mes = db.trabajos_por_cliente_mes(cliente_obj["id"], anio_sel, mes_sel)

        st.divider()

        if not trabajos_mes:
            st.markdown(f'<div class="empty-state">No hay trabajos entregados de <b>{cliente_sel}</b> en {MESES_ES[mes_sel]} {anio_sel}.</div>', unsafe_allow_html=True)
        else:
            total     = sum(t["precio"] or 0 for t in trabajos_mes)
            pendiente = sum(t["precio"] or 0 for t in trabajos_mes if t["estado"] == "entregado")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Trabajos",       len(trabajos_mes))
            col_b.metric("Total período",  f"${total:,.0f}")
            col_c.metric("Saldo pendiente",f"${pendiente:,.0f}")

            st.markdown('<div class="section-title">Detalle</div>', unsafe_allow_html=True)
            for t in trabajos_mes:
                badge = BADGE_ESTADO.get(t["estado"], "")
                precio_str = f"${t['precio']:,.0f}" if t["precio"] else "—"
                st.markdown(
                    f'<div class="ot-row">'
                    f'<span class="ot-num">{db.numero_ot(t["id"])}</span>'
                    f'<span class="ot-nombre">{t["nombre"] or t["tipo_trabajo"]}</span>'
                    f'<span class="ot-meta">{t["paciente"] or "—"}</span>'
                    f'<span style="margin-left:auto;display:flex;gap:8px;align-items:center">'
                    f'<b style="color:#1E3A5F">{precio_str}</b>{badge}'
                    f'</span></div>',
                    unsafe_allow_html=True,
                )

            st.divider()
            mes_label = f"{MESES_ES[mes_sel]} {anio_sel}"
            pdf_bytes = pdfs.generar_cobro(cliente_sel, trabajos_mes, mes_label)
            st.download_button(
                f"📄 Descargar cobro — {cliente_sel} — {mes_label}",
                data=pdf_bytes,
                file_name=f"cobro_{cliente_sel.replace(' ','_')}_{anio_sel}_{mes_sel:02d}.pdf",
                mime="application/pdf",
            )