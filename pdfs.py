# pdfs.py — Generación de PDFs optimizados para ahorro de tinta (Printer-Friendly).
import io
import os
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

# ── Paleta de colores "Printer-Friendly" (Ahorro de tinta) ──────────────────────
AZUL_TEXTO  = colors.HexColor("#022C54") # Navy oficial de marca Sincrodent
TEAL_MARCA  = colors.HexColor("#009097") # Teal oficial de marca Sincrodent
GRIS_TEXTO  = colors.HexColor("#475569") # Texto secundario
LINEA_GRIS  = colors.HexColor("#CBD5E1") # Líneas y bordes finos
GRIS_TABLA  = colors.HexColor("#F8FAFC") # Fondo ultra claro para encabezados de tabla
BLANCO      = colors.white

def _get_nombre_lab():
    from config import cargar
    nombre = cargar()["NOMBRE_LAB"]
    return nombre if nombre else "Laboratorio Dental"

def _get_logo_path():
    from config import cargar
    p = cargar()["LOGO_PATH"]
    return os.path.join(os.path.dirname(__file__), p)

def _get_logo_app_path():
    from config import cargar
    p = cargar()["LOGO_APP_PATH"]
    return os.path.join(os.path.dirname(__file__), p)

# ── Estilos reutilizables ──────────────────────────────────────────────────────
estilos = getSampleStyleSheet()

titulo_lab = ParagraphStyle(
    "titulo_lab", fontSize=18, textColor=AZUL_TEXTO,
    fontName="Helvetica-Bold", alignment=TA_LEFT, leading=22,
)
subtitulo_lab = ParagraphStyle(
    "subtitulo_lab", fontSize=10, textColor=GRIS_TEXTO,
    fontName="Helvetica", alignment=TA_LEFT,
)
ot_numero = ParagraphStyle(
    "ot_numero", fontSize=24, textColor=AZUL_TEXTO,
    fontName="Helvetica-Bold", alignment=TA_RIGHT, leading=28,
)
label = ParagraphStyle(
    "label", fontSize=8, textColor=GRIS_TEXTO,
    fontName="Helvetica-Bold", spaceAfter=1,
)
valor = ParagraphStyle(
    "valor", fontSize=10, textColor=colors.black,
    fontName="Helvetica", spaceAfter=6,
)
seccion = ParagraphStyle(
    "seccion", fontSize=10, textColor=AZUL_TEXTO,
    fontName="Helvetica-Bold", alignment=TA_LEFT,
)
normal = ParagraphStyle(
    "normal", fontSize=9, textColor=colors.black,
    fontName="Helvetica", leading=13,
)
pie = ParagraphStyle(
    "pie", fontSize=8, textColor=GRIS_TEXTO,
    fontName="Helvetica", alignment=TA_CENTER,
)
pie_izq = ParagraphStyle(
    "pie_izq", fontSize=8, textColor=GRIS_TEXTO,
    fontName="Helvetica", alignment=TA_LEFT,
)


def _obtener_componente_logo():
    """Retorna un objeto Image si el logo existe, o un Spacer si no se encuentra."""
    if os.path.exists(_get_logo_path()):
        return Image(_get_logo_path(), height=1.3 * cm, width=1.3 * cm, kind='proportional')
    return Spacer(1, 1)


def _obtener_isotipo_sincrodent(alto=0.5 * cm):
    """Retorna el isotipo Sincrodent.png si existe, o None."""
    ruta = _get_logo_app_path()
    if os.path.exists(ruta):
        return Image(ruta, height=alto, width=alto, kind='proportional')
    return None


def _pie_pagina(anonimizar):
    """Pie de página con el isotipo de Sincrodent + texto de trazabilidad."""
    pie_txt = f"Documento generado con Sincrodent el {date.today().strftime('%d/%m/%Y')} · {_get_nombre_lab()}"
    if anonimizar:
        pie_txt += " · Identidad del paciente protegida (Ley 20.584)"
    isotipo = _obtener_isotipo_sincrodent(alto=0.42 * cm)
    if isotipo is not None:
        tabla = Table([[isotipo, Paragraph(pie_txt, pie_izq)]], colWidths=[0.7 * cm, 16.8 * cm])
        tabla.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return tabla
    return Paragraph(pie_txt, pie)


