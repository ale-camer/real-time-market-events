# Plan: Alertas & Anomaly Detection (Issue #18)

## Objective
Implementar un sistema de detección de anomalías en tiempo real para identificar variaciones bruscas de precio (ej. caídas o subidas mayores a un X% inter-evento) y emitir alertas automáticas.

## Context
Actualmente nuestro pipeline procesa y almacena los eventos (Producer -> Kafka -> Faust -> TimescaleDB) y Grafana nos permite observarlos (Issue #17). Sin embargo, un buen sistema de datos en tiempo real no solo almacena, sino que reacciona. Vamos a aprovechar las capacidades de Stream Processing de nuestro worker (Faust) para agregar un agente que analice variaciones de precio en vivo, detecte anomalías (Pumps o Dumps) y emita alertas.

---

## Step 0 — Activar entorno y crear rama

```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Posicionarse en develop
git checkout develop
git pull origin develop

# 3. Crear rama del issue
git checkout -b feature/issue-18-anomaly-detection
```

---

## Step 1 — Definir Modelos y Tópicos para las Alertas

Necesitamos una estructura clara para saber qué es una alerta y a dónde enviarla.

**Requirements:**
1. En tu módulo de esquemas (`src/schemas/events.py` o en un nuevo `src/schemas/alerts.py`), crear un modelo Pydantic `PriceAnomalyAlert` con:
   - `symbol` (str)
   - `timestamp` (datetime)
   - `previous_price` (float)
   - `current_price` (float)
   - `percentage_change` (float)
   - `alert_type` (str) -> Ej: `"PUMP"`, `"DUMP"`.
2. En la configuración de Kafka (donde definiste los tópicos), definir un nuevo tópico llamado `price_alerts`.

**Controls:**
```bash
mypy src/schemas/
```

---

## Step 2 — Desarrollar el Agente de Detección (Faust)

Aquí ocurre la lógica de negocio en tiempo real. 

**Requirements:**
1. Modificar `src/consumers/agents.py` (o crear `anomaly_agent.py`) y definir un nuevo agente (`@app.agent(market_events_topic)`).
2. El agente procesará la misma corriente de eventos que el guardado en base de datos.
3. Lógica de Detección:
   - Necesitamos recordar el último precio de cada símbolo. Faust soporta Tablas en memoria (o podés usar un simple `dict` a nivel de módulo temporalmente si solo corre un worker).
   - Por cada evento, recuperar el precio anterior del `symbol`.
   - Calcular la variación porcentual: `change = ((current_price - prev_price) / prev_price) * 100`.
   - Si `abs(change) >= THRESHOLD` (ej. `2.0` %), construir el objeto `PriceAnomalyAlert`.
4. Una vez construida la alerta, enviarla (produce) al tópico `price_alerts` y escribir un log llamativo (ej. `logger.warning(f"🚨 ANOMALY: {symbol} dropped by {change}%")`).

**Controls:**
```bash
mypy src/consumers/
```

---

## Step 3 — Tests Unitarios

Garantizar que la matemática y la lógica de detección funcionan.

**Requirements:**
1. Crear (o editar) un archivo en `tests/consumers/test_anomaly_agent.py`.
2. Escribir tests que simulen la llegada de dos eventos consecutivos para el mismo símbolo.
3. **Test Positivo**: El precio salta 5%, asegurar que se llama a la función de enviar alerta.
4. **Test Negativo**: El precio salta 0.5%, asegurar que la alerta es ignorada.

**Controls:**
```bash
pytest tests/consumers/test_anomaly_agent.py -v
```

---

## Step 4 — Verificación Funcional (E2E)

Probar en el entorno dockerizado que todo fluye.

**Requirements:**
1. Levantar la infraestructura: `make build` o `docker compose up -d`.
2. Ver los logs en vivo del worker: `docker compose logs -f faust-worker`.
3. Iniciar el producer y esperar a ver si salta alguna alerta aleatoria.
4. *(Opcional)* Para forzar una alerta, podés editar el Producer temporalmente para que en un evento mande un multiplicador `* 1.5` en el precio y ver si el Faust Worker captura la anomalía e imprime el log de 🚨.

**Controls:**
```bash
make build
make logs
```

---

## Step 5 — Commitear, PR y Merge

```bash
# Formateo, linting y type checking
ruff check . --fix && ruff format .
mypy .
pytest tests/

# Comitear y pushear
git add .
git commit -m "feat: real-time price anomaly detection agent with Faust"
git push origin feature/issue-18-anomaly-detection

# PR y merge
gh pr create --base develop --title "feat: Price Anomaly Detection" --body "Closes #18"
gh pr merge --squash --delete-branch
gh issue close 18

# Volver a develop
git checkout develop
git pull origin develop
```
