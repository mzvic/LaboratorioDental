import streamlit as st
from datetime import date, datetime
import os
import database as db
import pdfs

st.set_page_config(
    page_title="Sincrodent — Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

db.inicializar_db()

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

/* Ocultar sidebar y branding Streamlit */
section[data-testid="stSidebar"] { display: none !important; }
[data-testid="stSidebarCollapsedControl"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
header { visibility: hidden; }

/* Contenido principal sin margen de sidebar */
.main .block-container { max-width: 1100px; padding-top: 1rem; }

/* ── BARRA DE NAV SUPERIOR ── */
.topnav {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #1E3A5F;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 20px;
}
.topnav-logo { font-size: 18px; font-weight: 700; color: white; white-space: nowrap; }
.topnav-search { flex: 1; }

/* Selectbox dentro de topnav */
.topnav [data-testid="stTextInput"] input {
    background: rgba(255,255,255,.12) !important;
    border: 1px solid rgba(255,255,255,.25) !important;
    color: white !important;
    border-radius: 8px !important;
    font-size: 13px !important;
}
.topnav [data-testid="stTextInput"] input::placeholder { color: rgba(255,255,255,.5) !important; }

/* Métricas */
[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
}
[data-testid="stMetricLabel"] {
    font-size: 11px !important;
    color: #94A3B8 !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: .05em;
}
[data-testid="stMetricValue"] {
    font-size: 26px !important;
    font-weight: 700 !important;
    color: #1E3A5F !important;
    letter-spacing: -.02em;
}

/* Botones */
.stButton > button {
    background: #1E3A5F !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: .4rem 1rem !important;
    transition: background .15s !important;
}
.stButton > button:hover { background: #2D5080 !important; }
.stButton > button[kind="secondary"] {
    background: white !important;
    color: #1E3A5F !important;
    border: 1px solid #CBD5E1 !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background: white !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    color: #1A1A2E !important;
    font-size: 14px !important;
}
[data-testid="stExpander"] { border: none !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: #F1F5F9;
    border-radius: 10px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px;
    font-size: 13px;
    font-weight: 500;
    color: #64748B;
    padding: 6px 16px;
    background: transparent;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #1E3A5F !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.08) !important;
}
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* Inputs */
.stTextInput input, .stTextArea textarea {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #1E3A5F !important;
    box-shadow: 0 0 0 3px rgba(30,58,95,.08) !important;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .03em;
}
.badge-pendiente  { background: #EFF6FF; color: #2563EB; }
.badge-en_proceso { background: #FFFBEB; color: #B45309; }
.badge-listo      { background: #F0FDF4; color: #16A34A; }
.badge-entregado  { background: #FFF7ED; color: #EA580C; }
.badge-cobrado    { background: #F0FDF4; color: #15803D; }
.badge-atrasado   { background: #FEF2F2; color: #DC2626; }

/* Alertas */
.alerta-critica {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-left: 4px solid #EF4444;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 16px;
}
.alerta-critica .titulo { color: #991B1B; font-weight: 700; font-size: 14px; margin-bottom: 6px; }
.alerta-critica .item   { color: #B91C1C; font-size: 13px; padding: 3px 0; }

/* Card deuda */
.deuda-card {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 10px;
    padding: 11px 16px;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.deuda-nombre { color: #78350F; font-weight: 500; font-size: 13px; }
.deuda-monto  { color: #92400E; font-weight: 700; font-size: 15px; }

/* Sección label */
.section-label {
    font-size: 11px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: .07em;
    margin: 1.5rem 0 .75rem;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 2rem;
    color: #CBD5E1;
    font-size: 14px;
    background: #F8FAFC;
    border-radius: 10px;
    border: 1px dashed #E2E8F0;
}

/* Info box en detalle */
.info-box {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 14px;
}
.info-label { font-size: 11px; font-weight: 600; color: #94A3B8; text-transform: uppercase; letter-spacing: .05em; margin-bottom: 3px; }
.info-value { font-size: 14px; font-weight: 500; color: #1A1A2E; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTES ─────────────────────────────────────────────────────────────────
BADGE_ESTADO = {
    "pendiente":  '<span class="badge badge-pendiente">Pendiente</span>',
    "en_proceso": '<span class="badge badge-en_proceso">En proceso</span>',
    "listo":      '<span class="badge badge-listo">Listo ✓</span>',
    "entregado":  '<span class="badge badge-entregado">Entregado</span>',
    "cobrado":    '<span class="badge badge-cobrado">Cobrado ✓</span>',
}
EMOJI_ESTADO = {
    "pendiente": "🔵", "en_proceso": "🟡",
    "listo": "🟢", "entregado": "🟠", "cobrado": "✅",
}
MESES_ES = ["","Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]
MESES_FULL = ["enero","febrero","marzo","abril","mayo","junio",
              "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_ES = ["lunes","martes","miércoles","jueves","viernes","sábado","domingo"]
PORTAL_BASE = "http://portal.odontomax.mzvic.xyz"
NAV_OPCIONES = ["📊 Dashboard","➕ Nueva orden","👥 Clientes","📋 Historial","💰 Cobros"]

if "detalle_id" not in st.session_state:
    st.session_state.detalle_id = None
if "pagina" not in st.session_state:
    st.session_state.pagina = "📊 Dashboard"


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
            badge_a = ' <span class="badge badge-atrasado">⚠ Atrasado</span>' if es_atrasado(t) else ""
            st.markdown(f'{badge}{badge_a}', unsafe_allow_html=True)
            if t["fecha_entrega"]:
                st.caption(f"Entrega: {t['fecha_entrega']}")
            if t["precio"]:
                st.caption(f"Precio: ${t['precio']:,.0f}")
        with col_btn:
            if st.button("Abrir", key=f"abrir_{t['id']}"):
                st.session_state.detalle_id = t["id"]
                st.rerun()


# ── BARRA SUPERIOR ─────────────────────────────────────────────────────────────
st.markdown('<div class="topnav">', unsafe_allow_html=True)
col_logo, col_nav, col_search = st.columns([2, 4, 3])

with col_logo:
    if os.path.exists("logo.jpeg"):
        st.image("logo.jpeg", width=44)

with col_nav:
    idx = NAV_OPCIONES.index(st.session_state.pagina) if st.session_state.pagina in NAV_OPCIONES else 0
    nav_sel = st.selectbox("nav", NAV_OPCIONES, index=idx,
        label_visibility="collapsed", key="nav_top")
    if nav_sel != st.session_state.pagina:
        st.session_state.pagina = nav_sel
        st.session_state.detalle_id = None
        st.rerun()

with col_search:
    busqueda = st.text_input("buscar", placeholder="🔍  Buscar OT o paciente...",
        label_visibility="collapsed", key="busqueda_top")

st.markdown('</div>', unsafe_allow_html=True)

pagina = st.session_state.pagina


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
        f'<h1 style="color:#1E3A5F;font-size:24px;font-weight:700;margin-bottom:6px">{ot} — {nombre_mostrar}</h1>'
        f'<div style="margin-bottom:1.25rem">{badge}{atraso}</div>',
        unsafe_allow_html=True,
    )

    tab_info, tab_mat, tab_edit = st.tabs(["📋 Información", "📦 Elementos utilizados", "✏️ Editar Orden"])

    with tab_info:
        st.markdown(
            f'<div class="info-box"><div style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">'
            f'<div><div class="info-label">Cliente</div><div class="info-value">{t["cliente_nombre"]}</div></div>'
            f'<div><div class="info-label">Paciente</div><div class="info-value">{t["paciente"] or "—"}</div></div>'
            f'<div><div class="info-label">Tipo</div><div class="info-value">{t["tipo_trabajo"]}</div></div>'
            f'<div><div class="info-label">Ingreso</div><div class="info-value">{t["fecha_ingreso"]}</div></div>'
            f'<div><div class="info-label">Entrega</div><div class="info-value">{t["fecha_entrega"] or "—"}</div></div>'
            f'<div><div class="info-label">Precio</div><div class="info-value">{"${:,.0f}".format(t["precio"]) if t["precio"] else "—"}</div></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
        if t["descripcion"]:
            st.markdown(
                f'<div class="info-box"><div class="info-label">Descripción</div>'
                f'<div class="info-value">{t["descripcion"]}</div></div>',
                unsafe_allow_html=True,
            )
        if t["notas"]:
            st.caption(f"📝 {t['notas']}")
        if t["foto_path"] and os.path.exists(t["foto_path"]):
            st.image(t["foto_path"], width=300)
        foto_nueva = st.file_uploader("Subir / reemplazar foto", type=["jpg","jpeg","png"], key=f"foto_{t['id']}")
        if foto_nueva:
            db.guardar_foto(t["id"], foto_nueva.read(), foto_nueva.name.rsplit(".",1)[-1].lower())
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
                st.markdown(f'<p style="font-weight:600;color:#15803D;margin-bottom:8px">Cobrar ${t["precio"]:,.0f}</p>', unsafe_allow_html=True)
                if st.button("✅ Marcar como cobrado", key=f"cobrar_{t['id']}"):
                    db.registrar_pago(t["id"], t["precio"], date.today())
                    st.success("Pago registrado.")
                    st.rerun()
        with col_pdf:
            mats = db.obtener_materiales(t["id"])
            pdf_bytes = pdfs.generar_ot(t, mats if mats else None)
            st.download_button("📄 Descargar OT PDF", data=pdf_bytes,
                file_name=f"OT-{t['id']:04d}.pdf", mime="application/pdf", key=f"pdf_{t['id']}")

    with tab_mat:
        mats = db.obtener_materiales(t["id"])
        total = db.costo_total_materiales(t["id"])
        if mats:
            cols_h = st.columns([3,1.5,1.5,1.5,.8])
            for c, txt in zip(cols_h, ["Material","Cantidad","Unidad","Costo",""]):
                c.markdown(f'<span style="font-size:11px;color:#94A3B8;font-weight:600;text-transform:uppercase">{txt}</span>', unsafe_allow_html=True)
            for m in mats:
                c1,c2,c3,c4,c5 = st.columns([3,1.5,1.5,1.5,.8])
                c1.write(m["nombre"])
                c2.write(f"{m['cantidad']:g}" if m["cantidad"] is not None else "—")
                c3.write(m["unidad"] or "—")
                c4.write(f"${m['costo']:,.0f}" if m["costo"] else "—")
                if c5.button("🗑", key=f"del_{m['id']}"): db.eliminar_material(m["id"]); st.rerun()
            st.markdown(f'<div style="text-align:right;font-weight:700;color:#1E3A5F;margin-top:8px">Total: ${total:,.0f}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="empty-state">Sin materiales registrados.</div>', unsafe_allow_html=True)
        st.divider()
        with st.form(f"form_mat_{t['id']}", clear_on_submit=True):
            c1,c2,c3,c4 = st.columns(4)
            nom = c1.text_input("Nombre"); cant = c2.number_input("Cantidad", min_value=0.0, step=0.5)
            uni = c3.selectbox("Unidad", ["g","ml","unidad","kit","otro"])
            cos = c4.number_input("Costo ($)", min_value=0, step=500)
            if st.form_submit_button("Agregar"):
                if nom.strip(): db.agregar_material(t["id"], nom, cant, uni, cos); st.rerun()
                else: st.error("El nombre no puede estar vacío.")

    with tab_edit:
        fecha_e = None
        if t["fecha_entrega"]:
            try: fecha_e = datetime.strptime(t["fecha_entrega"], "%Y-%m-%d").date()
            except ValueError: pass
        with st.form(f"form_editar_{t['id']}", clear_on_submit=False):
            c1,c2 = st.columns(2)
            en = c1.text_input("Nombre del trabajo", value=t["nombre"] or "")
            ep = c2.text_input("Paciente", value=t["paciente"] or "")
            idx_t = db.TIPOS_TRABAJO.index(t["tipo_trabajo"]) if t["tipo_trabajo"] in db.TIPOS_TRABAJO else 0
            et = st.selectbox("Tipo de trabajo", db.TIPOS_TRABAJO, index=idx_t)
            ed = st.text_area("Descripción", value=t["descripcion"] or "", height=80)
            c3,c4 = st.columns(2)
            ef = c3.date_input("Fecha de entrega", value=fecha_e)
            epr = c4.number_input("Precio ($)", min_value=0, step=1000, value=int(t["precio"]) if t["precio"] else 0)
            idx_s = db.ESTADOS.index(t["estado"]) if t["estado"] in db.ESTADOS else 0
            es_sel = st.selectbox("Estado", db.ESTADOS, index=idx_s)
            eno = st.text_input("Notas internas", value=t["notas"] or "")
            if st.form_submit_button("💾 Guardar cambios"):
                db.actualizar_trabajo(trabajo_id=t["id"], nombre=en, paciente=ep,
                    tipo_trabajo=et, descripcion=ed, fecha_entrega=ef,
                    precio=epr, estado=es_sel, notas=eno)
                st.success("Orden actualizada."); st.rerun()


# ── ROUTING ────────────────────────────────────────────────────────────────────
if st.session_state.detalle_id is not None:
    vista_detalle(st.session_state.detalle_id)

elif busqueda.strip():
    st.markdown(f'<h2 style="color:#1E3A5F;margin-bottom:.5rem">Resultados para «{busqueda}»</h2>', unsafe_allow_html=True)
    resultados = db.buscar_trabajos(busqueda)
    if resultados:
        st.caption(f"{len(resultados)} orden(es) encontrada(s)")
        for t in resultados: fila_trabajo(t)
    else:
        st.markdown('<div class="empty-state">No se encontraron órdenes.</div>', unsafe_allow_html=True)

elif pagina == "📊 Dashboard":
    hoy = date.today()
    trabajos_activos = db.obtener_trabajos_activos()
    atrasados = [t for t in trabajos_activos if es_atrasado(t)]
    resumen = db.resumen_general()
    deudas = db.deuda_por_cliente()

    st.markdown(
        f'<h1 style="color:#1E3A5F;font-size:24px;font-weight:700;margin-bottom:2px">Buenos días 👋</h1>'
        f'<p style="color:#94A3B8;font-size:13px;margin-bottom:1.25rem">'
        f'{DIAS_ES[hoy.weekday()].capitalize()} {hoy.day} de {MESES_FULL[hoy.month-1]} de {hoy.year}</p>',
        unsafe_allow_html=True,
    )

    if atrasados:
        n = len(atrasados)
        items = "".join([
            f'<div class="item">· <b>{db.numero_ot(a["id"])}</b> — {a["nombre"] or a["tipo_trabajo"]}'
            f'{" · " + a["paciente"] if a["paciente"] else ""}'
            f' <span style="opacity:.75">Venció {a["fecha_entrega"]}</span></div>'
            for a in atrasados
        ])
        st.markdown(
            f'<div class="alerta-critica"><div class="titulo">⚠ {n} trabajo{"s" if n>1 else ""} con entrega vencida</div>{items}</div>',
            unsafe_allow_html=True,
        )

    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Órdenes activas",     resumen["activos"])
    col2.metric("Listas para entregar",resumen["listos_para_entregar"])
    col3.metric("Deuda pendiente",     f"${resumen['deuda_total']:,.0f}")
    col4.metric("Cobrado este mes",    f"${resumen['cobrado_este_mes']:,.0f}")

    col_main, col_side = st.columns([3, 1])
    with col_main:
        st.markdown('<div class="section-label">Órdenes activas</div>', unsafe_allow_html=True)
        if not trabajos_activos:
            st.markdown('<div class="empty-state">✓ Sin órdenes activas.</div>', unsafe_allow_html=True)
        else:
            for t in trabajos_activos: fila_trabajo(t)
    with col_side:
        st.markdown('<div class="section-label">Dentistas con deuda</div>', unsafe_allow_html=True)
        if deudas:
            for row in deudas:
                st.markdown(
                    f'<div class="deuda-card">'
                    f'<span class="deuda-nombre">{row["nombre"]}</span>'
                    f'<span class="deuda-monto">${row["deuda"]:,.0f}</span>'
                    f'</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#16A34A;font-size:13px;padding:8px 12px;background:#F0FDF4;border-radius:8px;border:1px solid #BBF7D0">✓ Sin deudas</div>', unsafe_allow_html=True)

elif pagina == "➕ Nueva orden":
    st.markdown('<h2 style="color:#1E3A5F;margin-bottom:1rem">Nueva orden de trabajo</h2>', unsafe_allow_html=True)
    clientes = db.obtener_clientes()
    if not clientes:
        st.warning("Primero agrega un cliente en 👥 Clientes.")
    else:
        opciones = {c["nombre"]: c["id"] for c in clientes}
        with st.form("form_nueva_orden", clear_on_submit=True):
            c1,c2 = st.columns(2)
            cliente_nombre = c1.selectbox("Dentista / Cliente", list(opciones.keys()))
            nombre_trabajo = c2.text_input("Nombre del trabajo", placeholder="Corona Sra. González")
            c3,c4 = st.columns(2)
            paciente = c3.text_input("Nombre del paciente")
            tipo     = c4.selectbox("Tipo de trabajo", db.TIPOS_TRABAJO)
            descripcion = st.text_area("Descripción (color, pieza, material, instrucciones)", height=80)
            c5,c6 = st.columns(2)
            fecha_ingreso = c5.date_input("Fecha de ingreso", value=date.today())
            fecha_entrega = c6.date_input("Fecha de entrega prometida", value=None)
            c7,c8 = st.columns(2)
            precio = c7.number_input("Precio ($)", min_value=0, step=1000, value=0)
            notas  = c8.text_input("Notas internas (opcional)")
            foto   = st.file_uploader("Foto del trabajo (opcional)", type=["jpg","jpeg","png"])
            if st.form_submit_button("💾 Guardar orden"):
                tid = db.agregar_trabajo(
                    cliente_id=opciones[cliente_nombre], nombre=nombre_trabajo,
                    paciente=paciente, tipo=tipo, descripcion=descripcion,
                    fecha_ingreso=fecha_ingreso, fecha_entrega=fecha_entrega,
                    precio=precio if precio > 0 else None, notas=notas)
                if foto:
                    db.guardar_foto(tid, foto.read(), foto.name.rsplit(".",1)[-1].lower())
                st.success(f"Orden **{db.numero_ot(tid)}** guardada correctamente.")

elif pagina == "👥 Clientes":
    st.markdown('<h2 style="color:#1E3A5F;margin-bottom:1rem">Clientes / Dentistas</h2>', unsafe_allow_html=True)
    with st.expander("➕ Agregar nuevo cliente"):
        with st.form("form_cliente", clear_on_submit=True):
            c1,c2 = st.columns(2)
            nombre   = c1.text_input("Nombre del dentista o clínica")
            telefono = c2.text_input("Teléfono (opcional)")
            notas    = st.text_input("Notas (opcional)")
            if st.form_submit_button("Guardar cliente"):
                if nombre.strip():
                    token = db.agregar_cliente(nombre, telefono, notas)
                    st.success(f"Cliente **{nombre}** agregado.")
                    st.info(f"Link del portal: `{PORTAL_BASE}/?token={token}`")
                    st.rerun()
                else: st.error("El nombre no puede estar vacío.")
    st.markdown('<div class="section-label">Clientes registrados</div>', unsafe_allow_html=True)
    for c in db.obtener_clientes():
        with st.expander(f"🦷  {c['nombre']}" + (f"  ·  {c['telefono']}" if c["telefono"] else "")):
            if c["notas"]: st.caption(c["notas"])
            st.markdown("**Link del portal:**")
            st.code(f"{PORTAL_BASE}/?token={c['token']}", language=None)
            st.caption("Mándale este link. Solo esta clínica puede usarlo.")

elif pagina == "📋 Historial":
    st.markdown('<h2 style="color:#1E3A5F;margin-bottom:1rem">Historial de órdenes</h2>', unsafe_allow_html=True)
    clientes = db.obtener_clientes()
    c1,c2 = st.columns(2)
    filtro        = c1.selectbox("Cliente", ["Todos"] + [c["nombre"] for c in clientes])
    filtro_estado = c2.multiselect("Estado", db.ESTADOS, default=db.ESTADOS)
    trabajos = db.obtener_todos_trabajos()
    if filtro != "Todos": trabajos = [t for t in trabajos if t["cliente_nombre"] == filtro]
    if filtro_estado:     trabajos = [t for t in trabajos if t["estado"] in filtro_estado]
    if not trabajos:
        st.markdown('<div class="empty-state">Sin órdenes con esos filtros.</div>', unsafe_allow_html=True)
    else:
        st.caption(f"{len(trabajos)} orden(es)")
        for t in trabajos: fila_trabajo(t)

elif pagina == "💰 Cobros":
    st.markdown('<h2 style="color:#1E3A5F;margin-bottom:1rem">Órdenes de cobro mensual</h2>', unsafe_allow_html=True)
    clientes = db.obtener_clientes()
    if not clientes:
        st.info("No hay clientes registrados.")
    else:
        hoy = date.today()
        c1,c2,c3 = st.columns(3)
        cliente_sel = c1.selectbox("Dentista", [c["nombre"] for c in clientes])
        mes_sel     = c2.selectbox("Mes", list(range(1,13)), index=hoy.month-1, format_func=lambda m: MESES_ES[m])
        anio_sel    = c3.number_input("Año", min_value=2020, max_value=2030, value=hoy.year, step=1)
        cliente_obj  = next(c for c in clientes if c["nombre"] == cliente_sel)
        trabajos_mes = db.trabajos_por_cliente_mes(cliente_obj["id"], anio_sel, mes_sel)
        st.divider()
        if not trabajos_mes:
            st.markdown(f'<div class="empty-state">Sin trabajos de <b>{cliente_sel}</b> en {MESES_ES[mes_sel]} {anio_sel}.</div>', unsafe_allow_html=True)
        else:
            total     = sum(t["precio"] or 0 for t in trabajos_mes)
            pendiente = sum(t["precio"] or 0 for t in trabajos_mes if t["estado"] == "entregado")
            ca,cb,cc = st.columns(3)
            ca.metric("Trabajos", len(trabajos_mes))
            cb.metric("Total período", f"${total:,.0f}")
            cc.metric("Saldo pendiente", f"${pendiente:,.0f}")
            st.markdown('<div class="section-label">Detalle</div>', unsafe_allow_html=True)
            for t in trabajos_mes:
                badge = BADGE_ESTADO.get(t["estado"],"")
                precio_s = f'<b style="color:#1E3A5F">${t["precio"]:,.0f}</b>' if t["precio"] else "—"
                st.markdown(
                    f'<div style="background:white;border:1px solid #E2E8F0;border-radius:8px;padding:10px 14px;'
                    f'margin-bottom:6px;display:flex;align-items:center;gap:12px">'
                    f'<span style="font-weight:700;color:#1E3A5F;font-size:13px;min-width:72px">{db.numero_ot(t["id"])}</span>'
                    f'<span style="font-size:13px;flex:1">{t["nombre"] or t["tipo_trabajo"]}</span>'
                    f'<span style="color:#94A3B8;font-size:12px">{t["paciente"] or "—"}</span>'
                    f'<span style="margin-left:auto;display:flex;gap:8px;align-items:center">{precio_s}{badge}</span>'
                    f'</div>', unsafe_allow_html=True)
            st.divider()
            mes_label = f"{MESES_ES[mes_sel]} {anio_sel}"
            pdf_bytes = pdfs.generar_cobro(cliente_sel, trabajos_mes, mes_label)
            st.download_button(f"📄 Descargar cobro — {cliente_sel} — {mes_label}",
                data=pdf_bytes,
                file_name=f"cobro_{cliente_sel.replace(' ','_')}_{anio_sel}_{mes_sel:02d}.pdf",
                mime="application/pdf")