def _encabezado_lab(numero_ot):
    """Encabezado limpio sin bloques sólidos de color."""
    logo = _obtener_componente_logo()
    
    textos_header = [
        [Paragraph(_get_nombre_lab(), titulo_lab)],
        [Paragraph("Orden de Trabajo", subtitulo_lab)]
    ]
    tabla_textos = Table(textos_header, colWidths=[8 * cm])
    tabla_textos.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    col_izq = Table([[logo, tabla_textos]], colWidths=[1.6 * cm, 8.4 * cm])
    col_izq.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    col_der = [Paragraph(numero_ot, ot_numero)]
    isotipo = _obtener_isotipo_sincrodent(alto=0.6 * cm)
    if isotipo is not None:
        col_der = [isotipo, Spacer(1, 3), Paragraph(numero_ot, ot_numero)]

    tabla = Table(
        [[col_izq, col_der]],
        colWidths=[10 * cm, 7.5 * cm],
    )
    # Reemplazamos el fondo azul sólido por una caja limpia con borde inferior fino
    tabla.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, -1), 1.5, AZUL_TEXTO),
        ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
    ]))
    return tabla


def _fila_datos(pares):
    """Construye una tabla de dos columnas con pares (label, valor)."""
    filas = []
    for lbl, val in pares:
        filas.append([
            Paragraph(lbl, label),
            Paragraph(str(val) if val else "—", valor),
        ])
    tabla = Table(filas, colWidths=[4 * cm, 13.5 * cm])
    tabla.setStyle(TableStyle([
        ("VALIGN",       (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 2),
    ]))
    return tabla


def _titulo_seccion(texto):
    """Título con fondo blanco y una línea inferior fina (Ahorro de tinta)."""
    tabla = Table(
        [[Paragraph(texto.upper(), seccion)]],
        colWidths=[17.5 * cm],
    )
    tabla.setStyle(TableStyle([
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
        ("LINEBELOW",    (0, 0), (-1, -1), 1, LINEA_GRIS),
    ]))
    return tabla


# ── FUNCIÓN PRINCIPAL: OT ─────────────────────────────────────────────────────

def generar_ot(trabajo, materiales=None, anonimizar=False):
    """Genera el PDF de la Orden de Trabajo.

    Si anonimizar=True (entidad pública sujeta a Ley 20.584 y sesión sin
    privilegios de administrador), el nombre del paciente se reemplaza por
    sus iniciales en el documento.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    ot_str = f"OT-{trabajo['id']:04d}"
    es_conf = trabajo["notas"] and trabajo["notas"].startswith("[confidencial]")
    cliente_pdf = "Confidencial" if es_conf else trabajo["cliente_nombre"]
    notas_pdf = trabajo["notas"].replace("[confidencial] ", "").replace("[confidencial]", "").strip() if trabajo["notas"] else None

    if anonimizar:
        from config import anonimizar_nombre
        paciente_pdf = anonimizar_nombre(trabajo["paciente"])
    else:
        paciente_pdf = trabajo["paciente"]

    historia = []

    # ── Encabezado ──
    historia.append(_encabezado_lab(ot_str))
    historia.append(Spacer(1, 0.5 * cm))

    # ── Datos del trabajo ──
    historia.append(_titulo_seccion("Datos del trabajo"))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(_fila_datos([
        ("CLIENTE",          cliente_pdf),
        ("PACIENTE",         paciente_pdf),
        ("TIPO",             trabajo["tipo_trabajo"]),
        ("NOMBRE TRABAJO",   trabajo["nombre"]),
        ("DESCRIPCIÓN",      trabajo["descripcion"]),
        ("FECHA INGRESO",    trabajo["fecha_ingreso"]),
        ("FECHA ENTREGA",    trabajo["fecha_entrega"]),
        ("PRECIO",           f"${trabajo['precio']:,.0f}" if trabajo["precio"] else None),
        ("ESTADO",           trabajo["estado"].upper()),
        ("NOTAS",            notas_pdf),
    ]))
    historia.append(Spacer(1, 0.4 * cm))

    # ── Materiales ──
    if materiales:
        historia.append(_titulo_seccion("Elementos / materiales utilizados"))
        historia.append(Spacer(1, 0.2 * cm))

        filas_mat = [["Material", "Cantidad", "Unidad", "Costo"]]
        total_mat = 0
        for m in materiales:
            costo = m["costo"] or 0
            total_mat += costo
            filas_mat.append([
                m["nombre"],
                f"{m['cantidad']:g}" if m["cantidad"] is not None else "—",
                m["unidad"] or "—",
                f"${costo:,.0f}" if costo else "—",
            ])
        filas_mat.append(["", "", "TOTAL MATERIALES", f"${total_mat:,.0f}"])

        tabla_mat = Table(filas_mat, colWidths=[7 * cm, 3 * cm, 4 * cm, 3.5 * cm])
        tabla_mat.setStyle(TableStyle([
            ("BACKGROUND",   (0, 0), (-1, 0), GRIS_TABLA),
            ("TEXTCOLOR",    (0, 0), (-1, 0), AZUL_TEXTO),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("FONTNAME",     (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN",        (1, 0), (-1, -1), "CENTER"),
            ("ALIGN",        (-1, 0), (-1, -1), "RIGHT"),
            ("ALIGN",        (-1, -1), (-1, -1), "RIGHT"),
            ("GRID",         (0, 0), (-1, -1), 0.5, LINEA_GRIS),
            ("TOPPADDING",   (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
            ("LEFTPADDING",  (0, 0), (-1, -1), 6),
        ]))
        historia.append(tabla_mat)
        historia.append(Spacer(1, 0.5 * cm))

    # ── Firma de recepción ──
    historia.append(_titulo_seccion("Recepción del trabajo"))
    historia.append(Spacer(1, 0.3 * cm))

    firma = Table(
        [[
            [Paragraph("Firma:", label), Spacer(1, 1.2 * cm),
             HRFlowable(width=5.5 * cm, color=colors.black, thickness=0.5)],
            [Paragraph("Fecha recepción:", label), Spacer(1, 1.2 * cm),
             HRFlowable(width=5.5 * cm, color=colors.black, thickness=0.5)],
            [Paragraph("RUT / Nombre:", label), Spacer(1, 1.2 * cm),
             HRFlowable(width=5.5 * cm, color=colors.black, thickness=0.5)],
        ]],
        colWidths=[5.83 * cm, 5.83 * cm, 5.84 * cm],
    )
    firma.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "BOTTOM"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    historia.append(firma)

    # ── Pie de página ──
    historia.append(Spacer(1, 0.5 * cm))
    historia.append(HRFlowable(width="100%", color=LINEA_GRIS, thickness=0.5))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(_pie_pagina(anonimizar))

    doc.build(historia)
    buffer.seek(0)
    return buffer.read()


# ── FUNCIÓN PRINCIPAL: ORDEN DE COBRO ─────────────────────────────────────────

def generar_cobro(cliente_nombre, trabajos, mes_label, anonimizar=False):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    historia = []

    # ── Encabezado ──
    logo = _obtener_componente_logo()
    
    textos_header = [
        [Paragraph(_get_nombre_lab(), titulo_lab)],
        [Paragraph("Orden de Cobro", subtitulo_lab)]
    ]
    tabla_textos = Table(textos_header, colWidths=[8 * cm])
    tabla_textos.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    col_izq = Table([[logo, tabla_textos]], colWidths=[1.6 * cm, 8.4 * cm])
    col_izq.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    col_der_cobro = [Paragraph(mes_label, ot_numero)]
    isotipo_cobro = _obtener_isotipo_sincrodent(alto=0.6 * cm)
    if isotipo_cobro is not None:
        col_der_cobro = [isotipo_cobro, Spacer(1, 3), Paragraph(mes_label, ot_numero)]

    encab = Table(
        [[col_izq, col_der_cobro]],
        colWidths=[10 * cm, 7.5 * cm],
    )
    encab.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW",     (0, 0), (-1, -1), 1.5, AZUL_TEXTO),
        ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
    ]))
    historia.append(encab)
    historia.append(Spacer(1, 0.5 * cm))

    # ── Datos del cliente ──
    historia.append(_titulo_seccion("Cliente"))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(_fila_datos([
        ("DENTISTA / CLÍNICA", cliente_nombre),
        ("PERÍODO",            mes_label),
        ("FECHA EMISIÓN",      date.today().strftime("%d/%m/%Y")),
    ]))
    historia.append(Spacer(1, 0.4 * cm))

    # ── Detalle de trabajos ──
    historia.append(_titulo_seccion("Detalle de trabajos"))
    historia.append(Spacer(1, 0.2 * cm))

    filas = [["OT", "Paciente", "Trabajo", "Entrega", "Estado", "Precio"]]
    total = 0
    cobrado = 0
    pendiente = 0

    for t in trabajos:
        precio = t["precio"] or 0
        total += precio
        if t["estado"] == "cobrado":
            cobrado += precio
        else:
            pendiente += precio

        paciente_fila = t["paciente"] or "—"
        if anonimizar and t["paciente"]:
            from config import anonimizar_nombre
            paciente_fila = anonimizar_nombre(t["paciente"])

        filas.append([
            f"OT-{t['id']:04d}",
            paciente_fila,
            t["nombre"] or t["tipo_trabajo"],
            t["fecha_entrega"] or "—",
            t["estado"].upper(),
            f"${precio:,.0f}" if precio else "—",
        ])

    tabla_trab = Table(
        filas,
        colWidths=[2 * cm, 3 * cm, 4.5 * cm, 2.5 * cm, 2.5 * cm, 3 * cm],
    )
    tabla_trab.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0), GRIS_TABLA),
        ("TEXTCOLOR",      (0, 0), (-1, 0), AZUL_TEXTO),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",          (2, 1), (2, -1), "LEFT"),
        ("ALIGN",          (1, 1), (1, -1), "LEFT"),
        ("GRID",           (0, 0), (-1, -1), 0.5, LINEA_GRIS),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 5),
    ]))
    historia.append(tabla_trab)
    historia.append(Spacer(1, 0.4 * cm))

    # ── Resumen de totales ──
    historia.append(_titulo_seccion("Resumen"))
    historia.append(Spacer(1, 0.2 * cm))

    resumen = Table(
        [
            ["Total período:",    f"${total:,.0f}"],
            ["Ya cobrado:",       f"${cobrado:,.0f}"],
            ["SALDO PENDIENTE:",  f"${pendiente:,.0f}"],
        ],
        colWidths=[13 * cm, 4.5 * cm],
    )
    resumen.setStyle(TableStyle([
        ("FONTNAME",       (0, 0), (-1, -2), "Helvetica"),
        ("FONTNAME",       (0, -1), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 10),
        ("FONTSIZE",       (0, -1), (-1, -1), 12),
        ("TEXTCOLOR",      (0, -1), (-1, -1), AZUL_TEXTO),
        ("ALIGN",          (1, 0), (1, -1), "RIGHT"),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (0, -1), 0),
        ("LINEABOVE",      (0, -1), (-1, -1), 1, AZUL_TEXTO),
    ]))
    historia.append(resumen)
    historia.append(Spacer(1, 0.6 * cm))

    # ── Datos de pago ──
    historia.append(_titulo_seccion("Datos de pago"))
    historia.append(Spacer(1, 0.2 * cm))
    from config import cargar
    _cfg = cargar()
    banco_str = (
        f"Transferencia bancaria"
        f" · Banco: {_cfg['BANCO']}"
        f" · {_cfg['TIPO_CUENTA']}: {_cfg['NUMERO_CUENTA']}"
        f" · RUT: {_cfg['RUT_LAB']}"
        f" · Titular: {_cfg['NOMBRE_TITULAR']}"
    )
    historia.append(Paragraph(banco_str, normal))
    historia.append(Spacer(1, 0.8 * cm))

    # ── Pie ──
    historia.append(HRFlowable(width="100%", color=LINEA_GRIS, thickness=0.5))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(_pie_pagina(anonimizar))

    doc.build(historia)
    buffer.seek(0)
    return buffer.read()
