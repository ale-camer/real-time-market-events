# Plan: GitHub Actions CI (Issue #19)

## Objective
Implementar un pipeline de Integración Continua (CI) utilizando GitHub Actions para automatizar las validaciones de calidad de código: linting, type checking, y ejecución de tests unitarios con reporte de cobertura.

## Context
Como parte del hito M4 (Observabilidad & CI/CD), es fundamental asegurar que cada cambio propuesto mediante un Pull Request cumpla con los estándares del proyecto antes de ser integrado. Hasta ahora veníamos corriendo `ruff`, `mypy` y `pytest` localmente. Vamos a delegar esta responsabilidad a GitHub Actions para tener un proceso formal, profesional y auditable.

---

## Step 0 — Activar entorno y crear rama

```bash
# 1. Activar entorno virtual
source .venv/bin/activate

# 2. Posicionarse en develop
git checkout develop
git pull origin develop

# 3. Crear rama del issue
git checkout -b feature/issue-19-github-actions
```

---

## Step 1 — Crear el Workflow de GitHub Actions

Necesitamos definir el archivo YAML que le indicará a GitHub qué pasos ejecutar.

**Requirements:**
1. Crear el directorio `.github/workflows/` en la raíz del proyecto (si no existe).
2. Crear un archivo llamado `ci.yml` dentro de ese directorio.
3. El workflow debe reaccionar a:
   - Eventos `push` en las ramas `main` y `develop`.
   - Eventos `pull_request` dirigidos a las ramas `main` y `develop`.
4. Definir un job (ej. `build-and-test`) que corra sobre `ubuntu-latest`.
5. Los pasos del job deben ser:
   - Hacer checkout del código (`actions/checkout@v4`).
   - Configurar Python 3.11 (`actions/setup-python@v5`).
   - Instalar las dependencias del proyecto incluyendo las de desarrollo (`pip install -e ".[dev]"`).
   - Ejecutar el chequeo de formato y linting con Ruff (`ruff check .` y `ruff format --check .`).
   - Ejecutar el análisis estático de tipos con MyPy (`mypy src/ tests/`).
   - Ejecutar los tests unitarios con Pytest, generando un reporte de cobertura (`pytest tests/ --cov=src --cov-report=term-missing`).

**Controls:**
```bash
mkdir -p .github/workflows
touch .github/workflows/ci.yml
```

---

## Step 2 — Validación Local Preliminar

Antes de subir los cambios a GitHub, es buena práctica asegurarse de que el código actual pasa todas las validaciones, para que el primer run de Actions no falle de inmediato por errores que ya teníamos.

**Requirements:**
1. Ejecutar localmente todos los comandos que va a correr el CI.
2. Asegurar de que no queden errores sueltos (como hemos hecho en los pasos anteriores).

**Controls:**
```bash
ruff check .
ruff format --check .
mypy .
pytest tests/
```

---

## Step 3 — Commitear, Subir y Validar en GitHub

Una vez configurado el archivo, lo subimos y dejamos que GitHub Actions haga su magia.

**Requirements:**
1. Hacer commit del nuevo archivo `ci.yml`.
2. Pushear la rama.
3. Crear el Pull Request.
4. **IMPORTANTE:** Ir a la pestaña "Actions" en el repositorio de GitHub (o mirar los checks en el PR) y verificar que el workflow se dispara correctamente, instala dependencias y pasa todos los pasos en verde.

**Controls:**
```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions workflow for linting, typing and testing"
git push origin feature/issue-19-github-actions

gh pr create --base develop --head feature/issue-19-github-actions --title "ci: GitHub Actions Pipeline" --body "Closes #19"
```

---

## Step 4 — Merge y Cierre del Issue

Una vez que comprobaste en la interfaz de GitHub que el check pasó exitosamente, procedemos a finalizar el issue.

```bash
# Integrar el PR a develop
gh pr merge --squash --delete-branch

# Cerrar el issue
gh issue close 19

# Volver a la rama base
git checkout develop
git pull origin develop
```
