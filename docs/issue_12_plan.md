# Development Plan — Issue #12: Loader async — escritura eficiente en TimescaleDB (M3)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-12-async-loader`  
**Milestone:** M3 — Persistencia & API  
**GitHub Issue:** [#12](https://github.com/ale-camer/real-time-market-events/issues/12)

---

## Objective

El objetivo de este issue es construir el **Data Loader Asincrónico**. Este módulo se encargará de consumir los eventos enriquecidos y las agregaciones de OHLCV desde nuestros tópicos de Kafka para insertarlos de forma eficiente (en *batches* o lotes) dentro de nuestras tablas particionadas en TimescaleDB. Utilizaremos el motor asincrónico de SQLAlchemy configurado en el issue anterior.

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-12-async-loader

# 4. Link branch to GitHub Issue #12
gh issue develop 12 --checkout
# If already created, push manually:
git push -u origin feature/issue-12-async-loader
```

---

## Step 1 — Crear el Writer Asincrónico (`src/loaders/db_writer.py`)

Necesitamos una clase o módulo que gestione la inserción masiva. SQLAlchemy 2.0 provee operaciones de bulk insert que funcionan excepcionalmente bien con `asyncpg`.

**Requirements:**
1. Crear la carpeta `src/loaders/` (con su respectivo `__init__.py`).
2. Crear `src/loaders/db_writer.py`.
3. Crear una función `async def bulk_insert_events(session: AsyncSession, events: list[dict]) -> None:` que reciba un lote de eventos y use la sentencia asincrónica de SQLAlchemy para guardarlos.
4. Crear una función similar `async def bulk_insert_ohlcv(session: AsyncSession, candles: list[dict]) -> None:` para la inserción de datos en la tabla de agregaciones.
5. Emplear manejo de colisiones (ej. `on_conflict_do_nothing` del dialecto `postgresql`) por si se llega a intentar grabar el mismo ID/timestamp simultáneamente.

**Verify:**
Crear `tests/loaders/test_db_writer.py` para testear con Mocks o afirmaciones sobre el compilador de SQL que las consultas de inserción masiva se generan correctamente.
```bash
pytest tests/loaders/test_db_writer.py -v
```

---

## Step 2 — Configurar el Consumer/Loader Agent (`src/loaders/agent.py`)

Para abstraernos de la gestión de conexiones y punteros de Kafka, usaremos un agente dedicado de Faust (o un simple consumer async) que lea de los tópicos resultantes y llene los buffers.

**Requirements:**
1. Crear `src/loaders/agent.py`.
2. Crear un *Agente de Faust* (o proceso de consumo) que se suscriba a los tópicos relevantes de salida (donde viaja la info enriquecida).
3. Implementar un **buffer por lotes**: El agente debe encolar los eventos en memoria hasta alcanzar un `batch_size` (ej: 500 registros) o hasta que se cumpla un timeout.
4. Al activarse el flush del buffer, debe instanciar una sesión con `get_db_session()` y pasarle la lista al writer del Step 1, limpiando el buffer al finalizar.

**Verify:**
Crear `tests/loaders/test_agent.py` para asegurar que el agente encole correctamente la data y sólo gatille el flush al cumplir la capacidad del lote.
```bash
pytest tests/loaders/test_agent.py -v
```

---

## Step 3 — Linting & Type Check

Garantizar que todo el código del módulo loader cumpla con el estándar del proyecto.

```bash
ruff check src/loaders/ tests/loaders/ --fix
ruff format src/loaders/ tests/loaders/
mypy src/loaders/ tests/loaders/
```

---

## Step 4 — Commit, Push & PR

```bash
# Stage changes
git add src/loaders/ tests/loaders/ docs/issue_12_plan.md

# Commit
git commit -m "feat(m3): implement async db loader for timescaledb (#12)"

# Push and PR
git push origin feature/issue-12-async-loader

gh pr create \
  --title "feat(m3): Async DB Loader for TimescaleDB (#12)" \
  --body "Closes #12. Implementa batch inserts asincrónicos para persistir el flujo de eventos desde Kafka hacia Postgres/TimescaleDB." \
  --base develop \
  --head feature/issue-12-async-loader
```
