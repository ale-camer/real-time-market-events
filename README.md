# Real-Time Market Events Stream 🚀

> **Estado:** 🚀 Finalizado — Proyecto Portfolio (Versión 1.0)

Pipeline de streaming en tiempo real para captura, transformación y persistencia de eventos de mercado financiero (crypto, forex, acciones) usando Kafka, Faust y TimescaleDB.

---

## 📐 Arquitectura

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FUENTES DE DATOS                                 │
│  CoinGecko WS  │  Polygon.io WS  │  Alpha Vantage REST  │  Otros        │
└───────┬────────────────┬──────────────────┬─────────────────────────────┘
        │                │                  │
        ▼                ▼                  ▼
┌──────────────────────────────────────────────────────┐
│              KAFKA PRODUCERS (M1)                     │
│  • WebSocket Extractor (crypto, stocks)               │
│  • REST Poller (forex, fallback)                      │
│  • Schema validation (Pydantic/Avro)                  │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   [market.events.crypto]   [market.events.forex]   [market.events.stocks]
          │            │            │             [market.events.dlq]
          └────────────┼────────────┘
                       ▼
┌──────────────────────────────────────────────────────┐
│           FAUST STREAM PROCESSOR (M2)                 │
│  • Normalización de eventos                           │
│  • Enriquecimiento (OHLCV, métricas derivadas)        │
│  • Dead-letter queue (DLQ) para errores               │
│  • Windowed aggregations (1m, 5m, 1h)                 │
└──────────────────────┬───────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
┌──────────────────┐    ┌──────────────────────────┐
│  TimescaleDB (M3)│    │  FastAPI REST API (M3)    │
│  • Hypertables   │    │  • /events endpoint        │
│  • Continuous    │    │  • /metrics endpoint       │
│    aggregates    │    │  • WebSocket push          │
│  • Compresión    │    └──────────────────────────┘
└──────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────┐
│           OBSERVABILIDAD (M4)                         │
│  • Grafana dashboards (precio, volumen, latencia)     │
│  • Alertas por anomalías de precio                    │
│  • Airflow DAGs (reconciliación batch diaria)         │
│  • GitHub Actions CI/CD                               │
└──────────────────────────────────────────────────────┘
```

## 🗂️ Estructura del Proyecto

```
real-time-market-events/
├── src/
│   ├── extractors/          # M1 - WebSocket & REST extractors
│   ├── producers/           # M1 - Kafka producers
│   ├── schemas/             # M1 - Pydantic models & Avro schemas
│   ├── consumers/           # M2 - Faust stream processors
│   ├── transformers/        # M2 - Event transformation logic
│   ├── loaders/             # M3 - TimescaleDB writers
│   └── api/                 # M3 - FastAPI application
├── dags/                    # M4 - Apache Airflow DAGs (batch reconciliation)
├── tests/
│   ├── unit/
│   └── integration/
├── infra/
│   ├── docker/              # Dockerfiles
│   ├── docker-compose.yml   # Local dev environment
│   └── terraform/           # Cloud infra (optional)
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
│   └── issue_*.md
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🏁 Milestones

| # | Milestone | Descripción |
|---|-----------|-------------|
| M1 | Ingesta & Kafka | Extractores WebSocket/REST + Kafka Producer + validación de schemas |
| M2 | Stream Processing | Faust consumers + transformaciones + DLQ |
| M3 | Persistencia & API | TimescaleDB schema + Loader + FastAPI endpoints |
| M4 | Observabilidad & CI/CD | Grafana + Alertas + Docker + GitHub Actions + Docs |

## ⚙️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Extracción | `websockets`, `httpx` |
| Mensajería | Apache Kafka (`confluent-kafka`) |
| Stream Processing | Faust-Streaming |
| Schema Validation | Pydantic v2, Avro (`fastavro`) |
| Base de datos | TimescaleDB (PostgreSQL) + `asyncpg` + SQLAlchemy |
| API | FastAPI + Uvicorn |
| Orquestación batch | Apache Airflow |
| Observabilidad | Grafana + Prometheus |
| CI/CD | GitHub Actions |
| Infra local | Docker Compose |

## 🚀 Quick Start

```bash
# 1. Clonar el repo
git clone https://github.com/alejandrocamerlengo/real-time-market-events.git
cd real-time-market-events

# 2. Configurar variables de entorno
cp .env.example .env 
# (Opcional) Editar .env para agregar API keys de CoinGecko o Polygon si se desean datos reales.

# 3. Levantar toda la infraestructura (Kafka, DB, Grafana, API, Worker, Producer)
docker compose up -d --build

# 4. Ejecutar migraciones de base de datos
docker compose exec api alembic upgrade head

# 5. Acceder a los servicios:
# - FastAPI (Swagger UI): http://localhost:8000/docs
# - Grafana: http://localhost:3000 (user: admin, pass: admin)
```

## 📋 Issues Abiertos

Ver [GitHub Issues](https://github.com/alejandrocamerlengo/real-time-market-events/issues) para el backlog completo.

---

*Proyecto portfolio — parte de la estrategia de job search engineering.*
