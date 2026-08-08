# Development Plan — Issue #16: Docker Compose (M4)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-16-docker-compose`  
**Milestone:** M4 — Dockerization & Observability  
**GitHub Issue:** [#16](https://github.com/ale-camer/real-time-market-events/issues/16)

---

## Objective

El objetivo del **Milestone 4** es llevar nuestro proyecto desde un entorno local dependiente (venv, docker run manual) hacia una infraestructura completamente orquestada y empaquetada con **Docker**. En este Issue #16 vamos a crear el archivo `Dockerfile` para nuestras aplicaciones Python y el `docker-compose.yml` maestro que levantará toda la arquitectura en un solo comando: Kafka, Zookeeper, TimescaleDB, Faust Agents, Data Producers y la API de FastAPI. 

---

## Step 0 — Activate venv & Create Feature Branch

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Ensure you are on develop and up to date
git checkout develop
git pull origin develop

# 2. Create and switch to feature branch
git checkout -b feature/issue-16-docker-compose

# 3. Link branch to GitHub Issue #16
gh issue develop 16 --checkout
# If already created, push manually:
git push -u origin feature/issue-16-docker-compose
```

---

## Step 1 — Crear el Dockerfile Base

Necesitamos un único `Dockerfile` en la raíz del proyecto que servirá para todos nuestros servicios Python (API, Faust, Productor), instalando el código fuente y las dependencias vía pip/Poetry. Cada servicio luego sobrescribirá el `command` en el `docker-compose.yml`.

**Requirements:**
1. Crear un archivo `Dockerfile` en la raíz.
2. Usar una imagen base ligera como `python:3.14-slim`.
3. Instalar dependencias del sistema requeridas para compilar librerías (ej. `gcc`, `libpq-dev`).
4. Copiar los archivos de requerimientos y ejecutar `pip install`.
5. Copiar el resto del código (`src/`, `alembic/`, `alembic.ini`, etc.).

---

## Step 2 — Escribir el `docker-compose.yml`

El archivo Compose debe levantar toda la infraestructura y establecer dependencias (`depends_on`) claras, además de variables de entorno consistentes.

**Requirements:**
1. Crear `docker-compose.yml` en la raíz.
2. **Servicios de Infraestructura:**
   - `zookeeper`: Usar imagen `bitnami/zookeeper`.
   - `kafka`: Usar imagen `bitnami/kafka` conectado a Zookeeper. Crear automáticamente el topic `market.crypto`.
   - `timescaledb`: Usar `timescale/timescaledb:latest-pg14`.
   - `kafka-ui` (Opcional): Para monitorear el broker localmente.
3. **Servicios de Aplicación** (usando `build: .` y distintos comandos):
   - `api`: Corre `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`. Depende de la DB y Kafka.
   - `faust-worker`: Corre `faust -A src.consumers.agents worker -l info`.
   - `producer`: Corre el script principal de extracción o cron (ej. `python -m src.producers.kafka_producer`).
4. Configurar las variables de entorno (`KAFKA_BROKER_URL`, `DATABASE_URL`) compartidas en un archivo `.env` o definidas explícitamente en el yaml.

---

## Step 3 — Escribir Makefile (Opcional) y Documentar

Facilitar el uso de la arquitectura.

**Requirements:**
1. Actualizar el `README.md` con la instrucción principal de ejecución (`docker-compose up -d --build`).
2. (Opcional) Agregar comandos rápidos al `Makefile` para levantar, apagar, y ver logs.

---

## Step 4 — Probar la Orquestación Local

Asegurarnos de que el stack levante sin errores.

**Verify:**
```bash
# Levantar el entorno
docker compose up --build -d

# Ver logs de un servicio (ej. API)
docker compose logs -f api

# Bajar el entorno
docker compose down -v
```

---

## Step 5 — Commit, Push y Merge a Develop

Cerramos oficialmente el Issue #16 incorporándolo a `develop`.

```bash
# Stage changes
git add Dockerfile docker-compose.yml README.md docs/issue_16_plan.md

# Commit
git commit -m "feat(infra): create Dockerfile and docker-compose for full stack (#16)"

# Push and PR
git push origin feature/issue-16-docker-compose

gh pr create \
  --title "feat(infra): Docker Compose Setup (#16)" \
  --body "Closes #16. Implementa orquestación local completa con Kafka, Zookeeper, TimescaleDB, Faust y FastAPI." \
  --base develop \
  --head feature/issue-16-docker-compose

# Merge PR and cleanup
gh pr merge --squash --delete-branch
gh issue close 16
git checkout develop
git pull origin develop
```
