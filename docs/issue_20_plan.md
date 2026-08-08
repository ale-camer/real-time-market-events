# Plan: Documentación Final (Issue #20)

## Objective
Finalizar la documentación técnica del proyecto creando/actualizando los documentos clave: `architecture.md`, `data_dictionary.md` y actualizar el `README.md` general para reflejar el estado productivo del sistema.

## Context
Este es el último issue del hito M4 (Observabilidad & CI/CD) y del proyecto en su etapa inicial. Un proyecto no está terminado si no se puede entender, mantener y desplegar. Necesitamos que los reclutadores u otros desarrolladores puedan comprender fácilmente la arquitectura, el modelo de datos y cómo levantar el proyecto localmente.

---

## Step 0 — Activar entorno y crear rama

```bash
# 1. Posicionarse en develop y actualizar
git checkout develop
git pull origin develop

# 2. Crear rama del issue
git checkout -b feature/issue-20-final-docs
```

---

## Step 1 — Actualizar README.md

El `README.md` es la carta de presentación. Debemos asegurarnos de que la sección de *Quick Start* esté completa y refleje exactamente cómo levantar el proyecto utilizando Docker Compose.

**Requirements:**
1. Revisar y actualizar la arquitectura en texto/ascii si hubo cambios.
2. Completar la sección de *Quick Start* con los comandos reales:
   - Clonar repositorio.
   - Creación de entorno virtual e instalación (`pip install -e ".[dev]"`).
   - Variables de entorno (`.env.example` -> `.env`).
   - Inicialización de servicios (`docker compose up -d`).
   - Comando para correr migraciones de BD si no están automatizadas.
   - Scripts para encender extractores/productores de Kafka.
   - Comando para correr el worker de Faust.
   - Comando para levantar la API de FastAPI.

**Controls:**
- Lectura manual del archivo y verificación de que los comandos listados efectivamente funcionen (simular en la mente o en una terminal limpia).

---

## Step 2 — Redactar architecture.md

Crear un documento que explique en profundidad las decisiones técnicas.

**Requirements:**
1. Crear/Modificar `docs/architecture.md`.
2. Incluir diagrama de arquitectura (puede ser Mermaid o texto).
3. Explicar el flujo de datos: Extracción -> Kafka -> Faust -> TimescaleDB -> FastAPI -> Grafana.
4. Documentar los principales ADRs (Architecture Decision Records) o decisiones de diseño (por ejemplo, ¿por qué Faust y no Spark?, ¿por qué TimescaleDB y no InfluxDB?).

---

## Step 3 — Redactar data_dictionary.md

Documentar los esquemas y las métricas calculadas.

**Requirements:**
1. Crear/Modificar `docs/data_dictionary.md`.
2. Listar y explicar el formato de los eventos crudos (`Market Event`).
3. Listar y explicar los eventos enriquecidos y las agregaciones de ventanas (OHLCV).
4. Listar la estructura principal de las tablas/hypertables en TimescaleDB.

---

## Step 4 — Commitear, Subir y Merge

**Controls:**
```bash
ruff check .
ruff format --check .
mypy .
pytest tests/
```

Una vez que todo esté en verde y los documentos redactados:

```bash
git add README.md docs/
git commit -m "docs: finalize project documentation (architecture, data dict, readme)"
git push origin feature/issue-20-final-docs

gh pr create --base develop --head feature/issue-20-final-docs --title "docs: Final Documentation" --body "Closes #20"
# Esperar que pase el CI en GitHub Actions
gh pr merge --squash --delete-branch
gh issue close 20

git checkout develop
git pull origin develop

# Al ser el final del hito M4 y tener la versión estable, integramos develop a main
git checkout main
git pull origin main
git merge develop -m "chore: release version 1.0 (M4 complete)"
git push origin main
git checkout develop
```
