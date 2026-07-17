"""
pdfs.py — Generación de PDFs para el laboratorio dental con soporte para Logo.
  - generar_ot(trabajo, materiales)  → bytes del PDF de una OT
  - generar_cobro(cliente, trabajos) → bytes del PDF de orden de cobro mensual
"""

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

# ── Paleta de colores ──────────────────────────────────────────────────────────
AZUL       = colors.HexColor("#1E3A5F")
AZUL_CLARO = colors.HexColor("#E8EEF4")
GRIS       = colors.HexColor("#666666")
GRIS_CLARO = colors.HexColor("#F5F5F5")
VERDE      = colors.HexColor("#2E7D32")
BLANCO     = colors.white

NOMBRE_LAB = "Laboratorio Dental OdontoMax"   # ← cambia esto al nombre real
LOGO_PATH  = os.path.join(os.path.dirname(__file__), "logo.jpeg") # ← Ruta a tu logo local

# ── Estilos reutilizables ──────────────────────────────────────────────────────
estilos = getSampleStyleSheet()

titulo_lab = ParagraphStyle(
    "titulo_lab", fontSize=18, textColor=BLANCO,
    fontName="Helvetica-Bold", alignment=TA_LEFT, leading=22,
)
subtitulo_lab = ParagraphStyle(
    "subtitulo_lab", fontSize=10, textColor=AZUL_CLARO,
    fontName="Helvetica", alignment=TA_LEFT,
)
ot_numero = ParagraphStyle(
    "ot_numero", fontSize=26, textColor=AZUL,
    fontName="Helvetica-Bold", alignment=TA_RIGHT, leading=30,
)
label = ParagraphStyle(
    "label", fontSize=8, textColor=GRIS,
    fontName="Helvetica-Bold", spaceAfter=1,
)
valor = ParagraphStyle(
    "valor", fontSize=10, textColor=colors.black,
    fontName="Helvetica", spaceAfter=6,
)
seccion = ParagraphStyle(
    "seccion", fontSize=9, textColor=BLANCO,
    fontName="Helvetica-Bold", alignment=TA_LEFT,
)
normal = ParagraphStyle(
    "normal", fontSize=9, textColor=colors.black,
    fontName="Helvetica", leading=13,
)
pie = ParagraphStyle(
    "pie", fontSize=8, textColor=GRIS,
    fontName="Helvetica", alignment=TA_CENTER,
)


def _obtener_componente_logo():
    """Retorna un objeto Image si el logo existe, o un Spacer si no se encuentra."""
    if os.path.exists(LOGO_PATH):
        # Ajustamos el logo a un alto máximo de 1.2 cm manteniendo la proporción
        return Image(LOGO_PATH, height=1.2 * cm, width=1.2 * cm, kind='proportional')
    return Spacer(1, 1)


