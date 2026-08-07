# Development Plan — Issue #10: Tests consumer & integración Kafka-Faust (M2)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-10-consumer-tests`  
**Milestone:** M2 — Stream Processing  
**GitHub Issue:** [#10](https://github.com/ale-camer/real-time-market-events/issues/10)

---

## Objective

Garantizar la calidad y robustez del pipeline de procesamiento implementando tests unitarios y de integración para la capa de consumo. Evaluaremos las funciones puras de transformación (normalización y enriquecimiento), la lógica de negocio de las agregaciones OHLCV, el manejo de errores hacia la Dead-Letter Queue (DLQ), y simularemos el comportamiento de los agentes asincrónicos de Faust. 

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
git checkout -b feature/issue-10-consumer-tests

# 4. Link branch to GitHub Issue #10
gh issue develop 10 --checkout
# If already created, push manually:
git push -u origin feature/issue-10-consumer-tests
```

**Verify:**
```bash
git branch --show-current
gh issue view 10
```

---

## Step 1 — Test Transformers & Enrichment (`tests/consumers/test_transformers.py`)

Testear las funciones "puras" que transforman los datos sin depender de Faust.

**Requirements:**
1. Crear el archivo de test en la carpeta `tests/consumers/`.
2. Escribir tests para `normalize_symbol` verificando el comportamiento para crypto, forex y stocks.
3. Escribir tests para `normalize_timestamp` para asegurar el formato ISO 8601 UTC.
4. Escribir tests para `enrich_event` usando instancias de Pydantic simuladas.

**Verify:**
```bash
pytest tests/consumers/test_transformers.py -v
```

---

## Step 2 — Test OHLCV Aggregation Logic (`tests/consumers/test_ohlcv.py`)

Asegurar que la matemática detrás del resampleo de velas japonesas sea correcta.

**Requirements:**
1. Testear `OHLCV.create_initial` verificando que setea correctamente open=high=low=close.
2. Testear `OHLCV.update()` verificando que el high suba si el precio es mayor, el low baje si el precio es menor, el close se actualice siempre, y el volumen se acumule correctamente.

**Verify:**
```bash
pytest tests/consumers/test_ohlcv.py -v
```

---

## Step 3 — Test Error Handler & DLQ (`tests/consumers/test_error_handler.py`)

Verificar el flujo de captura y ruteo de excepciones.

**Requirements:**
1. Testear la instanciación de `DLQEvent` pasando distintas combinaciones de payload (dict, str).
2. Testear asincrónicamente (`@pytest.mark.asyncio`) la función `send_to_dlq`, mockeando `dlq_topic.send` de Faust usando `unittest.mock.patch` o `AsyncMock`, para verificar que efectivamente se envía el evento con el topic correspondiente y el stacktrace.

**Verify:**
```bash
pytest tests/consumers/test_error_handler.py -v
```

---

## Step 4 — Mock Faust Agents (`tests/consumers/test_agents.py`)

Simular el procesamiento asincrónico del stream sin levantar Kafka.

**Requirements:**
1. Mockear la dependencia de `faust.StreamT` pasándole un iterador asincrónico simple o usando las utilidades de testing de Faust si estuvieran disponibles.
2. Validar que un evento válido en `process_crypto_events` termina llamando a la actualización de la tabla (mockeando el `app.Table`).
3. Validar que si `enrich_event` levanta una excepción forzada (mockeada), el agente la ataja y llama a `send_to_dlq`.

**Verify:**
```bash
pytest tests/consumers/test_agents.py -v
```

---

## Step 5 — Full Test Coverage, Lint & Type Check Pass

```bash
# Linting & Formatting
ruff check . --fix
ruff format .

# Static type analysis
mypy src/ tests/

# Run all tests with coverage for consumers
pytest tests/consumers/ --cov=src.consumers --cov=src.transformers --cov-report=term-missing
```

---

## Step 6 — Commit, Push & Open PR

```bash
# Stage new files
git add tests/ docs/issue_10_plan.md

# Commit
git commit -m "test(m2): implement unit and mock integration tests for faust consumer (#10)

- Tests transformers and enrichment logic
- Tests OHLCV calculation mathematics
- Tests DLQ error handler routing
- Adds async tests for Faust agents via mocks"

# Push branch
git push origin feature/issue-10-consumer-tests
```

Open Pull Request:
```bash
gh pr create \
  --title "test(m2): Consumer & Kafka-Faust Integration Tests (#10)" \
  --body "Closes #10. Implements comprehensive test suite for the Faust stream processing pipeline including normalization, OHLCV logic, DLQ, and async agents." \
  --base develop \
  --head feature/issue-10-consumer-tests
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 10 --comment "Implemented via PR — Consumer testing suite completed."

# Sync local develop
git checkout develop
git pull origin develop
```

---

## Step 8 — Milestone 2 (M2) Release

Al ser el último issue del Milestone 2, promovemos los cambios estables a la rama de producción (`main`).

```bash
# 1. Checkout main and ensure it's up to date
git checkout main
git pull origin main

# 2. Merge develop into main
git merge develop -m "chore(release): Milestone 2 - Stream Processing"

# 3. Push to main
git push origin main

# 4. Create a Git tag for the release (opcional pero recomendado)
git tag -a v0.2.0 -m "Release: Milestone 2 (Stream Processing)"
git push origin v0.2.0

# 5. Return to develop to prepare for M3
git checkout develop
```
