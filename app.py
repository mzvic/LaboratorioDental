import streamlit as st
from datetime import date
import calendar
import os
import database as db
import pdfs

st.set_page_config(
    page_title="Laboratorio Dental",
    page_icon="🦷",
    layout="wide",
)

db.inicializar_db()

COLORES_ESTADO = {
    "pendiente":  "🔵",
    "en_proceso": "🟡",
    "listo":      "🟢",
    "entregado":  "🟠",
    "cobrado":    "✅",
}

MESES_ES = [
    "", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

if "detalle_id" not in st.session_state:
    st.session_state.detalle_id = None


def titulo_trabajo(t):
    ot    = db.numero_ot(t["id"])
    emoji = COLORES_ESTADO.get(t["estado"], "⚪")
    nombre = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
    pac   = f" · 👤 {t['paciente']}" if t["paciente"] else ""
    tard  = ""
    if (t["fecha_entrega"]
            and t["fecha_entrega"] < str(date.today())
            and t["estado"] not in ("entregado", "cobrado")):
        tard = " ⚠️"
    return f"{emoji} {ot} — {nombre} ({t['cliente_nombre']}){pac}{tard}"


def fila_trabajo(t):
    col_btn, col_info = st.columns([1, 6])
    with col_btn:
        if st.button("Abrir", key=f"abrir_{t['id']}"):
            st.session_state.detalle_id = t["id"]
            st.rerun()
    with col_info:
        st.write(titulo_trabajo(t))


def vista_detalle(trabajo_id):
    t = db.obtener_trabajo(trabajo_id)
    if not t:
        st.error("Esa orden ya no existe.")
        st.session_state.detalle_id = None
        return

    if st.button("← Volver"):
        st.session_state.detalle_id = None
        st.rerun()

    ot = db.numero_ot(t["id"])
    nombre_mostrar = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
    st.title(f"{ot} — {nombre_mostrar}")

    tab_info, tab_mat = st.tabs(["📋 Información", "📦 Elementos utilizados"])

    # ─── TAB INFORMACIÓN ───────────────────────────────────────────────────────
    with tab_info:
        col1, col2, col3, col4 = st.columns(4)
        col1.write(f"**Cliente:** {t['cliente_nombre']}")
        col2.write(f"**Paciente:** {t['paciente'] or '—'}")
        col3.write(f"**Tipo:** {t['tipo_trabajo']}")
        col4.write(f"**Precio:** ${t['precio']:,.0f}" if t["precio"] else "**Precio:** —")

        col5, col6 = st.columns(2)
        col5.write(f"**Ingreso:** {t['fecha_ingreso']}")
        col6.write(f"**Entrega:** {t['fecha_entrega'] or '—'}")

        if t["descripcion"]:
            st.write(f"**Descripción:** {t['descripcion']}")
        if t["notas"]:
            st.caption(f"Notas: {t['notas']}")

        if t["foto_path"] and os.path.exists(t["foto_path"]):
            st.image(t["foto_path"], caption="Foto del trabajo", width=320)

        foto_nueva = st.file_uploader(
            "Subir / reemplazar foto", type=["jpg", "jpeg", "png"],
            key=f"foto_{t['id']}"
        )
        if foto_nueva:
            ext = foto_nueva.name.rsplit(".", 1)[-1].lower()
            db.guardar_foto(t["id"], foto_nueva.read(), ext)
            st.success("Foto guardada.")
            st.rerun()

        st.divider()

        col_estado, col_cobro, col_pdf = st.columns(3)

        with col_estado:
            nuevo_estado = st.selectbox(
                "Estado", db.ESTADOS,
                index=db.ESTADOS.index(t["estado"]),
                key=f"estado_{t['id']}",
            )
            if nuevo_estado != t["estado"]:
                if st.button("Actualizar estado", key=f"btn_estado_{t['id']}"):
                    db.actualizar_estado(t["id"], nuevo_estado)
                    st.rerun()

        with col_cobro:
            if t["estado"] == "entregado" and t["precio"]:
                st.write(f"**Cobrar ${t['precio']:,.0f}**")
                if st.button("✅ Marcar como cobrado", key=f"cobrar_{t['id']}"):
                    db.registrar_pago(t["id"], t["precio"], date.today())
                    st.success("Pago registrado.")
                    st.rerun()

        with col_pdf:
            st.write("**Imprimir OT**")
            materiales = db.obtener_materiales(t["id"])
            pdf_bytes = pdfs.generar_ot(t, materiales if materiales else None)
            st.download_button(
                label="📄 Descargar OT en PDF",
                data=pdf_bytes,
                file_name=f"OT-{t['id']:04d}.pdf",
                mime="application/pdf",
                key=f"pdf_ot_{t['id']}",
            )

    # ─── TAB MATERIALES ────────────────────────────────────────────────────────
    with tab_mat:
        st.subheader("Elementos / materiales utilizados")
        materiales = db.obtener_materiales(t["id"])
        total = db.costo_total_materiales(t["id"])

        if materiales:
            for m in materiales:
                c1, c2, c3, c4, c5 = st.columns([3, 1.5, 1.5, 1.5, 1])
                c1.write(m["nombre"])
                c2.write(f"{m['cantidad']:g}" if m["cantidad"] is not None else "—")
                c3.write(m["unidad"] or "—")
                c4.write(f"${m['costo']:,.0f}" if m["costo"] else "—")
                if c5.button("🗑️", key=f"del_mat_{m['id']}"):
                    db.eliminar_material(m["id"])
                    st.rerun()
            st.markdown(f"**Costo total en materiales: ${total:,.0f}**")
        else:
            st.info("Aún no se ha registrado ningún material.")

        st.divider()
        st.write("**Agregar elemento**")
        with st.form(f"form_mat_{t['id']}", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            nom_m   = c1.text_input("Nombre (ej: Resina, Yeso)")
            cant    = c2.number_input("Cantidad", min_value=0.0, step=0.5)
            unidad  = c3.selectbox("Unidad", ["g", "ml", "unidad", "kit", "otro"])
            costo_m = c4.number_input("Costo ($)", min_value=0, step=500)
            if st.form_submit_button("Agregar"):
                if nom_m.strip():
                    db.agregar_material(t["id"], nom_m, cant, unidad, costo_m)
                    st.rerun()
                else:
                    st.error("El nombre no puede estar vacío.")


# ── NAVEGACIÓN ─────────────────────────────────────────────────────────────────

st.sidebar.title("🦷 Lab. Dental")
st.sidebar.markdown("---")
st.sidebar.markdown("**Buscar orden**")
busqueda = st.sidebar.text_input(
    "Número OT o nombre de paciente",
    placeholder="OT-0003 o García",
    label_visibility="collapsed",
)
pagina = st.sidebar.radio(
    "Ir a",
    ["📊 Dashboard", "➕ Nueva orden", "👥 Clientes", "📋 Historial", "💰 Cobros"],
)

# ── DETALLE (prioridad sobre todo) ─────────────────────────────────────────────
if st.session_state.detalle_id is not None:
    vista_detalle(st.session_state.detalle_id)

# ── BÚSQUEDA ───────────────────────────────────────────────────────────────────
elif busqueda.strip():
    st.title(f"Resultados para «{busqueda}»")
    resultados = db.buscar_trabajos(busqueda)
    if resultados:
        st.write(f"**{len(resultados)} orden(es) encontrada(s)**")
        for t in resultados:
            fila_trabajo(t)
    else:
        st.info("No se encontraron órdenes.")

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
elif pagina == "📊 Dashboard":
    st.title("Dashboard")
    resumen = db.resumen_general()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Órdenes activas",          resumen["activos"])
    col2.metric("Listas para entregar",     resumen["listos_para_entregar"])
    col3.metric("Deuda total (entregados)", f"${resumen['deuda_total']:,.0f}")
    col4.metric("Cobrado este mes",         f"${resumen['cobrado_este_mes']:,.0f}")

    st.divider()
    deudas = db.deuda_por_cliente()
    if deudas:
        st.subheader("⚠️ Dentistas con deuda")
        for row in deudas:
            st.warning(f"**{row['nombre']}** — debe **${row['deuda']:,.0f}**")
    else:
        st.success("Sin deudas pendientes.")

    st.divider()
    st.subheader("Órdenes activas")
    trabajos = db.obtener_trabajos_activos()
    if not trabajos:
        st.info("No hay órdenes activas.")
    else:
        for t in trabajos:
            fila_trabajo(t)

# ── NUEVA ORDEN ────────────────────────────────────────────────────────────────
elif pagina == "➕ Nueva orden":
    st.title("Nueva orden de trabajo")
    clientes = db.obtener_clientes()

    if not clientes:
        st.warning("Primero agrega un cliente en 👥 Clientes.")
    else:
        opciones = {c["nombre"]: c["id"] for c in clientes}

        with st.form("form_nueva_orden", clear_on_submit=True):
            cliente_nombre = st.selectbox("Dentista / Cliente", list(opciones.keys()))
            nombre_trabajo = st.text_input("Nombre del trabajo (ej: Corona Sra. González)")
            paciente       = st.text_input("Nombre del paciente")
            tipo           = st.selectbox("Tipo de trabajo", db.TIPOS_TRABAJO)
            descripcion    = st.text_area("Descripción (diente, materiales, instrucciones)", height=80)
            col1, col2     = st.columns(2)
            fecha_ingreso  = col1.date_input("Fecha de ingreso", value=date.today())
            fecha_entrega  = col2.date_input("Fecha de entrega prometida", value=None)
            precio         = st.number_input("Precio ($)", min_value=0, step=1000, value=0)
            notas          = st.text_input("Notas internas (opcional)")
            foto_archivo   = st.file_uploader("Foto del trabajo (opcional)", type=["jpg", "jpeg", "png"])
            enviado        = st.form_submit_button("Guardar orden")

        if enviado:
            tid = db.agregar_trabajo(
                cliente_id    = opciones[cliente_nombre],
                nombre        = nombre_trabajo,
                paciente      = paciente,
                tipo          = tipo,
                descripcion   = descripcion,
                fecha_ingreso = fecha_ingreso,
                fecha_entrega = fecha_entrega,
                precio        = precio if precio > 0 else None,
                notas         = notas,
            )
            if foto_archivo:
                ext = foto_archivo.name.rsplit(".", 1)[-1].lower()
                db.guardar_foto(tid, foto_archivo.read(), ext)
            st.success(f"Orden **{db.numero_ot(tid)}** para **{cliente_nombre}** guardada.")

# ── CLIENTES ───────────────────────────────────────────────────────────────────
elif pagina == "👥 Clientes":
    st.title("Clientes / Dentistas")

    # URL base del portal — local por ahora, reemplazar con dominio Cloudflare al hacer deploy
    PORTAL_BASE = "http://localhost:8502"

    with st.expander("➕ Agregar nuevo cliente"):
        with st.form("form_cliente", clear_on_submit=True):
            nombre   = st.text_input("Nombre del dentista o clínica")
            telefono = st.text_input("Teléfono (opcional)")
            notas    = st.text_input("Notas (opcional)")
            if st.form_submit_button("Guardar cliente"):
                if nombre.strip():
                    token = db.agregar_cliente(nombre, telefono, notas)
                    st.success(f"Cliente **{nombre}** agregado.")
                    st.info(f"Link del portal: `{PORTAL_BASE}/?token={token}`")
                    st.rerun()
                else:
                    st.error("El nombre no puede estar vacío.")

    st.divider()
    for c in db.obtener_clientes():
        with st.expander(f"**{c['nombre']}**" + (f" — {c['telefono']}" if c["telefono"] else "")):
            if c["notas"]:
                st.caption(c["notas"])

            link = f"{PORTAL_BASE}/?token={c['token']}"
            st.markdown("**Link del portal para esta clínica:**")
            st.code(link, language=None)
            st.caption("Mándale este link por WhatsApp. Solo esta clínica puede usarlo.")

# ── HISTORIAL ──────────────────────────────────────────────────────────────────
elif pagina == "📋 Historial":
    st.title("Historial de órdenes")

    clientes      = db.obtener_clientes()
    filtro        = st.selectbox("Filtrar por cliente", ["Todos"] + [c["nombre"] for c in clientes])
    filtro_estado = st.multiselect("Filtrar por estado", db.ESTADOS, default=db.ESTADOS)

    trabajos = db.obtener_todos_trabajos()
    if filtro != "Todos":
        trabajos = [t for t in trabajos if t["cliente_nombre"] == filtro]
    if filtro_estado:
        trabajos = [t for t in trabajos if t["estado"] in filtro_estado]

    if not trabajos:
        st.info("No hay órdenes con esos filtros.")
    else:
        st.write(f"**{len(trabajos)} orden(es)**")
        for t in trabajos:
            fila_trabajo(t)

# ── COBROS ─────────────────────────────────────────────────────────────────────
elif pagina == "💰 Cobros":
    st.title("Órdenes de cobro mensual")
    st.write("Genera un PDF por dentista con todos los trabajos entregados en el mes.")

    clientes = db.obtener_clientes()
    if not clientes:
        st.info("No hay clientes registrados.")
    else:
        col1, col2, col3 = st.columns(3)
        hoy = date.today()

        cliente_sel = col1.selectbox(
            "Dentista",
            [c["nombre"] for c in clientes],
        )
        mes_sel = col2.selectbox(
            "Mes",
            list(range(1, 13)),
            index=hoy.month - 1,
            format_func=lambda m: MESES_ES[m],
        )
        anio_sel = col3.number_input(
            "Año", min_value=2020, max_value=2030,
            value=hoy.year, step=1,
        )

        cliente_obj = next(c for c in clientes if c["nombre"] == cliente_sel)
        trabajos_mes = db.trabajos_por_cliente_mes(cliente_obj["id"], anio_sel, mes_sel)

        st.divider()

        if not trabajos_mes:
            st.info(f"No hay trabajos entregados de **{cliente_sel}** en {MESES_ES[mes_sel]} {anio_sel}.")
        else:
            total = sum(t["precio"] or 0 for t in trabajos_mes)
            pendiente = sum(t["precio"] or 0 for t in trabajos_mes if t["estado"] == "entregado")

            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Trabajos", len(trabajos_mes))
            col_b.metric("Total período", f"${total:,.0f}")
            col_c.metric("Saldo pendiente", f"${pendiente:,.0f}")

            st.write(f"**{len(trabajos_mes)} trabajo(s) de {cliente_sel} en {MESES_ES[mes_sel]} {anio_sel}:**")
            for t in trabajos_mes:
                emoji = COLORES_ESTADO.get(t["estado"], "⚪")
                precio_str = f"${t['precio']:,.0f}" if t["precio"] else "—"
                st.write(f"{emoji} {db.numero_ot(t['id'])} — {t['nombre'] or t['tipo_trabajo']} · {t['paciente'] or '—'} · {precio_str}")

            st.divider()
            mes_label = f"{MESES_ES[mes_sel]} {anio_sel}"
            pdf_bytes = pdfs.generar_cobro(cliente_sel, trabajos_mes, mes_label)
            st.download_button(
                label=f"📄 Descargar orden de cobro — {cliente_sel} — {mes_label}",
                data=pdf_bytes,
                file_name=f"cobro_{cliente_sel.replace(' ', '_')}_{anio_sel}_{mes_sel:02d}.pdf",
                mime="application/pdf",
            )