def _encabezado_lab(numero_ot):
    """Tabla de encabezado: logo + nombre laboratorio + número OT."""
    logo = _obtener_componente_logo()
    
    # Metemos el logo y los textos en una sub-tabla interna para alinearlos perfectamente
    textos_header = [
        [Paragraph(NOMBRE_LAB, titulo_lab)],
        [Paragraph("Orden de Trabajo", subtitulo_lab)]
    ]
    tabla_textos = Table(textos_header, colWidths=[8 * cm])
    tabla_textos.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    # Estructura de la columna izquierda: [Logo, Bloque de Texto]
    col_izq = Table([[logo, tabla_textos]], colWidths=[1.5 * cm, 8.5 * cm])
    col_izq.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    col_der = [
        Paragraph(numero_ot, ot_numero),
    ]
    
    tabla = Table(
        [[col_izq, col_der]],
        colWidths=[10 * cm, 7.5 * cm],
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (0, 0), 18),
        ("RIGHTPADDING", (1, 0), (1, 0), 18),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", (0, 0), (-1, -1), [6, 6, 6, 6]),
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
    tabla = Table(
        [[Paragraph(texto.upper(), seccion)]],
        colWidths=[17.5 * cm],
    )
    tabla.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
        ("TOPPADDING",   (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    return tabla


# ── FUNCIÓN PRINCIPAL: OT ─────────────────────────────────────────────────────

def generar_ot(trabajo, materiales=None):
    """
    Genera el PDF de una Orden de Trabajo.
    trabajo   : sqlite3.Row (de obtener_trabajo)
    materiales: lista de sqlite3.Row (de obtener_materiales), puede ser None
    Retorna   : bytes del PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    ot_str = f"OT-{trabajo['id']:04d}"
    historia = []

    # ── Encabezado ──
    historia.append(_encabezado_lab(ot_str))
    historia.append(Spacer(1, 0.5 * cm))

    # ── Datos del trabajo ──
    historia.append(_titulo_seccion("Datos del trabajo"))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(_fila_datos([
        ("CLIENTE",          trabajo["cliente_nombre"]),
        ("PACIENTE",         trabajo["paciente"]),
        ("TIPO",             trabajo["tipo_trabajo"]),
        ("NOMBRE TRABAJO",   trabajo["nombre"]),
        ("DESCRIPCIÓN",      trabajo["descripcion"]),
        ("FECHA INGRESO",    trabajo["fecha_ingreso"]),
        ("FECHA ENTREGA",    trabajo["fecha_entrega"]),
        ("PRECIO",           f"${trabajo['precio']:,.0f}" if trabajo["precio"] else None),
        ("ESTADO",           trabajo["estado"].upper()),
        ("NOTAS",            trabajo["notas"]),
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
            ("BACKGROUND",   (0, 0), (-1, 0), AZUL_CLARO),
            ("TEXTCOLOR",    (0, 0), (-1, 0), AZUL),
            ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",     (0, 0), (-1, -1), 9),
            ("FONTNAME",     (0, -1), (-1, -1), "Helvetica-Bold"),
            ("BACKGROUND",   (0, -1), (-1, -1), GRIS_CLARO),
            ("ALIGN",        (1, 0), (-1, -1), "CENTER"),
            ("ALIGN",        (-1, 0), (-1, -1), "RIGHT"),
            ("ALIGN",        (-1, -1), (-1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [BLANCO, GRIS_CLARO]),
            ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
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
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ]))
    historia.append(firma)

    # ── Pie de página ──
    historia.append(Spacer(1, 0.5 * cm))
    historia.append(HRFlowable(width="100%", color=GRIS, thickness=0.5))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(Paragraph(
        f"Documento generado el {date.today().strftime('%d/%m/%Y')} · {NOMBRE_LAB}",
        pie,
    ))

    doc.build(historia)
    buffer.seek(0)
    return buffer.read()


# ── FUNCIÓN PRINCIPAL: ORDEN DE COBRO ─────────────────────────────────────────

def generar_cobro(cliente_nombre, trabajos, mes_label):
    """
    Genera el PDF de orden de cobro mensual para un dentista.
    cliente_nombre : str
    trabajos       : lista de sqlite3.Row con estado = 'entregado' o 'cobrado'
    mes_label      : str, ej: "Junio 2026"
    Retorna        : bytes del PDF
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    historia = []

    # ── Encabezado con Logo ──
    logo = _obtener_componente_logo()
    
    textos_header = [
        [Paragraph(NOMBRE_LAB, titulo_lab)],
        [Paragraph("Orden de Cobro", subtitulo_lab)]
    ]
    tabla_textos = Table(textos_header, colWidths=[8 * cm])
    tabla_textos.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    col_izq = Table([[logo, tabla_textos]], colWidths=[1.5 * cm, 8.5 * cm])
    col_izq.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    encab = Table(
        [[col_izq, [Paragraph(mes_label, ot_numero)]]],
        colWidths=[10 * cm, 7.5 * cm],
    )
    encab.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), AZUL),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (0, 0), 18),
        ("RIGHTPADDING", (1, 0), (1, 0), 18),
        ("TOPPADDING",   (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 14),
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

        filas.append([
            f"OT-{t['id']:04d}",
            t["paciente"] or "—",
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
        ("BACKGROUND",     (0, 0), (-1, 0), AZUL_CLARO),
        ("TEXTCOLOR",      (0, 0), (-1, 0), AZUL),
        ("FONTNAME",       (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, -1), 8),
        ("ALIGN",          (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",          (2, 1), (2, -1), "LEFT"),
        ("ALIGN",          (1, 1), (1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ("GRID",           (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
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
        ("TEXTCOLOR",      (0, -1), (-1, -1), VERDE),
        ("ALIGN",          (1, 0), (1, -1), "RIGHT"),
        ("BACKGROUND",     (0, -1), (-1, -1), colors.HexColor("#E8F5E9")),
        ("TOPPADDING",     (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 6),
        ("LEFTPADDING",    (0, 0), (0, -1), 10),
        ("LINEABOVE",      (0, -1), (-1, -1), 1.5, VERDE),
    ]))
    historia.append(resumen)
    historia.append(Spacer(1, 0.6 * cm))

    # ── Datos de pago ──
    historia.append(_titulo_seccion("Datos de pago"))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(Paragraph(
        "Transferencia bancaria · Banco: _______________  · Cuenta: _______________  · RUT: _______________",
        normal,
    ))
    historia.append(Spacer(1, 0.8 * cm))

    # ── Pie ──
    historia.append(HRFlowable(width="100%", color=GRIS, thickness=0.5))
    historia.append(Spacer(1, 0.2 * cm))
    historia.append(Paragraph(
        f"Documento generado el {date.today().strftime('%d/%m/%Y')} · {NOMBRE_LAB}",
        pie,
    ))

    doc.build(historia)
    buffer.seek(0)
    return buffer.read()
