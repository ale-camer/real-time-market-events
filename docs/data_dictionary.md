# Data Dictionary

## Overview
Este documento detalla la estructura y propósito de los principales eventos, esquemas de datos y tablas utilizados a lo largo del pipeline de **Real-Time Market Events**.

---

## 1. Eventos Crudos (Raw Events)
Generados por los extractores y enviados a Kafka bajo los tópicos `market.crypto`, `market.stocks` y `market.forex`.

### BaseMarketEvent
| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `event_id` | `UUID (String)` | Identificador único del evento. | `123e4567-e89b-12d3-a456-426614174000` |
| `asset_class` | `Enum (String)` | Clase de activo (`crypto`, `stocks`, `forex`). | `crypto` |
| `symbol` | `String` | Par o símbolo original del exchange/fuente. | `BTC-USD` |
| `price` | `Float` | Precio del activo en el momento del evento (> 0). | `60000.5` |
| `volume` | `Float` | Volumen transaccionado (>= 0). | `1.5` |
| `timestamp` | `Float` | UNIX Timestamp exacto de la operación. | `1712499632.123` |
| `source` | `String` | Fuente de origen de los datos. | `coingecko` |

---

## 2. Eventos Enriquecidos y Normalizados
Consumidos por Faust. El Worker los transforma para estandarizar símbolos.

### EnrichedEvent
Mismos campos que `BaseMarketEvent` pero incluye un campo extra con el par normalizado para evitar colisiones entre distintos exchanges.

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `normalized_symbol` | `String` | Símbolo normalizado (e.g. BTC/USD). | `BTC/USD` |

---

## 3. Agregaciones (OHLCV)
Métricas calculadas por Faust en ventanas temporales estáticas (Tumbling Windows de 1 minuto) y guardadas en TimescaleDB.

### OHLCV Event
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `symbol` | `String` | Símbolo normalizado (ej. `BTC/USD`). |
| `timestamp` | `Float` | UNIX Timestamp marcando el inicio de la ventana. |
| `open` | `Float` | Precio al inicio de la ventana temporal. |
| `high` | `Float` | Precio máximo alcanzado en la ventana temporal. |
| `low` | `Float` | Precio mínimo alcanzado en la ventana temporal. |
| `close` | `Float` | Precio al cierre de la ventana temporal (último evento). |
| `volume` | `Float` | Sumatoria total del volumen transaccionado en la ventana. |

---

## 4. Detección de Anomalías
Eventos generados cuando Faust detecta variaciones extremas inter-evento (> 2%) y emitidos al tópico `market.alerts`.

### PriceAnomalyAlert
| Campo | Tipo | Descripción |
|-------|------|-------------|
| `symbol` | `String` | Par normalizado que disparó la alerta. |
| `timestamp` | `Datetime` | Marca de tiempo del evento que desencadenó el trigger. |
| `previous_price` | `Float` | Precio anterior guardado en estado (Faust Table). |
| `current_price` | `Float` | Precio actual anómalo. |
| `percentage_change`| `Float` | % de salto de precio entre previous y current. |
| `alert_type` | `String` | `"PUMP"` si subió, `"DUMP"` si bajó. |

---

## 5. TimescaleDB (Base de Datos Relacional de Series Temporales)
Las tablas principales creadas por las migraciones de Alembic:

### Tabla `market_events` (Hypertable)
Almacena los eventos crudos normalizados.
- `id` (Integer, Primary Key)
- `event_id` (String, Indexado)
- `symbol` (String, Indexado)
- `price` (Numeric/Float)
- `volume` (Numeric/Float)
- `timestamp` (Timestamp with Timezone, Partition Key)

### Tabla `market_metrics` (Hypertable)
Almacena los registros agregados OHLCV.
- `id` (Integer, Primary Key)
- `symbol` (String, Indexado)
- `window_start` (Timestamp with Timezone, Partition Key)
- `open` (Numeric/Float)
- `high` (Numeric/Float)
- `low` (Numeric/Float)
- `close` (Numeric/Float)
- `volume` (Numeric/Float)
