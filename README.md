# 🎭 meme-bot: Generador Autónomo de Cadáver Exquisito Digital

[![Publicar Meme](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/publish.yml/badge.svg)](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/publish.yml)
[![Recopilar Métricas](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/metrics.yml/badge.svg)](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/metrics.yml)
[![Validar Proyecto](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/validate.yml/badge.svg)](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/validate.yml)
[![Health Check](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/health_check.yml/badge.svg)](https://github.com/ojitosdeemoji/meme-bot/actions/workflows/health_check.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Bluesky](https://img.shields.io/badge/Bluesky-AT%20Protocol-0085ff.svg)](https://bsky.app)

**meme-bot** es un agente cibernético autónomo diseñado para generar, componer y publicar obras de arte conceptual inspiradas en el principio surrealista del **cadáver exquisito**. Combina citas filosóficas y aforismos sintetizados mediante Cadenas de Markov con imágenes de archivo histórico y de actualidad obtenidas de X/Twitter (o su catálogo local de contingencia), publicando automáticamente en **Bluesky**.

---

## 🏛️ Arquitectura del Sistema

```text
       ┌────────────────────────┐         ┌────────────────────────┐
       │   data/corpus.pdf      │         │   Cuentas en X (Allow) │
       │  (Textos Filosóficos)  │         │   o Catálogo Local     │
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
