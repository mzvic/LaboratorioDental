"""
portal.py — Portal exclusivo para clínicas/dentistas.
Corre en un puerto separado: streamlit run portal.py --server.port 8502
Cada clínica accede con su link único: http://localhost:8502/?token=XXX
"""

import streamlit as st
from datetime import date, timedelta
import database as db
import os
st.set_page_config(
    page_title="Enviar trabajo al laboratorio",
    page_icon="🦷",
    layout="centered",
)

db.inicializar_db()

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
LOGO_PATH = os.path.join(os.path.dirname(__file__), "logo.jpeg")

# ── Portal activo ──────────────────────────────────────────────────────────────
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=80)
else:
    st.image("https://via.placeholder.com/80x80.png?text=🦷", width=60)
# ── Portal activo ──────────────────────────────────────────────────────────────

st.title("Laboratorio Dental OdontoMax")
st.subheader(f"Portal de envío — {cliente['nombre']}")
st.caption("Complete el formulario para enviar una nueva orden de trabajo al laboratorio.")

st.divider()

# Campos obligatorios marcados con *
st.markdown("Los campos marcados con **\*** son obligatorios.")

with st.form("form_portal", clear_on_submit=True):

    # ── Datos del paciente ──
    st.markdown("#### Paciente")
    paciente = st.text_input("Nombre del paciente *")

    # ── Tipo de trabajo ──
    st.markdown("#### Trabajo solicitado")
    tipo = st.selectbox("Tipo de trabajo *", db.TIPOS_TRABAJO)
    nombre_trabajo = st.text_input("Descripción corta del trabajo *",
                                   placeholder="Ej: Corona pieza 14 Sra. Pérez")

    # ── Especificaciones técnicas ──
    st.markdown("#### Especificaciones técnicas")
    col1, col2 = st.columns(2)

    GUIA_VITA = [
        "A1", "A2", "A3", "A3.5", "A4",
        "B1", "B2", "B3", "B4",
        "C1", "C2", "C3", "C4",
        "D2", "D3", "D4",
        "Otro / No aplica",
    ]
    color = col1.selectbox("Color (guía VITA) *", GUIA_VITA)
    diente = col2.text_input("Número(s) de pieza(s) *",
                              placeholder="Ej: 14, 15-17")

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
        height=100,
    )

    # ── Fechas ──
    st.markdown("#### Fecha de entrega")
    fecha_minima = date.today() + timedelta(days=3)
    fecha_entrega = st.date_input(
        "Fecha de entrega solicitada *",
        value=fecha_minima,
        min_value=fecha_minima,
    )

    # ── Foto / archivo adjunto ──
    st.markdown("#### Fotografía (opcional)")
    foto = st.file_uploader(
        "Adjuntar foto del caso (impresión, foto clínica, etc.)",
        type=["jpg", "jpeg", "png"],
    )

    st.divider()
    enviado = st.form_submit_button("📤 Enviar orden al laboratorio", type="primary")

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
            precio        = None,   # el laboratorio define el precio
            notas         = f"Enviado por portal — {cliente['nombre']}",
        )

        if foto:
            ext = foto.name.rsplit(".", 1)[-1].lower()
            db.guardar_foto(trabajo_id, foto.read(), ext)

        ot = db.numero_ot(trabajo_id)

        st.success(f"✅ Orden enviada correctamente. Su número de OT es **{ot}**.")
        st.info(
            f"El laboratorio revisará su solicitud y se pondrá en contacto "
            f"para confirmar la fecha de entrega del **{fecha_entrega.strftime('%d/%m/%Y')}**."
        )
        st.balloons()
