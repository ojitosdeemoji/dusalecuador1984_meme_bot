# Política de Aislamiento y Uso de Fuentes en X (Twitter)

Este documento define las directrices técnicas y éticas para el módulo de extracción de material visual desde X/Twitter dentro del proyecto **meme-bot**.

## 1. Principio de Aislamiento Estricto
- Se utiliza una cuenta dedicada exclusivamente a lectura técnica, completamente desacoplada de cualquier identidad o cuenta personal.
- La cuenta de servicio nunca emitirá publicaciones, comentarios, likes, reposts ni mensajes directos en la plataforma X.
- En caso de revocación de sesión, bloqueo por IP o desafío de seguridad (*checkpoint*) en X, el proyecto no intentará técnicas de evasión agresivas ni granjas de CAPTCHAs.

## 2. Restricción de Alcance (Allowlist)
- El bot no realizará búsquedas abiertas o masivas de usuarios no identificados.
- Las consultas se restringirán únicamente a una lista blanca (*allowlist*) de cuentas explícitamente autorizadas por la dirección artística del proyecto (cuentas de dominio público, archivos históricos o autores con autorización).

## 3. Estrategia de Fallback Obligatorio
- La disponibilidad de X se considera inherently inestable cuando se consulta desde infraestructura de CI/CD (GitHub Actions).
- Si la conexión con X arroja un error 403, 429 (rate limit), caída de sesión o contenido no disponible, el sistema activará automáticamente el catálogo local de reserva (`data/images/`).
- La continuidad de la obra artística nunca dependerá de la disponibilidad de un servicio de terceros.
