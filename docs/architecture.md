# System Architecture

## Overview
El proyecto "Real-Time Market Events Stream" implementa un pipeline de datos robusto y de baja latencia para la ingesta, procesamiento y visualización de datos de mercado (criptomonedas, forex y acciones).

La arquitectura está dividida en cuatro etapas principales: Ingesta (M1), Stream Processing (M2), Persistencia y API (M3), y Observabilidad (M4).

## Architecture Diagram

```mermaid
flowchart TD
    %% Fuentes de datos
    subgraph Data_Sources [Fuentes de Datos Externas]
        CG(CoinGecko WS)
        Poly(Polygon.io WS)
    end

    %% Ingesta
    subgraph Ingestion [M1 - Ingestion Layer]
        Ex(Extractores Asíncronos)
        KP(Kafka Producer)
        Ex -->|Dict| KP
    end

    %% Mensajería
    subgraph Broker [M1 - Message Broker]
        K[Apache Kafka]
    end

    %% Stream Processing
    subgraph Processing [M2 - Stream Processing (Faust)]
        FW(Faust Worker)
        FW -->|Normalización| FW
        FW -->|Enriquecimiento OHLCV| FW
        FW -->|Anomaly Detection| FW
    end

    %% Persistencia
    subgraph Storage [M3 - Storage Layer]
        TDB[(TimescaleDB)]
    end

    %% Consumo
    subgraph Consumption [M3 & M4 - Consumption Layer]
        API(FastAPI REST/WS)
        Grafana(Grafana Dashboards)
    end

    Data_Sources -->|WebSockets| Ingestion
    KP -->|Produce (Avro/JSON)| Broker
    Broker -->|Consume| Processing
    Processing -->|Consume/Produce| Broker
    Processing -->|Inserts (asyncpg)| Storage
    Storage -->|Queries| API
    Storage -->|Queries| Grafana
```

## Component Details

### 1. Ingestion Layer (Extractors & Producers)
- **Tecnologías:** `websockets`, `confluent-kafka`, `pydantic`.
- **Descripción:** Módulos asíncronos en Python que se conectan a APIs por WebSockets (CoinGecko, Polygon). Los datos extraídos se validan mediante esquemas de Pydantic y luego se publican en Apache Kafka utilizando un `EventProducer` construido sobre `confluent-kafka`.
- **Resiliencia:** Backoff exponencial y reconexión automática frente a caídas del WebSocket.

### 2. Message Broker (Apache Kafka)
- **Tecnologías:** Confluent Kafka, Zookeeper.
- **Descripción:** Funciona como el buffer central e intermediario desacoplado del sistema. Permite a los extractores inyectar datos a alta velocidad sin preocuparse de si el procesamiento posterior o la base de datos están saturados.
- **Tópicos:**
  - `market.crypto`, `market.stocks`, `market.forex` (Raw events).
  - `market.alerts` (Anomalías detectadas).

### 3. Stream Processing (Faust)
- **Tecnologías:** Faust-Streaming.
- **Descripción:** Un worker de Faust lee los eventos crudos desde Kafka. 
- **Responsabilidades:**
  - **Normalización:** Convierte los distintos formatos (ej. formato CoinGecko vs Polygon) en un formato canónico `EnrichedEvent`.
  - **Agregaciones (OHLCV):** Agrupa transacciones en ventanas de tiempo (ej. 1 minuto) para calcular Apertura, Cierre, Máximo, Mínimo y Volumen.
  - **Detección de anomalías:** Mantiene en memoria (`faust.Table`) el último precio conocido de cada símbolo. Si un nuevo evento tiene un salto de precio mayor al 2%, emite una alerta al tópico `market.alerts`.

### 4. Storage & API (TimescaleDB + FastAPI)
- **Tecnologías:** TimescaleDB (PostgreSQL), `asyncpg`, FastAPI.
- **Descripción:**
  - **TimescaleDB:** Base de datos elegida específicamente para series temporales. Utiliza *hypertables* particionadas por tiempo para lograr una inserción y consulta ultra-rápida.
  - **FastAPI:** Interfaz de consumo que provee endpoints REST (`/api/v1/events`, `/api/v1/metrics`) para consultar el histórico de precios y volumen de forma estandarizada.

### 5. Observability (Grafana)
- **Tecnologías:** Grafana.
- **Descripción:** Se conecta de manera directa a TimescaleDB utilizando el plugin de PostgreSQL. Permite visualizar paneles en tiempo real de los precios de mercado, métricas agregadas y disparos de alertas generadas por el agente de Faust.

## Architecture Decision Records (ADRs)

1. **¿Por qué Apache Kafka y no RabbitMQ/Redis PubSub?**
   - El mercado financiero genera picos masivos de eventos por segundo (throughput alto). Kafka persiste los mensajes a disco secuencialmente, asegurando que si los workers de procesamiento (Faust) fallan, puedan retomar desde el *offset* donde dejaron, sin perder ni un evento.

2. **¿Por qué Faust-Streaming en lugar de Spark/Flink?**
   - Faust está escrito íntegramente en Python y utiliza `asyncio`. Al tratarse de un pipeline que se integra fuertemente con otras librerías de Python (como Pydantic y FastAPI), Faust proporciona una curva de aprendizaje baja, excelente tipado dinámico y un footprint en memoria ligero para levantar workers distribuidos.

3. **¿Por qué TimescaleDB sobre PostgreSQL vanilla o InfluxDB?**
   - Las operaciones principales sobre estos datos incluyen consultas sobre rangos de tiempo e inserciones masivas. TimescaleDB ofrece soporte SQL estándar (con el que trabajamos usando SQLAlchemy/asyncpg) combinado con optimizaciones subyacentes de partición y retención propias de una Time-Series Database, sin introducir la complejidad de un lenguaje query no-estándar (como Flux de InfluxDB).
