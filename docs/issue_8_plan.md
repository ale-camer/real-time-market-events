# Development Plan — Issue #8: Dead-Letter Queue (DLQ) (M2)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-8-dlq`  
**Milestone:** M2 — Stream Processing  
**GitHub Issue:** [#8](https://github.com/ale-camer/real-time-market-events/issues/8)

---

## Objective

Implementar un mecanismo de **Dead-Letter Queue (DLQ)** en el pipeline de Faust. Esto permitirá que si un evento viene corrupto o levanta una excepción durante el procesamiento o enriquecimiento, no rompa el stream entero ni se pierda de forma silenciosa. Esos eventos problemáticos serán desviados al topic `market.dlq` junto con la metadata del error (stack trace, topic de origen, etc.) para su análisis y posible reprocesamiento en el futuro.

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
git checkout -b feature/issue-8-dlq

# 4. Link branch to GitHub Issue #8
gh issue develop 8 --checkout
# If already created, push manually:
git push -u origin feature/issue-8-dlq
```

**Verify:**
```bash
git branch --show-current
gh issue view 8
```

---

## Step 1 — Define the DLQ Schema (`src/schemas/dlq_event.py`)

Crear el modelo Pydantic para estructurar los eventos que van a caer en la DLQ.

**Requirements:**
1. Crear una clase `DLQEvent` que herede de `BaseModel`.
2. Campos mínimos recomendados:
   - `original_payload` (puede ser un dict o string dependiendo de lo que se haya podido parsear).
   - `error_message` (str) - mensaje de la excepción.
   - `stack_trace` (str) - opcional.
   - `failed_at` (float) - timestamp.
   - `source_topic` (str) - en qué topic ocurrió el error.

**Verify:**
```bash
python -c "from src.schemas.dlq_event import DLQEvent; print('DLQ Schema loaded.')"
```

---

## Step 2 — Define the DLQ Topic (`src/consumers/topics.py`)

Agregar el nuevo topic de Faust adonde enviaremos los eventos fallidos.

**Requirements:**
1. Importar `DLQEvent`.
2. Crear `dlq_topic = app.topic("market.dlq", value_type=DLQEvent)`. (Agregar `# type: ignore[arg-type]` si mypy falla como nos pasó en el Issue 6).

**Verify:**
```bash
python -c "import sys; from src.consumers.topics import dlq_topic; print(f'DLQ Topic configured: {dlq_topic.get_topic_name()}')"
```

---

## Step 3 — Implement the DLQ Handler (`src/consumers/error_handler.py`)

Centralizar la lógica de envío al DLQ.

**Requirements:**
1. Crear una función asincrónica `async def send_to_dlq(payload: dict | str, error: Exception, source_topic: str) -> None`.
2. Esta función debe instanciar el `DLQEvent` armando el stack trace (podés usar el módulo `traceback` de Python) y mandarlo al `dlq_topic` usando `await dlq_topic.send(value=event)`.

**Verify:**
```bash
python -c "from src.consumers.error_handler import send_to_dlq; print('DLQ Handler loaded.')"
```

---

## Step 4 — Implement Error Handling in Agents (`src/consumers/agents.py`)

Modificar los agentes actuales para que no mueran ante una excepción.

**Requirements:**
1. Dentro del iterador `async for event in stream:`, envolver la llamada a `enrich_event` (y cualquier otra lógica de procesamiento) en un bloque `try-except Exception as e`.
2. En caso de captura, ejecutar `await send_to_dlq(event.model_dump(), e, "market.xxx")`.
3. Loguear con `logger.error()` que el evento falló y fue derivado al DLQ.

**Verify:**
```bash
# Revisar que la sintaxis esté bien antes de mypy
ruff check src/consumers/agents.py
```

---

## Step 5 — Full Lint & Type Check Pass

Ejecutar validaciones globales.

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
git add src/ docs/issue_8_plan.md

# Commit
git commit -m "feat(m2): implement dead-letter queue (DLQ) for stream errors (#8)

- Adds DLQEvent schema
- Configures market.dlq topic in Faust
- Creates async error handler to route failed events to DLQ
- Adds try-except error catching in Faust stream agents"

# Push branch
git push origin feature/issue-8-dlq
```

Open Pull Request:
```bash
gh pr create \
  --title "feat(m2): Dead-Letter Queue (DLQ) (#8)" \
  --body "Closes #8. Implements error catching and DLQ routing in Faust pipeline to prevent stream crashes." \
  --base develop \
  --head feature/issue-8-dlq
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 8 --comment "Implemented via PR — DLQ routing configured."

# Sync local develop
git checkout develop
git pull origin develop
```
