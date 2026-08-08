# Plan: Grafana Dashboards (Issue #17)

## Objective
Añadir capacidades de observabilidad y visualización de datos integrando Grafana al entorno Dockerizado, proveyendo dashboards pre-configurados para analizar eventos de mercado y la salud del pipeline.

## Context
En el Issue #16, toda la infraestructura base (Kafka, Zookeeper, TimescaleDB, Faust Worker, API, Producer) fue orquestada y dockerizada exitosamente en un único `docker-compose.yml`. Ahora que la data en tiempo real fluye y se persiste, necesitamos conectar Grafana a TimescaleDB para visualizar el OHLCV (velas) de cryptos, stocks y forex, junto con métricas de salud o latencia.

---

## Step 0 — Activar entorno y crear rama

Como siempre, preparamos nuestro espacio de trabajo de manera ordenada:

```bash
# 1. Activar el entorno virtual
source .venv/bin/activate

# 2. Asegurarse de estar en la rama develop y actualizados
git checkout develop
git pull origin develop

# 3. Crear una nueva rama para este issue
git checkout -b feature/issue-17-grafana-dashboards
```

---

## Step 1 — Modificar `docker-compose.yml` para incluir Grafana

El servicio de Grafana debe ser añadido al stack y depender de la base de datos para funcionar correctamente.

**Requirements:**
1. Añadir el servicio `grafana` en `docker-compose.yml`.
2. Usar la imagen oficial estable, por ejemplo `grafana/grafana-oss:10.4.0` (o similar).
3. Mapear el puerto `3000:3000` al host.
4. Definir un volumen con nombre (`grafana_data`) para la persistencia de datos (usuarios, sesiones).
5. Montar volúmenes locales (bind mounts) para el **provisioning** automático de *Datasources* y *Dashboards*.
6. Configurar variables de entorno iniciales (por ejemplo, `GF_SECURITY_ADMIN_PASSWORD=admin`).
7. Añadir `depends_on: timescaledb`.

---

## Step 2 — Configurar Auto-Provisioning del Datasource (TimescaleDB)

No queremos que el usuario tenga que entrar y crear la conexión a la base de datos manualmente cada vez que borra los volúmenes. Grafana soporta aprovisionamiento automático mediante archivos YAML.

**Requirements:**
1. Crear el directorio `infra/grafana/provisioning/datasources/`.
2. Escribir un archivo `timescaledb.yaml` (o `postgres.yml`) que defina la conexión:
   - **Type**: `postgres`
   - **URL**: `timescaledb:5432`
   - **Database / User / Password**: Las mismas credenciales definidas en el servicio de Timescale.
   - **TimescaleDB Option**: Asegurarse de activar el flag de TimescaleDB en la configuración (usualmente en `jsonData.timescaledb: true`).

---

## Step 3 — Configurar Provisioning de Dashboards y Creación Inicial

De igual manera, los tableros que armemos deben ser inyectados automáticamente al levantar el contenedor.

**Requirements:**
1. Crear el directorio `infra/grafana/provisioning/dashboards/`.
2. Crear un archivo `default.yaml` que le indique a Grafana dónde encontrar los archivos JSON de los dashboards (por ejemplo, apuntando al volumen `/var/lib/grafana/dashboards` dentro del contenedor).
3. Crear el directorio raíz para los JSON: `infra/grafana/dashboards/`.
4. (Opcional en código) Proveer un JSON `market_overview.json` básico. En la práctica, es más fácil entrar a Grafana, armar el tablero visualmente con queries de SQL, exportarlo a JSON y guardarlo en esta carpeta.

---

## Step 4 — Probar y Armar Consultas SQL de Visualización

Una vez levantado todo, se debe probar el acceso y las visualizaciones.

**Requirements:**
1. Levantar con `make build` (o `docker compose up -d`).
2. Entrar a `http://localhost:3000` (admin/admin).
3. Verificar que el Datasource de PostgreSQL esté funcionando.
4. Crear gráficas para:
   - **Precio de Cierre (Close)**: Gráfico de líneas o velas en el tiempo para `crypto_ohlcv_1m`.
   - **Volumen**: Gráfico de barras inferior.
5. Exportar el dashboard y guardarlo en el repositorio local.

---

## Step 5 — Commitear, PR y Merge

```bash
# Formateo general (si modificaste algún archivo .py accidentalmente)
ruff check . --fix && ruff format .

git add .
git commit -m "feat: integrate grafana and provision timescaledb datasource"
git push origin feature/issue-17-grafana-dashboards

# Crear PR, mergear y limpiar rama (con Github CLI o interfaz web)
gh pr create --title "feat: Grafana Observability Dashboards" --body "Closes #17"
gh pr merge --squash --delete-branch
gh issue close 17
```
