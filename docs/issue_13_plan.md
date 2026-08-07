# Development Plan — Issue #13: Consultas optimizadas — OHLCV, ranking y alertas (M3)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-13-optimized-queries`  
**Milestone:** M3 — Persistencia & API  
**GitHub Issue:** [#13](https://github.com/ale-camer/real-time-market-events/issues/13)

---

## Objective

El objetivo de este issue es construir la **Capa de Consultas (Data Access Layer)**. Para que nuestra futura API FastAPI sea increíblemente rápida, necesitamos pre-armar consultas asincrónicas en SQLAlchemy que aprovechen todo el poder de las *hypertables* de TimescaleDB. Desarrollaremos funciones para extraer el historial OHLCV (soportando re-agrupamiento temporal o *time_bucket*), y consultas analíticas como el top de activos por volumen.

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-13-optimized-queries

# 4. Link branch to GitHub Issue #13
gh issue develop 13 --checkout
# If already created, push manually:
git push -u origin feature/issue-13-optimized-queries
```

---

## Step 1 — Crear el Repositorio de Consultas (`src/db/repositories.py`)

Necesitamos aislar la lógica de lectura de la base de datos para que la API solo tenga que llamar a estas funciones, manteniendo el código limpio.

**Requirements:**
1. Crear el archivo `src/db/repositories.py`.
2. Crear una función asincrónica `get_ohlcv_history(session, symbol, start_time, end_time, interval)` que reciba la sesión y busque en la tabla `ohlcv_candles` filtrando por el índice de fecha. Debe retornar la lista de velas ordenadas por tiempo.
3. Crear una función `get_top_volume_assets(session, start_time, end_time, limit=10)` que consulte la tabla `market_events` (o `ohlcv_candles`), agrupe por `symbol`, sume el volumen total en ese rango de tiempo, y retorne los top `limit` activos.

**Verify:**
Crear `tests/db/test_repositories.py` para verificar (mediante mocks sobre la sesión de SQLAlchemy) que las sentencias SQL (`select()`, `group_by()`, `order_by()`) se arman con las columnas y filtros correctos.
```bash
pytest tests/db/test_repositories.py -v
```

---

## Step 2 — (Opcional pero recomendado) Aprovechar `time_bucket` de TimescaleDB

Si la API pide velas de 1 hora y nosotros solo tenemos guardadas velas de 1 minuto, necesitamos reagruparlas al vuelo.

**Requirements:**
1. En `get_ohlcv_history`, si el `interval` es mayor a 1 minuto, utilizar `sqlalchemy.func.time_bucket()` para agrupar dinámicamente las velas de 1 minuto en bloques mayores (sumando el volumen, obteniendo el `max(high)`, `min(low)`, etc.).
2. *Nota:* SQLAlchemy permite usar cualquier función nativa de Postgres mediante `func`.

**Verify:**
Asegurar que se haya implementado `test_get_ohlcv_history_time_bucket` en `tests/db/test_repositories.py` para validar la lógica del bucket:
```bash
pytest tests/db/test_repositories.py -v
```

---

## Step 3 — Linting & Type Check

Verificar el tipado y formato de las nuevas consultas.

```bash
ruff check src/db/ tests/db/ --fix
ruff format src/db/ tests/db/
mypy src/db/ tests/db/
```

---

## Step 4 — Commit, Push & PR

```bash
# Stage changes
git add src/db/ tests/db/ docs/issue_13_plan.md

# Commit
git commit -m "feat(m3): implement optimized queries for ohlcv and volume ranking (#13)"

# Push and PR
git push origin feature/issue-13-optimized-queries

gh pr create \
  --title "feat(m3): Optimized DB Queries (#13)" \
  --body "Closes #13. Implementa funciones asincrónicas en SQLAlchemy para lectura rápida de historial OHLCV y cálculo de top volumen usando funciones nativas de TimescaleDB." \
  --base develop \
  --head feature/issue-13-optimized-queries

# Merge PR and cleanup (Run these after PR is approved and checks pass)
gh pr merge --squash --delete-branch
gh issue close 13
git checkout develop
git pull origin develop
```
