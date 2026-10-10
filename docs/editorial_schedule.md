# Programación Temporal y Ventanas Editoriales (3 Publicaciones Diarias)

Este documento describe la cadencia operativa de publicación automatizada del proyecto **meme-bot**.

## 1. Frecuencia y Horarios Base (UTC)
El bot está configurado en GitHub Actions con tres activaciones automáticas al día mediante la expresión cron:
`20 11,17,23 * * *`

- **Ventana 1 (Matutina):** 11:20 UTC (08:20 CLT / 07:20 EDT)
- **Ventana 2 (Tarde):** 17:20 UTC (14:20 CLT / 13:20 EDT)
- **Ventana 3 (Noche):** 23:20 UTC (20:20 CLT / 19:20 EDT)

## 2. Dispersión Temporal (Jitter Editorial)
Para simular un ritmo editorial orgánico y reducir la congestión en la infraestructura compartida de GitHub:
- En cada ejecución programada (`schedule`), el sistema introduce un retardo aleatorio de entre 0 y 15 minutos (0 a 900 segundos) antes de adquirir la imagen y procesar el meme.
- Las ejecuciones manuales (`workflow_dispatch`) omiten el retardo para permitir pruebas y ejecuciones inmediatas.

## 3. Comportamiento Operativo y Resiliencia
- En ejecución programada, el bot opera en **modo producción** (publicación activa en Bluesky y actualización atómica de `data/state.json`).
- Si la adquisición de imágenes en X/Twitter no devuelve resultados o experimenta caídas de conexión, conmuta automáticamente al catálogo de reserva local (`data/images/`).
- La concurrencia está restringida a una única ejecución simultánea para garantizar la integridad de las listas de exclusión de hashes.
