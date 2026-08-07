# Development Plan — Issue #15: Tests de integración DB (M3)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-15-db-integration-tests`  
**Milestone:** M3 — Persistencia & API  
**GitHub Issue:** [#15](https://github.com/ale-camer/real-time-market-events/issues/15)

---

## Objective

El objetivo final de nuestro Milestone 3 es asegurar la calidad absoluta (Quality Assurance) de nuestra capa de persistencia. Hasta ahora, validamos los repositorios y la API usando *Mocks*. En este issue implementaremos **Tests de Integración reales** utilizando `testcontainers-python`. Levantaremos un motor TimescaleDB temporal (en Docker) solo para la suite de testing, correremos las migraciones de Alembic, insertaremos datos y consultaremos los endpoints. Al finalizar este issue, habremos coronado el M3 y uniremos todo el trabajo hacia la rama `main`.

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-15-db-integration-tests

# 4. Link branch to GitHub Issue #15
gh issue develop 15 --checkout
# If already created, push manually:
git push -u origin feature/issue-15-db-integration-tests
```

---

## Step 1 — Instalar Dependencias de Integración

Necesitamos incorporar la librería `testcontainers` para poder controlar Docker desde Pytest.

**Requirements:**
1. Instalar la librería `testcontainers[postgres]` en el entorno virtual. Opcionalmente podemos agregarla en una sección `[project.optional-dependencies]` de test en el `pyproject.toml`.
```bash
pip install testcontainers[postgres] pytest-asyncio
```

---

## Step 2 — Configurar Testcontainers Fixture (`tests/conftest.py`)

Vamos a crear el motor (fixture) que levante y apague la DB en cada corrida de tests.

**Requirements:**
1. Crear o editar `tests/conftest.py`.
2. Configurar un fixture de Pytest (`@pytest.fixture(scope="session")`) que levante un contenedor usando `PostgresContainer(image="timescale/timescaledb:latest-pg14")`.
3. Extraer la `DATABASE_URL` del contenedor y ejecutar las migraciones de Alembic de forma programática contra esa base efímera.
4. Crear otro fixture que reemplace (Dependency Override) el `get_db_session` de FastAPI para que la API en test lea la DB de Testcontainers.

**Verify:**
Crear un archivo `tests/db/test_db_connection.py` con un test simple para verificar que el contenedor levanta correctamente y SQLAlchemy puede conectarse a la DB.
```bash
pytest tests/db/test_db_connection.py -v
```

---

## Step 3 — Escribir el Test de Integración (`tests/api/test_integration.py`)

Haremos una prueba "End-to-End" (E2E) que toque desde la API hasta la DB real.

**Requirements:**
1. Crear `tests/api/test_integration.py`.
2. Usar SQLAlchemy directo en el test para hacer un `INSERT` de una o dos velas `OHLCVModel` falsas pero en la tabla real.
3. Usar el `TestClient` de FastAPI para llamar a `GET /api/v1/ohlcv/{symbol}`.
4. Asercionar (assert) que el JSON de respuesta devuelva exactamente las velas que insertamos.

**Verify:**
Correr exclusivamente el archivo de integración. Va a tardar un poquito más porque descarga/levanta la imagen de Docker, pero la confianza que da es invaluable.
```bash
pytest tests/api/test_integration.py -v
```

---

## Step 4 — Linting & Type Check

Validar la sanidad del código (Ruff / MyPy) antes del último commit.

```bash
ruff check src/ tests/ --fix
ruff format src/ tests/
mypy src/ tests/
```

---

## Step 5 — Commit, Push y Merge a Develop

Cerramos oficialmente el Issue #15 incorporándolo a `develop`.

```bash
# Stage changes
git add pyproject.toml tests/ docs/issue_15_plan.md

# Commit
git commit -m "test(m3): implement real db integration tests via testcontainers (#15)"

# Push and PR
git push origin feature/issue-15-db-integration-tests

gh pr create \
  --title "test(m3): Database Integration Tests (#15)" \
  --body "Closes #15. Introduce testcontainers para probar la API y DB contra un TimescaleDB real efímero." \
  --base develop \
  --head feature/issue-15-db-integration-tests

# Merge PR and cleanup
gh pr merge --squash --delete-branch
gh issue close 15
git checkout develop
git pull origin develop
```

---

## Step 6 — Release M3 (Merge develop to main)

Como este es el último ticket asignado al **Milestone 3 (Persistencia & API)**, y nuestra rama `develop` ya cuenta con repositorios, migraciones, modelos, webSockets, REST y tests de integración, es momento de lanzar una **Release oficial a Producción** (`main`).

```bash
# 1. Ir a la rama principal (main) y asegurarse de tenerla al día
git checkout main
git pull origin main

# 2. Hacer el merge desde develop hacia main, creando un commit the release
git merge develop -m "chore(release): Milestone 3 - Persistencia & API"

# 3. Empujar los cambios a main
git push origin main

# 4. Volver a develop para arrancar limpios el Milestone 4
git checkout develop
```
