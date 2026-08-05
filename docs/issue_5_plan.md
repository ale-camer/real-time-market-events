# Development Plan — Issue #5: Unit Tests — Extractors and Schemas (M1)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-5-unit-tests`  
**Milestone:** M1 — Ingestion & Kafka  
**GitHub Issue:** [#5](https://github.com/ale-camer/real-time-market-events/issues/5)

---

## Objective

Write and consolidate a comprehensive suite of **unit tests** for all data extractors (CoinGecko WebSocket, Polygon.io HTTP REST), event schemas (Pydantic v2 & Avro), and the Kafka producer (`aiokafka`/`KafkaProducer`). Ensure clean mocks for external dependencies (network/sockets/broker) and achieve a minimum **test coverage of 80%** across the `src/` module.

---

## Step 0 — Activate venv & Create Feature Branch

> Always do this before touching any code.

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# Verify it's active
which python   # should point to .venv/bin/python
python --version  # should be 3.11.x or 3.14.x
```

```bash
# 2. Make sure you are on develop and up to date
git checkout develop
git pull origin develop

# 3. Create and switch to feature branch
git checkout -b feature/issue-5-unit-tests

# 4. Link branch to GitHub Issue #5
gh issue develop 5 --checkout
# If already created, push manually:
git push -u origin feature/issue-5-unit-tests
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-5-unit-tests
gh issue view 5             # should show issue #5 details
```

---

## Step 1 — Configure Testing Stack & Mocks (`pyproject.toml`)

Verify that the testing dependencies are installed and properly configured in `pyproject.toml`:
- `pytest`
- `pytest-asyncio`
- `pytest-cov`
- `respx` (for mocking HTTP requests from `httpx`)

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installations
pytest --version
python -c "import respx; print(respx.__version__)"
```

---

## Step 2 — Pydantic & Avro Schema Tests (`tests/unit/schemas/test_schemas.py`)

Ensure coverage for validation, model conversion, and Avro serialization.

**Test cases to cover in `tests/unit/schemas/test_schemas.py`:**
1. Correct instantiation of `CryptoEvent`, `StockEvent`, and `ForexEvent`.
2. Type and range validation (price <= 0, volume < 0, empty or malformed symbols).
3. Timestamp conversion and ISO format parsing.
4. Binary Avro serialization and deserialization (`serialize_avro` and `deserialize_avro`).
5. Exception handling when deserializing corrupt bytes.

**Run tests:**
```bash
pytest tests/unit/schemas/test_schemas.py -v
```

---

## Step 3 — CoinGecko WebSocket Extractor Tests (`tests/unit/extractors/test_coingecko.py`)

Test the logic of the synchronous/asynchronous CoinGecko extractor by mocking the network socket.

**Test cases to cover:**
1. Successful connection and reception of price/ticker messages in JSON format.
2. Transformation of raw CoinGecko JSON into `CryptoEvent` (Pydantic).
3. Handling of disconnections, automatic reconnections, or timeouts.
4. Handling of malformed or unrecognized messages (without crashing the application).

**Run tests:**
```bash
pytest tests/unit/extractors/test_coingecko.py -v
```

---

## Step 4 — Polygon.io WebSocket Extractor Tests (`tests/unit/extractors/test_polygon.py`)

Test the logic of the asynchronous Polygon.io extractor by mocking the network WebSocket.

**Test cases to cover:**
1. Successful connection, authentication, and reception of market messages -> Conversion to `StockEvent` / `ForexEvent`.
2. Handling of authentication errors (Missing API Key).
3. Handling of disconnections, automatic reconnections, and exponential backoff (`ConnectionClosedError`).
4. Proper graceful shutdown (`shutdown()`).

**Run tests:**
```bash
pytest tests/unit/extractors/test_polygon.py -v
```

---

## Step 5 — Kafka Producer Tests (`tests/unit/producers/test_kafka_producer.py`)

Verify event publishing without requiring a real Kafka cluster running locally.

**Test cases to cover:**
1. Initialization and start/stop of the `KafkaProducer` client.
2. Mocking of `AIOKafkaProducer.send_and_wait` or `send`.
3. Verification of the target topic based on the asset class (`market.crypto`, `market.stocks`, `market.forex`).
4. Verification that the sent payload matches the Avro serialized bytes.
5. Handling of publishing failures (e.g., KafkaTimeoutError or KafkaConnectionError) and retry policies.

**Run tests:**
```bash
pytest tests/unit/producers/test_kafka_producer.py -v
```

---

## Step 6 — Full Lint & Type Check Pass

Run full project checks to ensure code quality and coverage metric (80%).

```bash
# Linting & Formatting
ruff check src/ tests/
ruff format src/ tests/

# Static type analysis
mypy src/ tests/

# Full test suite with coverage report
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

All checks must pass (coverage ≥ 80%).

---

## Step 7 — Commit, Push & Open PR

```bash
# Stage new files
git add tests/ docs/issue_5_plan.md pyproject.toml

# Commit
git commit -m "test(m1): implement unit tests for extractors, schemas, and kafka producer (#5)

- Adds unit tests for CoinGecko WebSocket extractor with socket mocks
- Adds unit tests for Polygon REST extractor using respx HTTP mocks
- Expands tests for Pydantic v2 models and Avro serialization/deserialization
- Adds unit tests for Kafka producer event publishing with mocked broker
- Ensures >=80% test coverage across src/ modules"

# Push branch
git push origin feature/issue-5-unit-tests
```

Open Pull Request:
```bash
gh pr create \
  --title "test(m1): Unit tests for extractors, schemas, and Kafka producer (#5)" \
  --body "Closes #5. Adds unit testing coverage with mocks for CoinGecko, Polygon, Schemas, and Kafka Producer." \
  --base develop \
  --head feature/issue-5-unit-tests
```

---

## Step 8 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 5 --comment "Implemented via PR — all M1 unit tests added with >=80% coverage."

# Sync local develop
git checkout develop
git pull origin develop
```

**Verify issue is closed:**
```bash
gh issue list       # #5 should no longer appear
gh issue view 5     # status: CLOSED
```

---

## Step 9 — Release Milestone 1 to Main

Since this issue completes Milestone 1, promote `develop` to `main`.

```bash
# Open Release PR
gh pr create \
  --title "release: Milestone 1 - Ingestion & Kafka" \
  --body "Promotes completed M1 features (Schemas, Extractors, Kafka Producer, and Unit Tests) from develop to main." \
  --base main \
  --head develop

# Merge Release PR
gh pr merge --merge --delete-branch=false

# Sync local branches
git checkout main
git pull origin main
git checkout develop
```

---

## Acceptance Criteria

- [ ] Unit tests for the CoinGecko extractor using a WebSocket mock (`websockets` / `unittest.mock`).
- [ ] Unit tests for the Polygon.io extractor using a WebSocket mock (`websockets` / `unittest.mock`).
- [ ] Comprehensive unit tests for Pydantic v2 and Avro schemas (valid, edge cases, and invalid payloads).
- [ ] Unit tests for the Kafka Producer using broker mocks.
- [ ] Global test coverage for Milestone 1 is ≥ 80%.
- [ ] Code is clean, passing `ruff` (linter + formatter) and static typing verification with `mypy` without errors.
