# Contexto: Software Laboratorio Dental

## El negocio
- Laboratorio dental familiar (papá). Lleva años funcionando "a medias", con deudas y flujo irregular.
- Ubicación: Concepción, Chile.
- Trabaja desde la casa (sin arriendo). Tiene 2+ personas trabajando.
- Factura entre $500k y $1.5M CLP/mes.
- Clientes: entre 5 y 15 dentistas/clínicas.
- Servicios principales: prótesis removibles y coronas/puentes fijos.
- Problemas principales: órdenes llegan por WhatsApp sin registro, no sabe cuánto le deben, no sabe el costo real de cada trabajo, flujo de caja irregular.

## El desarrollador
- Estudiante de 4to año Ingeniería Civil Electrónica.
- Manejo: Python (bueno), Excel (bueno), C (básico).
- Sin experiencia en Flask, HTML, JS, ni frameworks web.
- Stack elegido: **Python + Streamlit + SQLite + ReportLab**.

## Estado actual del software
Funcional y probado localmente. Archivos:

```
laboratorio/
├── app.py           ← Interfaz Streamlit (4 pantallas + búsqueda)
├── database.py      ← SQLite, todas las funciones CRUD
├── pdfs.py          ← Generación PDFs con ReportLab
├── requirements.txt ← streamlit, reportlab
├── README.md
├── data/
│   └── laboratorio.db   ← Base de datos SQLite
└── fotos/               ← Imágenes adjuntas a trabajos
```

### Funcionalidades implementadas
- **OT automática**: cada trabajo recibe número OT-0001, OT-0002, etc.
- **Búsqueda**: por número OT o nombre de paciente (sidebar permanente).
- **4 pantallas**: Dashboard, Nueva orden, Clientes, Historial.
- **Pestaña Cobros**: genera orden de cobro mensual por dentista en PDF.
- **Vista de detalle**: al hacer clic en "Abrir" en cualquier fila, abre página dedicada al trabajo con dos pestañas:
  - Información (datos, foto, cambiar estado, cobrar)
  - Elementos utilizados (materiales con cantidad, unidad y costo)
- **PDFs**: OT imprimible (con sección de firma) y orden de cobro mensual.
- **Estados**: pendiente → en_proceso → listo → entregado → cobrado.
- **Dashboard**: métricas (activas, listas, deuda total, cobrado este mes) + alertas de deuda por cliente.
- **Fotos**: se pueden subir al crear la orden o desde la vista de detalle.

### Tablas de la base de datos
```
clientes      : id, nombre, telefono, notas
trabajos      : id, cliente_id, nombre, paciente, tipo_trabajo, descripcion,
                fecha_ingreso, fecha_entrega, precio, estado, foto_path, notas
pagos         : id, trabajo_id, monto, fecha, notas
materiales    : id, trabajo_id, nombre, cantidad, unidad, costo, fecha
```

### Pendiente de implementar
1. **Portal para clínicas**: formulario web separado donde el dentista llena campos obligatorios (color, diente, tipo, etc.) y crea la orden directamente. Plan: segunda app Streamlit en otro puerto, o formulario HTML estático con Formspree.
2. **Deploy con Cloudflare Tunnel**: acceso móvil para el papá sin exponer puertos. Dominio propio (~$10 USD/año). Cloudflare Access (OTP por email) + geo-restriction a Chile. Cloudflared corre como servicio en Windows.
3. **Login simple en Streamlit**: pantalla de usuario/contraseña como capa extra de seguridad.

### Funcionalidades sugeridas para después
- Reporte mensual exportable (PDF/Excel)
- Alertas de trabajos atrasados más visibles
- Edición de una orden ya guardada
- Backup automático del .db
- Ranking de clientes por rentabilidad
- Proyección de flujo de caja

## Roadmap de negocio (carta Gantt)

### Etapa 1 — Jul a Sep 2026: Desarrollo y piloto
- Completar software (portal clínicas + deploy)
- Papá registra TODAS las OT en el sistema
- Documentar métricas: tiempo ahorrado, deuda cobrada, flujo

### Etapa 2 — Oct a Dic 2026: Demo a otros laboratorios
- Preparar pitch con caso real del papá
- Contactar 3–5 laboratorios de la zona
- Demos activas + onboarding
- Iniciar migración a arquitectura SaaS cloud (multi-tenant)

### Hito — Enero 2027: Institutos
- Presentar a CFT/INACAP que imparten Técnico en Laboratorio Dental
- Proponer convenio: licencia gratuita a cambio de integración curricular
- Modelo inspirado en MATLAB: estudiantes se fidelizan durante la carrera
- Meta: 1 instituto piloto para 2do semestre 2027

## Visión de negocio a largo plazo
- Producto SaaS para laboratorios dentales en Chile y Latinoamérica.
- Competidor local de Vevident (español, €18–60/mes).
- Precios estimados: Starter ~$10–15 USD/mes, Laboratorio ~$25–40 USD/mes.
- Ventaja competitiva: hecho en Chile, soporte local, en pesos, conocido desde la formación técnica.
- Migración técnica necesaria: SQLite → PostgreSQL, Streamlit → framework web real, autenticación por usuarios, Stripe para cobros.

## Cómo retomar en una nueva sesión
Pegar este archivo al inicio del chat y agregar la pregunta o el update específico.
Para mostrar errores o código nuevo: simplemente pegarlo en el chat.
