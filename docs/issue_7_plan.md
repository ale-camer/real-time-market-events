# Development Plan — Issue #7: Transformer de eventos (M2)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-7-event-transformer`  
**Milestone:** M2 — Stream Processing  
**GitHub Issue:** [#7](https://github.com/ale-camer/real-time-market-events/issues/7)

---

## Objective

Implementar la capa de transformación de eventos (`src/transformers`). Esto incluye la normalización de los eventos entrantes (estandarización de símbolos, formatos de fecha) y el enriquecimiento stateless (agregando metadatos de procesamiento) antes de pasarlos a la capa de agregación (Issue 9) o la base de datos. Además, se definirán los schemas de salida `EnrichedMarketEvent`.

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
git checkout -b feature/issue-7-event-transformer

# 4. Link branch to GitHub Issue #7
gh issue develop 7 --checkout
# If already created, push manually:
git push -u origin feature/issue-7-event-transformer
```

---

## Step 1 — Define Enriched Schemas (`src/schemas/enriched_event.py`)

Crear los modelos Pydantic para los datos ya transformados.

**Requirements:**
1. Crear un modelo base `EnrichedMarketEvent` que herede de `BaseMarketEvent` (o que contenga los mismos datos base).
2. Agregar nuevos campos, por ejemplo: `processed_timestamp` (timestamp de cuando Faust procesó el evento), `normalized_symbol` (símbolo en formato estándar), e indicadores básicos si aplican.

**Verify:**
```bash
python -c "from src.schemas.enriched_event import EnrichedMarketEvent; print('Enriched schemas loaded.')"
```

---

## Step 2 — Implement Normalization Logic (`src/transformers/normalization.py`)

Crear funciones puras para normalizar los datos del evento.

**Requirements:**
1. Función `normalize_symbol(symbol: str, asset_class: str) -> str` que asegure que todos los pares tengan el mismo formato (por ejemplo, separando base y quote currency si es posible, o asegurando mayúsculas y guiones).
2. Función `normalize_timestamp(ts: float) -> str` que convierta el timestamp de UNIX a un formato ISO 8601 UTC unificado.

**Verify:**
```bash
python -c "from src.transformers.normalization import normalize_symbol; print('Normalization module loaded.')"
```

---

## Step 3 — Implement Enrichment Logic (`src/transformers/enrichment.py`)

Crear la función principal que toma un evento crudo y devuelve un evento enriquecido.

**Requirements:**
1. Función `enrich_event(event: BaseMarketEvent) -> EnrichedMarketEvent`.
2. Esta función debe invocar los normalizadores del Paso 2 y popular los nuevos campos definidos en el Paso 1 (por ejemplo, calculando el `processed_timestamp` actual).

**Verify:**
```bash
python -c "from src.transformers.enrichment import enrich_event; print('Enrichment module loaded.')"
```

---

## Step 4 — Integrate Transformers into Faust Agents (`src/consumers/agents.py`)

Actualizar los agentes esqueleto creados en el Issue 6 para que utilicen los transformadores.

**Requirements:**
1. Importar `enrich_event`.
2. Dentro de `process_crypto_events`, `process_stock_events` y `process_forex_events`, invocar `enrich_event(event)` por cada evento del stream.
3. Actualizar el log para imprimir el evento ya enriquecido.

**Verify:**
```bash
# Verificar que mypy apruebe los cambios en los tipos
mypy src/consumers/agents.py
```

---

## Step 5 — Full Lint & Type Check Pass

Ejecutar las validaciones en todo el proyecto.

```bash
# Linting & Formatting
ruff check src/ --fix
ruff format src/

# Static type analysis
mypy src/
```

---

## Step 6 — Commit, Push & Open PR

```bash
# Stage new files
git add src/ docs/issue_7_plan.md

# Commit
git commit -m "feat(m2): implement event normalization and enrichment (#7)

- Adds EnrichedMarketEvent schemas
- Implements stateless normalization and enrichment logic
- Integrates transformers into Faust agents"

# Push branch
git push origin feature/issue-7-event-transformer
```

Open Pull Request:
```bash
gh pr create \
  --title "feat(m2): Event Transformer (#7)" \
  --body "Closes #7. Implements normalization and stateless enrichment for market events inside Faust agents." \
  --base develop \
  --head feature/issue-7-event-transformer
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 7 --comment "Implemented via PR — Event Transformers created."

# Sync local develop
git checkout develop
git pull origin develop
```
