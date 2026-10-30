# 🎭 dusalecuador1984_meme_bot: Generador Autónomo de Cadáver Exquisito Digital

[![Publicar Meme](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/publish.yml/badge.svg)](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/publish.yml)
[![Recopilar Métricas](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/metrics.yml/badge.svg)](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/metrics.yml)
[![Validar Proyecto](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/validate.yml/badge.svg)](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/validate.yml)
[![Health Check](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/health_check.yml/badge.svg)](https://github.com/ojitosdeemoji/dusalecuador1984_meme_bot/actions/workflows/health_check.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Bluesky](https://img.shields.io/badge/Bluesky-AT%20Protocol-0085ff.svg)](https://bsky.app)

**dusalecuador1984_meme_bot** es un agente cibernético autónomo diseñado para generar, componer y publicar obras de arte medial inspiradas en el principio surrealista del **cadáver exquisito** y en la distopía política contemporánea. 

La obra fusiona fragmentos del texto clásico *1984* de George Orwell (sintetizados mediante Cadenas de Markov) con imágenes institucionales extraídas automáticamente vía *web scraping* desde las redes oficiales del Ejecutivo y Ministerios. Todo el proceso es ejecutado de forma autónoma por un bot en **Bluesky**, actuando como un experimento sobre la autoría, el vaciado legal, la persecución estatal contra la cultura memética y la libertad de expresión en la esfera digital.

---

## 👁️ Declaración Conceptual

En el contexto hipervigilado del presente sociopolítico, la persecución estatal frente a la sátira digital y la penalización de expresiones en redes sociales han instaurado una atmósfera de paranoia colectiva que resuena con el *Gran Hermano* orwelliano. 

**dusalecuador1984_meme_bot** responde a esta problemática mediante las siguientes premisas:

1. **Suspensión de la Autoría Tradicional:** Ante la falta de capacidades técnicas avanzadas para programar y la urgencia de responder a la contingencia actual (*FOMO*), se utiliza la Inteligencia Artificial no solo como prótesis instrumental, sino como un **agente ejecutor**. El creador actúa como un *director conceptual*, desplazando la responsabilidad autoral hacia un proceso algorítmico y descentralizado.
2. **Zona Gris y Vaciado Legal:** El artista no selecciona directamente las imágenes, no redacta las frases ni presiona el botón de envío. La obra existe como un bucle generativo implantado en un modelo cibernético que se autoalimenta e interactúa de manera autónoma con el público.
3. **Sátira como Resistencia Alogrítmica:** El meme deja de ser un chiste efímero para convertirse en una herramienta de distanciamiento crítico, enfrentando la imaginería del poder institucional con la sintaxis del control político distópico.

---

## 🏛️ Arquitectura del Sistema

```text
       ┌────────────────────────┐         ┌────────────────────────┐
       │   data/corpus.pdf      │         │ Cuentas Gubernamentales│
       │     (Texto 1984)       │         │ (Scraping de Imágenes) │
       └───────────┬────────────┘         └───────────┬────────────┘
                   │                                  │
                   ▼                                  ▼
       ┌────────────────────────┐         ┌────────────────────────┐
       │  src/markov_generator  │         │    src/image_source    │
       │ (Síntesis de Markov)   │         │ (Extracción + Fallback)│
       └───────────┬────────────┘         └───────────┬────────────┘
                   │                                  │
                   └────────────────┬─────────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │    src/image_composer     │
                      │  (Renderizado con Pillow) │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │       src/publisher       │
                      │  (AT Protocol / Bluesky)  │
                      └─────────────┬─────────────┘
                                    │
                                    ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │  src/metrics_collector │       │    data/state.json     │
       │  (Lectura de Feedback) │──────▶│ (Persistencia Atómica) │
       └───────────┬────────────┘       └───────────┬────────────┘
                   │                                │
                   ▼                                ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │      src/scoring       │──────▶│  src/decision_engine   │
       │ (Atenuación Temporal)  │       │ (Exploración/Explotac.)│
       └────────────────────────┘       └────────────────────────┘
```

---

## 🛠️ Componentes Técnicos

- **Síntesis de Markov (`src/markov_generator`):** Descompone la novela *1984* para generar aforismos y estructuras sintácticas de tono autoritario y distópico de forma probabilística.
- **Extracción de Imagen (`src/image_source`):** Realiza *web scraping* dinámico sobre fuentes de información institucional y cuentas gubernamentales públicas, extrayendo material fotográfico de contingencia.
- **Composición Visual (`src/image_composer`):** Tipografía y superposición en capas mediante Pillow, imitando la estética del "meme" como vehículo de mensaje político.
- **Retroalimentación Adaptativa (`src/decision_engine`):** Monitorea la respuesta de la audiencia en Bluesky (*likes* y *reposts*) para ajustar gradualmente las estrategias generativas del bot, convirtiendo al público en parte de la cadena cibernética de la obra.