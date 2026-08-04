# Issue #0 — Day 0 Setup Checklist

**Proyecto:** Real-Time Market Events Stream  
**Rama:** `feature/day-0-setup`  
**Milestone:** Pre-M1 (Scaffolding)  
**Fecha:** 2026-08-03  

---

## Objetivo

Inicializar el repositorio con el esqueleto base del proyecto. **Sin lógica de negocio.**  
Solo estructura, configuración y documentación.

---

## ✅ Checklist

### 🔀 Git Flow

- [ ] `git init` en el directorio del proyecto
- [ ] Commit vacío inicial en `main` (`--allow-empty`)
- [ ] Rama `develop` creada desde `main`
- [ ] Rama `feature/day-0-setup` creada desde `develop`
- [ ] Todo el trabajo del Día 0 se realiza en `feature/day-0-setup`

### 🐍 Entorno Virtual

- [ ] `.venv` creado con `python3 -m venv .venv`
- [ ] `.venv` verificado (`which python` dentro del entorno)
- [ ] `.venv/` incluido en `.gitignore`

### 📁 Estructura de Carpetas

- [ ] `src/` creado (con `.gitkeep`)
- [ ] `src/extractors/` creado
- [ ] `src/producers/` creado
- [ ] `src/schemas/` creado
- [ ] `src/consumers/` creado
- [ ] `src/transformers/` creado
- [ ] `src/loaders/` creado
- [ ] `src/api/` creado
- [ ] `dags/` creado (con `.gitkeep`)
- [ ] `tests/unit/` creado (con `.gitkeep`)
- [ ] `tests/integration/` creado (con `.gitkeep`)
- [ ] `infra/docker/` creado (con `.gitkeep`)
- [ ] `infra/terraform/` creado (con `.gitkeep`)
- [ ] `docs/` creado

### 📄 Archivos de Configuración

- [ ] `.gitignore` creado
- [ ] `.env.example` creado (sin valores reales)
- [ ] `pyproject.toml` creado (con metadata y grupos de dependencias comentados)

### 📝 Documentación Inicial

- [ ] `README.md` creado con arquitectura propuesta
- [ ] `docs/issue_0_setup.md` creado (este archivo)

### ☁️ GitHub

- [ ] Repositorio público creado con `gh repo create`
- [ ] Remote `origin` vinculado al repositorio local
- [ ] Push de `feature/day-0-setup` a GitHub
- [ ] PR abierto: `feature/day-0-setup` → `develop`
- [ ] Milestone **M1 - Ingesta & Kafka** creado en GitHub
- [ ] Milestone **M2 - Stream Processing** creado en GitHub
- [ ] Milestone **M3 - Persistencia & API** creado en GitHub
- [ ] Milestone **M4 - Observabilidad & CI/CD** creado en GitHub
- [ ] Issues #1–#5 creados y asignados a M1
- [ ] Issues #6–#10 creados y asignados a M2
- [ ] Issues #11–#15 creados y asignados a M3
- [ ] Issues #16–#20 creados y asignados a M4

---

## 📋 Issues Planificados

### M1 — Ingesta & Kafka (Issues #1–#5)

| # | Título | Descripción |
|---|--------|-------------|
| #1 | Extractor WebSocket CoinGecko | Implementar cliente WebSocket para eventos de crypto en tiempo real |
| #2 | Extractor REST Polygon.io | Implementar cliente REST/WebSocket para stocks y forex |
| #3 | Kafka Producer | Implementar el producer con manejo de reintentos y serialización |
| #4 | Schemas Pydantic & Avro | Definir modelos de validación de eventos de mercado |
| #5 | Tests unitarios extractores | Tests para extractores y schemas con mocks de APIs |

### M2 — Stream Processing (Issues #6–#10)

| # | Título | Descripción |
|---|--------|-------------|
| #6 | Faust App skeleton | Configurar la aplicación Faust y su ciclo de vida |
| #7 | Transformer de eventos | Normalización y enriquecimiento de eventos (OHLCV, métricas) |
| #8 | Dead-letter queue (DLQ) | Manejo de errores y eventos mal formados |
| #9 | Windowed aggregations | Agregaciones por ventanas de tiempo (1m, 5m, 1h) |
| #10 | Tests consumer & integración Kafka-Faust | Tests de integración del pipeline de stream |

### M3 — Persistencia & API (Issues #11–#15)

| # | Título | Descripción |
|---|--------|-------------|
| #11 | TimescaleDB schema & migrations | Hypertables, índices, continuous aggregates con Alembic |
| #12 | Loader / Writer async | Escritura eficiente en TimescaleDB con asyncpg |
| #13 | Consultas optimizadas | Queries OHLCV, compresión y retención de datos |
| #14 | FastAPI endpoints | REST API: /events, /metrics, WebSocket push |
| #15 | Tests integración DB | Tests de integración con base de datos real (pytest + testcontainers) |

### M4 — Observabilidad & CI/CD (Issues #16–#20)

| # | Título | Descripción |
|---|--------|-------------|
| #16 | Docker Compose infra | Kafka, Zookeeper, TimescaleDB, Grafana en compose |
| #17 | Grafana dashboards | Dashboards de precio, volumen y latencia del pipeline |
| #18 | Alertas & anomaly detection | Alertas por variaciones de precio anómalas |
| #19 | GitHub Actions CI | Pipeline de CI: lint, type check, tests, coverage |
| #20 | Documentación final | architecture.md, data_dictionary.md, ADRs |

---

## 🔗 Referencias

- [Faust Streaming](https://faust-streaming.github.io/faust/)
- [TimescaleDB Docs](https://docs.timescale.com/)
- [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/overview.html)
- [CoinGecko API](https://www.coingecko.com/en/api/documentation)
- [Polygon.io API](https://polygon.io/docs/stocks/getting-started)
