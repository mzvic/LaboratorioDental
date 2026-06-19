# Laboratorio Dental — Software de Órdenes

## Instalación (solo la primera vez)

1. Asegúrate de tener Python instalado.
   Para verificar, abre la terminal y escribe:
   ```
   python --version
   ```

2. Instala Streamlit:
   ```
   pip install streamlit
   ```

## Cómo correr el programa

1. Abre la terminal en la carpeta del proyecto.
2. Ejecuta:
   ```
   streamlit run app.py
   ```
3. Se abre automáticamente en el navegador.

## Estructura del proyecto

```
laboratorio/
├── app.py           ← Interfaz visual (pantallas)
├── database.py      ← Base de datos y consultas
├── requirements.txt ← Dependencias
├── README.md        ← Este archivo
└── data/
    └── laboratorio.db  ← Base de datos (se crea sola al iniciar)
```

## Backup

Para hacer una copia de seguridad, solo copia el archivo:
```
data/laboratorio.db
```
Ese archivo contiene TODOS los datos del sistema.

## Estados de una orden

| Estado      | Significado                          |
|-------------|--------------------------------------|
| pendiente   | Recién ingresada, sin comenzar       |
| en_proceso  | Se está fabricando                   |
| listo       | Terminado, esperando entrega         |
| entregado   | Entregado al dentista, sin cobrar    |
| cobrado     | Pagado ✅                            |
