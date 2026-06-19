import streamlit as st
from datetime import date
import os
import database as db

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

if "detalle_id" not in st.session_state:
    st.session_state.detalle_id = None


def titulo_trabajo(t):
    """Texto corto para listas: OT, nombre custom (o tipo), paciente, estado."""
    ot = db.numero_ot(t["id"])
    emoji = COLORES_ESTADO.get(t["estado"], "⚪")
    nombre = t["nombre"] if t["nombre"] else t["tipo_trabajo"]
    paciente_label = f" · 👤 {t['paciente']}" if t["paciente"] else ""
    vencido = ""
    if (t["fecha_entrega"]
            and t["fecha_entrega"] < str(date.today())
            and t["estado"] not in ("entregado", "cobrado")):
        vencido = " ⚠️"
    return f"{emoji} {ot} — {nombre} ({t['cliente_nombre']}){paciente_label}{vencido}"


def fila_trabajo(t):
    """Fila clickeable en una lista: botón que abre el detalle."""
    col_btn, col_info = st.columns([1, 5])
    with col_btn:
        if st.button("Abrir", key=f"abrir_{t['id']}"):
            st.session_state.detalle_id = t["id"]
            st.rerun()
    with col_info:
        st.write(titulo_trabajo(t))


def vista_detalle(trabajo_id):
    """Página completa de un trabajo: info + materiales, en pestañas."""
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

    tab_info, tab_materiales = st.tabs(["📋 Información", "📦 Elementos utilizados"])

    # ───── TAB INFORMACIÓN ─────
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

        foto_nueva = st.file_uploader("Subir / reemplazar foto", type=["jpg", "jpeg", "png"], key=f"foto_{t['id']}")
        if foto_nueva:
            extension = foto_nueva.name.rsplit(".", 1)[-1].lower()
            db.guardar_foto(t["id"], foto_nueva.read(), extension)
            st.success("Foto guardada.")
            st.rerun()

        st.divider()

        col_estado, col_pago = st.columns(2)
        with col_estado:
            nuevo_estado = st.selectbox(
                "Estado",
                db.ESTADOS,
                index=db.ESTADOS.index(t["estado"]),
                key=f"estado_{t['id']}",
            )
            if nuevo_estado != t["estado"]:
                if st.button("Actualizar estado", key=f"btn_estado_{t['id']}"):
                    db.actualizar_estado(t["id"], nuevo_estado)
                    st.rerun()
        with col_pago:
            if t["estado"] == "entregado" and t["precio"]:
                st.write(f"**Cobrar ${t['precio']:,.0f}**")
                if st.button("✅ Marcar como cobrado", key=f"cobrar_{t['id']}"):
                    db.registrar_pago(t["id"], t["precio"], date.today())
                    st.success("Pago registrado.")
                    st.rerun()

    # ───── TAB MATERIALES ─────
    with tab_materiales:
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
            st.info("Aún no se ha registrado ningún material para este trabajo.")

        st.divider()
        st.write("**Agregar elemento**")
        with st.form(f"form_material_{t['id']}", clear_on_submit=True):
            c1, c2, c3, c4 = st.columns(4)
            nombre_mat = c1.text_input("Nombre (ej: Resina, Yeso, Metal)")
            cantidad   = c2.number_input("Cantidad", min_value=0.0, step=0.5)
            unidad     = c3.selectbox("Unidad", ["g", "ml", "unidad", "kit", "otro"])
            costo      = c4.number_input("Costo ($)", min_value=0, step=500)
            if st.form_submit_button("Agregar"):
                if nombre_mat.strip():
                    db.agregar_material(t["id"], nombre_mat, cantidad, unidad, costo)
                    st.success(f"{nombre_mat} agregado.")
                    st.rerun()
                else:
                    st.error("El nombre del material no puede estar vacío.")


# ──────────────────────────────────────────
# NAVEGACIÓN
# ──────────────────────────────────────────

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
    ["📊 Dashboard", "➕ Nueva orden", "👥 Clientes", "📋 Historial"],
)

# Si hay un detalle abierto, tiene prioridad sobre todo lo demás
if st.session_state.detalle_id is not None:
    vista_detalle(st.session_state.detalle_id)

elif busqueda.strip():
    st.title(f"Resultados para «{busqueda}»")
    resultados = db.buscar_trabajos(busqueda)
    if resultados:
        st.write(f"**{len(resultados)} orden(es) encontrada(s)**")
        for t in resultados:
            fila_trabajo(t)
    else:
        st.info("No se encontraron órdenes con ese criterio.")

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

elif pagina == "➕ Nueva orden":
    st.title("Nueva orden de trabajo")
    clientes = db.obtener_clientes()

    if not clientes:
        st.warning("Primero agrega un cliente en la sección 👥 Clientes.")
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
            trabajo_id = db.agregar_trabajo(
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
                extension = foto_archivo.name.rsplit(".", 1)[-1].lower()
                db.guardar_foto(trabajo_id, foto_archivo.read(), extension)

            ot = db.numero_ot(trabajo_id)
            st.success(f"Orden **{ot}** para **{cliente_nombre}** guardada correctamente.")

elif pagina == "👥 Clientes":
    st.title("Clientes / Dentistas")

    with st.expander("➕ Agregar nuevo cliente"):
        with st.form("form_cliente", clear_on_submit=True):
            nombre   = st.text_input("Nombre del dentista o clínica")
            telefono = st.text_input("Teléfono (opcional)")
            notas    = st.text_input("Notas (opcional)")
            if st.form_submit_button("Guardar cliente"):
                if nombre.strip():
                    db.agregar_cliente(nombre, telefono, notas)
                    st.success(f"Cliente **{nombre}** agregado.")
                    st.rerun()
                else:
                    st.error("El nombre no puede estar vacío.")

    st.divider()
    clientes = db.obtener_clientes()
    if not clientes:
        st.info("Aún no hay clientes registrados.")
    else:
        for c in clientes:
            st.write(f"**{c['nombre']}**" + (f" — {c['telefono']}" if c["telefono"] else ""))
            if c["notas"]:
                st.caption(c["notas"])

elif pagina == "📋 Historial":
    st.title("Historial de órdenes")

    clientes      = db.obtener_clientes()
    nombres       = ["Todos"] + [c["nombre"] for c in clientes]
    filtro        = st.selectbox("Filtrar por cliente", nombres)
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
