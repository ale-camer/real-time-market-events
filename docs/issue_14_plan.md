# Development Plan — Issue #14: FastAPI — endpoints REST y WebSocket push (M3)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-14-fastapi`  
**Milestone:** M3 — Persistencia & API  
**GitHub Issue:** [#14](https://github.com/ale-camer/real-time-market-events/issues/14)

---

## Objective

El objetivo de este issue es construir la **Capa de Presentación / API**. Expondremos los datos de mercado mediante **FastAPI**. Por un lado, armaremos endpoints REST ultrarrápidos apoyados en los repositorios de bases de datos que construimos en el issue anterior. Por otro lado, configuraremos un endpoint de **WebSockets** que nos permita "pushear" eventos en tiempo real (leyendo directamente desde Kafka o un broker intermedio) hacia cualquier cliente frontend o tablero de visualización.

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-14-fastapi

# 4. Link branch to GitHub Issue #14
gh issue develop 14 --checkout
# If already created, push manually:
git push -u origin feature/issue-14-fastapi
```

---

## Step 1 — Habilitar Dependencias

Descomentar (o agregar) las librerías de FastAPI en nuestro gestor de dependencias.

**Requirements:**
1. Editar `pyproject.toml`.
2. Descomentar las dependencias `fastapi>=0.111.0` y `uvicorn[standard]>=0.30.0` en la sección M3.
3. Ejecutar la actualización del entorno virtual:
```bash
pip install -e .
```

---

## Step 2 — Inicializar App y Endpoints REST (`src/api/routes/rest.py`)

Armaremos los endpoints HTTP estándar que consulten la base de datos a través de SQLAlchemy.

**Requirements:**
1. Crear el paquete `src/api/` y `src/api/routes/`.
2. Crear `src/api/routes/rest.py`.
3. Definir un router de FastAPI (`APIRouter`).
4. Armar el endpoint `GET /api/v1/ohlcv/{symbol}` que reciba `start_time`, `end_time` y un `interval` opcional, e inyecte `AsyncSession` usando `Depends(get_db_session)`.
5. Armar el endpoint `GET /api/v1/ranking/volume` que devuelva el ranking de activos por volumen, inyectando también la DB.

**Verify:**
Crear `tests/api/test_rest.py` y usar `httpx.AsyncClient` o `TestClient` para mockear la BD y validar la estructura JSON de la respuesta.
```bash
pytest tests/api/test_rest.py -v
```

---

## Step 3 — Endpoint de WebSockets (`src/api/routes/ws.py`)

Configurar la conexión bidireccional para el streaming en vivo.

**Requirements:**
1. Crear `src/api/routes/ws.py`.
2. Crear un endpoint `WebSocket` en `/ws/market/{symbol}` (o global).
3. (Opcional/Simplificado para este issue) Crear un "gestor de conexiones" (Connection Manager) que guarde las conexiones activas. Más adelante (o aquí mismo si usamos `aiokafka`), conectaremos este manager para que envíe `websocket.send_json()` cada vez que detectemos un nuevo mensaje del tópico.

**Verify:**
Agregar `test_ws.py` a los tests usando el `TestClient` de FastAPI (que permite `.websocket_connect()`) para asegurar que el endpoint acepta la conexión y maneja desconexiones.
```bash
pytest tests/api/test_ws.py -v
```

---

## Step 4 — Entrypoint Principal (`src/api/main.py`)

Unificar todo en la aplicación FastAPI.

**Requirements:**
1. Crear `src/api/main.py`.
2. Instanciar `app = FastAPI(title="Market Events API")`.
3. Incluir los routers (`app.include_router(rest.router)`, `app.include_router(ws.router)`).
4. Configurar Middlewares (CORS).

**Verify:**
Crear `tests/api/test_main.py` para validar que la app arranca correctamente y que los routers fueron incluidos (por ejemplo, mediante una petición de prueba o verificando la lista de rutas).
```bash
pytest tests/api/test_main.py -v
```

---

## Step 5 — Linting & Type Check

Verificar el tipado en la nueva API.

```bash
ruff check src/api/ tests/api/ --fix
ruff format src/api/ tests/api/
mypy src/api/ tests/api/
```

---

## Step 6 — Commit, Push & PR

```bash
# Stage changes
git add pyproject.toml src/api/ tests/api/ docs/issue_14_plan.md

# Commit
git commit -m "feat(m3): build fastapi application with rest and ws endpoints (#14)"

# Push and PR
git push origin feature/issue-14-fastapi

gh pr create \
  --title "feat(m3): FastAPI REST & WS Endpoints (#14)" \
  --body "Closes #14. Expone la data procesada mediante endpoints REST (historial/ranking) y sienta las bases para push de eventos en vivo mediante WebSockets." \
  --base develop \
  --head feature/issue-14-fastapi

# Merge PR and cleanup
gh pr merge --squash --delete-branch
gh issue close 14
git checkout develop
git pull origin develop
```
