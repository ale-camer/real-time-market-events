# Development Plan — Issue #11: TimescaleDB — schema, hypertables y migrations (M3)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-11-timescaledb-schema`  
**Milestone:** M3 — Persistencia & API  
**GitHub Issue:** [#11](https://github.com/ale-camer/real-time-market-events/issues/11)

---

## Objective

Arrancamos el **Milestone 3**. El objetivo de este issue es establecer la capa de persistencia utilizando PostgreSQL extendido con **TimescaleDB** para optimizar el almacenamiento y consulta de series de tiempo. Para ello, configuraremos SQLAlchemy 2.0 con soporte asincrónico, inicializaremos Alembic para manejar las migraciones de la base de datos, e inyectaremos la lógica para convertir las tablas en *hypertables*.

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-11-timescaledb-schema

# 4. Link branch to GitHub Issue #11
gh issue develop 11 --checkout
# If already created, push manually:
git push -u origin feature/issue-11-timescaledb-schema
```

---

## Step 1 — Habilitar dependencias de Persistencia

Necesitamos activar las librerías necesarias para conectarnos asincrónicamente a Postgres y gestionar modelos.

**Requirements:**
1. Abrir `pyproject.toml`.
2. Descomentar del bloque M3 las siguientes dependencias:
   - `"asyncpg>=0.29.0"`
   - `"sqlalchemy[asyncio]>=2.0.30"`
   - `"alembic>=1.13.0"`
3. Guardar e instalar:
   ```bash
   pip install -e ".[dev]"
   ```

---

## Step 2 — Configurar Modelos SQLAlchemy (`src/db/models.py`)

Definir los modelos declarativos que representarán nuestras tablas en la base de datos.

**Requirements:**
1. Crear la carpeta `src/db/` (asegurarse de que tenga `__init__.py`).
2. Crear `src/db/models.py` definiendo la clase base `Base = declarative_base()`.
3. Crear el modelo `MarketEventModel` (para eventos crudos/enriquecidos):
   - `id` (UUID o Integer autoincremental).
   - `symbol` (String).
   - `asset_class` (String).
   - `price` (Float).
   - `volume` (Float).
   - `timestamp` (DateTime, primary_key composita o indexada para Timescale).
4. Crear el modelo `OHLCVModel` (para las velas de 1 minuto):
   - `symbol` (String).
   - `timestamp` (DateTime).
   - `open`, `high`, `low`, `close` (Float).
   - `volume` (Float).

**Verify:**
Crear `tests/db/test_models.py` para verificar que `Base.metadata.tables` contiene `market_events` y `ohlcv_candles`, y que los modelos tienen las columnas esperadas.
```bash
pytest tests/db/test_models.py -v
```

---

## Step 3 — Inicializar Alembic

Configurar la herramienta de migraciones para que use `asyncpg`.

**Requirements:**
1. Ejecutar en la raíz del proyecto:
   ```bash
   alembic init -t async migrations
   ```
2. Modificar `migrations/env.py`:
   - Importar la `Base` desde `src.db.models`.
   - Setear `target_metadata = Base.metadata`.
3. Ajustar `alembic.ini` temporalmente para que lea la URL de conexión desde variables de entorno o definir un default `postgresql+asyncpg://...` (usaremos docker luego, pero Alembic necesita el dialecto correcto).

**Verify:**
Verificar que la configuración carga correctamente sin errores de importación de los modelos.
```bash
alembic history
```

---

## Step 4 — Crear la Primera Migración con Hypertables

Alembic por defecto genera tablas de Postgres estándar. Hay que inyectar el código SQL de TimescaleDB.

**Requirements:**
1. Generar la revisión base:
   ```bash
   alembic revision --autogenerate -m "init_schema"
   ```
2. Abrir el archivo generado en `migrations/versions/`.
3. En la función `upgrade()`, **después** de crear las tablas, inyectar el código para convertirlas en hypertables de TimescaleDB partiéndolas por el campo de fecha:
   ```python
   op.execute("SELECT create_hypertable('market_events', 'timestamp');")
   op.execute("SELECT create_hypertable('ohlcv_candles', 'timestamp');")
   ```

**Verify:**
Verificar visualmente que el script de migración se haya generado con el comando `create_hypertable` incluido.
```bash
grep -r "create_hypertable" migrations/versions/
```

---

## Step 5 — Configurar Engine y Sesión (`src/db/session.py`)

Preparar el punto de entrada asincrónico para cuando la aplicación (FastAPI o el Loader) necesite guardar datos.

**Requirements:**
1. Crear `src/db/session.py`.
2. Instanciar `create_async_engine()` apuntando a la URL de la base de datos.
3. Configurar el `async_sessionmaker` para gestionar el ciclo de vida de la sesión.

**Verify:**
Crear `tests/db/test_session.py` testeando (o mockeando) que `create_async_engine` se inicialice correctamente según la URI pasada y que el sessionmaker funcione.
```bash
pytest tests/db/test_session.py -v
```

---

## Step 6 — Linting & Type Check

Asegurar que toda la capa de persistencia cumpla los estándares del proyecto.

```bash
ruff check src/db/ migrations/ --fix
ruff format src/db/ migrations/
mypy src/db/
```

---

## Step 7 — Commit, Push & PR

```bash
# Stage changes
git add src/db/ migrations/ alembic.ini pyproject.toml docs/issue_11_plan.md

# Commit
git commit -m "feat(m3): setup timescaledb schema, sqlalchemy models and alembic (#11)"

# Push and PR
git push origin feature/issue-11-timescaledb-schema

gh pr create \
  --title "feat(m3): TimescaleDB Schema & Migrations (#11)" \
  --body "Closes #11. Configures SQLAlchemy async models for events and OHLCV, initializes Alembic, and sets up TimescaleDB hypertables." \
  --base develop \
  --head feature/issue-11-timescaledb-schema
```
