# Development Plan — Issue #9: Windowed Aggregations (M2)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-9-windowed-aggregations`  
**Milestone:** M2 — Stream Processing  
**GitHub Issue:** [#9](https://github.com/ale-camer/real-time-market-events/issues/9)

---

## Objective

Implementar las **agregaciones por ventanas de tiempo (Windowed Aggregations)** usando Faust. El objetivo es procesar el stream de eventos en tiempo real y calcular las velas OHLCV (Open, High, Low, Close, Volume) en intervalos de 1 minuto (tumbling windows). Esto reducirá exponencialmente el volumen de datos que llegará a la base de datos (TimescaleDB) en el Milestone 3 y preparará la data procesada para los gráficos del dashboard en el Milestone 4.

---

## Step 0 — Activate venv & Create Feature Branch

> Always do this before touching any code.

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-9-windowed-aggregations

# 4. Link branch to GitHub Issue #9
gh issue develop 9 --checkout
# If already created, push manually:
git push -u origin feature/issue-9-windowed-aggregations
```

**Verify:**
```bash
git branch --show-current
gh issue view 9
```

---

## Step 1 — Define OHLCV Schema (`src/schemas/ohlcv.py`)

Crear el modelo Pydantic para representar los datos agregados.

**Requirements:**
1. Crear la clase `OHLCV` heredando de `BaseModel`.
2. Incluir los campos: `symbol` (str), `timestamp` (float o str indicando el inicio de la ventana), `open` (float), `high` (float), `low` (float), `close` (float), y `volume` (float).
3. (Opcional pero recomendado) Incluir métodos helpers en el modelo, como `def update(self, price: float, volume: float)` para facilitar la lógica de actualización continua.

**Verify:**
```bash
python -c "from src.schemas.ohlcv import OHLCV; print('OHLCV Schema loaded.')"
```

---

## Step 2 — Define Aggregation Topics & Tables (`src/consumers/aggregations.py`)

Configurar las Tablas (Tables) de Faust, que son las que manejan el estado particionado para las ventanas.

**Requirements:**
1. Instanciar una tabla para cada asset class (ej: `crypto_ohlcv_1m = app.Table("crypto_ohlcv_1m", default=OHLCV)`).
2. Configurar la tabla para usar **tumbling windows** de 1 minuto usando `.tumbling(60.0)`.
3. Crear los topics de salida correspondientes (ej: `crypto_ohlcv_topic = app.topic("market.crypto.ohlcv.1m")`) donde podríamos eventualmente derivar el resultado al cerrar la ventana.

**Verify:**
```bash
python -c "from src.consumers.aggregations import crypto_ohlcv_1m; print('Tables configured.')"
```

---

## Step 3 — Implement Aggregation Logic (`src/consumers/agents.py`)

Integrar la lógica de cálculo de OHLCV dentro de los agentes procesadores de streams ya existentes.

**Requirements:**
1. Importar las tablas del Paso 2.
2. Dentro del iterador, luego de obtener el `enriched_event`, acceder a la ventana actual en la tabla de Faust usando el `normalized_symbol` como key de diccionario.
3. Si la key no existe (inicio de ventana), inicializar el OHLCV (open=precio, high=precio, low=precio, close=precio, volume=volumen).
4. Si ya existe, aplicar la lógica OHLCV: `high = max(high, precio)`, `low = min(low, precio)`, `close = precio`, `volume += volumen`.
5. Asegurarse de que todo este código esté dentro del bloque `try-except` que envía errores al DLQ (implementado en el Issue 8).

**Verify:**
```bash
# Validar sintaxis
ruff check src/consumers/agents.py
```

---

## Step 4 — Full Lint & Type Check Pass

Ejecutar validaciones globales para asegurar que los tipos encajen con Faust.

```bash
# Linting & Formatting
ruff check src/ --fix
ruff format src/

# Static type analysis
mypy src/
```

---

## Step 5 — Commit, Push & Open PR

```bash
# Stage new files
git add src/ docs/issue_9_plan.md

# Commit
git commit -m "feat(m2): implement windowed aggregations for OHLCV (#9)

- Adds OHLCV Pydantic schema
- Configures Faust Tables with 1-minute tumbling windows
- Integrates stateful OHLCV calculation logic into consumer agents"

# Push branch
git push origin feature/issue-9-windowed-aggregations
```

Open Pull Request:
```bash
gh pr create \
  --title "feat(m2): Windowed Aggregations (OHLCV) (#9)" \
  --body "Closes #9. Implements stateful 1-minute tumbling window aggregations in Faust to compute real-time OHLCV metrics." \
  --base develop \
  --head feature/issue-9-windowed-aggregations
```

---

## Step 6 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 9 --comment "Implemented via PR — Windowed aggregations completed."

# Sync local develop
git checkout develop
git pull origin develop
```
