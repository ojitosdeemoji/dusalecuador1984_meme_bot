# Manual de Operaciones Autónomas y Mantenimiento (Runbook)

Este documento contiene los procedimientos operativos para la administración a largo plazo del bot de memes de cadáver exquisito (**meme-bot**).

---

## 1. Arquitectura y Cadencia Autónoma

El bot opera de forma 100% desatendida mediante GitHub Actions:

- **Publicaciones en Bluesky (3 veces al día):**
  - Horarios UTC: `11:20`, `17:20` y `23:20`.
  - Dispersión (*jitter*): Retardo aleatorio de 0 a 15 minutos en cada ventana para naturalidad orgánica.
- **Sincronización de Métricas y Scoring:**
  - Horario UTC: `05:00` (una vez al día).
  - Consulta pasiva vía AT Protocol (`likes`, `reposts`, `replies`, `quotes`) y cálculo de `score` atenuado.
- **Centinela de Salud (Health Check):**
  - Horario UTC: Domingos a las `00:00`.
  - Audita el nivel de insumos restantes y detecta anomalías.

---

## 2. Procedimientos de Mantenimiento Preventivo

### A. Renovación de Cookies de X/Twitter (si expiran)
Si X invalida las cookies de la cuenta de servicio, el bot **no se detendrá**: conmutará automáticamente al catálogo local de reserva (`data/images/`). Para restaurar la extracción desde X:
1. Abre tu navegador web en la cuenta de servicio de X.
2. Pulsa `F12` (Herramientas de Desarrollador) → Pestaña **Application** (Chrome/Edge) o **Almacenamiento** (Firefox) → **Cookies** → `https://x.com`.
3. Copia el nuevo valor de `auth_token` y `ct0`.
4. En GitHub: Ve a **Settings** → **Secrets and variables** → **Actions**.
5. Actualiza `X_AUTH_TOKEN` y `X_CT0` con los nuevos valores.

### B. Agregar Más Frases o Ampliar el Corpus
Cuando el monitor de salud indique que restan pocas frases literales:
1. Coloca un nuevo documento o reemplaza `data/corpus.pdf`.
2. Ejecuta el workflow **Validar proyecto** para auditar que el nuevo PDF sea extraíble.
3. El generador de cadenas de Markov incorporará inmediatamente el nuevo vocabulario.

### C. Agregar Nuevas Imágenes Locales
Para nutrir el catálogo de reserva:
1. Sube archivos `.jpg` o `.png` de alta resolución a la carpeta `data/images/`.
2. Mantén los nombres limpios y descriptivos (por ejemplo: `obra_04.jpg`).
3. El bot calculará sus hashes SHA-256 automáticamente y las utilizará cuando corresponda.

### D. Modificar Cuentas Autorizadas en X
1. Edita el archivo `data/x_allowlist.json`.
2. Añade o desactiva cuentas cambiando `"enabled": true` o `false`.
3. Ejecuta **Validar proyecto** para verificar la sintaxis del JSON.

---

## 3. Protocolos de Emergencia y Control

### ¿Cómo pausar temporalmente las publicaciones automáticas?
1. Abre `.github/workflows/publish.yml`.
2. Comenta o elimina el bloque `schedule:` (las líneas con `- cron:`).
3. Haz commit a la rama `main`. El bot solo publicará cuando pulses **Run workflow** manualmente.

### ¿Cómo forzar una publicación de prueba sin salir en vivo?
1. Ve a **Actions** → **Publicar o simular meme**.
2. Pulsa **Run workflow** asegurándote de que la casilla **Modo simulación (Dry Run)** esté **marcada**.
3. Descarga el artefacto generado para inspeccionar el resultado sin emitir posts a Bluesky.

---

## 4. Bucle Cibernético de Aprendizaje

El motor de decisión creativa (`src/decision_engine.py`) modula la selección estética según el volumen histórico acumulado en `data/state.json`:

- **Posts 1 a 30 (Fase 1 - Exploración Pura):** 100% decisiones aleatorias para calibración estadística.
- **Posts 31 a 100 (Fase 2 - Preferencia Suave):** 80% exploración y 20% sesgo hacia los rasgos con mayor score.
- **Posts > 100 (Fase 3 - Equilibrio Generativo):** 40% exploración obligatoria y 60% explotación de patrones celebrados.
