# Development Plan — Issue #4: Pydantic v2 & Avro Event Schemas

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-4-event-schemas`  
**Milestone:** M1 — Ingestion & Kafka  
**GitHub Issue:** [#4](https://github.com/ale-camer/real-time-market-events/issues/4)

---

## Objective

Define strongly-typed event schemas for market events (crypto, stocks, forex) using Pydantic v2 and Apache Avro (`fastavro`). Ensure raw events ingested by extractors are validated, normalized into standard data models, and can be serialized to / deserialized from Avro binary format for high-performance streaming through Kafka.

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
git checkout -b feature/issue-4-event-schemas

# 4. Link branch to GitHub Issue #4
gh issue develop 4 --checkout
# If already created, push manually:
git push -u origin feature/issue-4-event-schemas
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-4-event-schemas
gh issue view 4             # should show issue #4 details
```

---

## Step 1 — Uncomment & Install Dependencies

Edit `pyproject.toml` to uncomment `fastavro`:

```toml
# pyproject.toml → [project] dependencies
"fastavro>=1.9.0",
```

Then install:
```bash
pip install -e ".[dev]"
```

**Verify:**
```bash
pip show fastavro
python -c "import fastavro; print(fastavro.__version__)"
```

---

## Step 2 — Implement Pydantic V2 Schemas (`src/schemas/market_event.py`)

Create `src/schemas/market_event.py` containing:
- `AssetClass` (Enum: `CRYPTO`, `STOCKS`, `FOREX`).
- `BaseMarketEvent` (Pydantic V2 model with fields: `event_id`, `asset_class`, `symbol`, `price`, `volume`, `timestamp`, `source`).
- Specific event models (`CryptoEvent`, `StockEvent`, `ForexEvent`) extending `BaseMarketEvent` with custom field validators (e.g. positive price/volume, non-empty symbol, ISO timestamp format/unix epoch timestamp handling).

**Lint & Type Check:**
```bash
ruff check src/schemas/market_event.py --fix
ruff format src/schemas/market_event.py
mypy src/schemas/market_event.py
```

---

## Step 3 — Implement Avro Schemas & Serializer (`src/schemas/avro_schemas.py`)

Create `src/schemas/avro_schemas.py` containing:
- Avro schema dictionaries defined with standard Avro spec (Record type `MarketEvent`).
- Helper functions `serialize_avro(event: BaseMarketEvent) -> bytes` and `deserialize_avro(payload: bytes) -> dict`.

**Lint & Type Check:**
```bash
ruff check src/schemas/avro_schemas.py --fix
ruff format src/schemas/avro_schemas.py
mypy src/schemas/avro_schemas.py
```

---

## Step 4 — Write Unit Tests (`tests/unit/schemas/test_schemas.py`)

Create tests covering:
1. Valid payload instantiation for Crypto, Stocks, and Forex Pydantic models.
2. Field validation errors (negative price, invalid asset class, missing symbol).
3. Avro serialization & deserialization round-trip (Pydantic model -> Avro bytes -> dict -> Pydantic model).
4. Edge cases (zero volume, fractional timestamps).

**Run tests:**
```bash
# Run schema unit tests
pytest tests/unit/schemas/test_schemas.py -v

# Run full test suite with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

**Lint & Type Check test file:**
```bash
ruff check tests/unit/schemas/test_schemas.py --fix
ruff format tests/unit/schemas/test_schemas.py
mypy tests/unit/schemas/test_schemas.py
```

---

## Step 5 — Full Lint & Type Check Pass

Run full project checks:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/ tests/
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

All checks must pass (coverage ≥ 80%).

---

## Step 6 — Commit, Push & Open PR

```bash
# Stage new files
git add src/schemas/ pyproject.toml tests/unit/schemas/ docs/issue_4_plan.md

# Commit
git commit -m "feat(schemas): add Pydantic v2 models and Avro serialization (#4)

- Implements BaseMarketEvent, CryptoEvent, StockEvent, ForexEvent models
- Adds Avro schema definition and fastavro serialization helpers
- Adds comprehensive unit tests for validation and round-trip serialization"

# Push branch
git push origin feature/issue-4-event-schemas
```

Open Pull Request:
```bash
gh pr create \
  --title "feat(schemas): Pydantic v2 & Avro event schemas (#4)" \
  --body "Closes #4. Implements strongly typed market event models and Avro binary serialization." \
  --base develop \
  --head feature/issue-4-event-schemas
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 4 --comment "Implemented in feat(schemas): Pydantic v2 & Avro event schemas — merged to develop."

# Sync local develop
git checkout develop
git pull origin develop
```

**Verify issue is closed:**
```bash
gh issue list       # #4 should no longer appear
gh issue view 4     # status: CLOSED
```

---

## Acceptance Criteria

- [ ] `fastavro` enabled in `pyproject.toml`.
- [ ] Pydantic V2 models (`BaseMarketEvent`, `CryptoEvent`, `StockEvent`, `ForexEvent`) implemented in `src/schemas/market_event.py`.
- [ ] Avro schema and `serialize_avro` / `deserialize_avro` helpers implemented in `src/schemas/avro_schemas.py`.
- [ ] Unit tests cover validation rules, invalid payloads, and Avro round-trip serialization in `tests/unit/schemas/test_schemas.py`.
- [ ] Coverage ≥ 80%, `ruff` and `mypy` pass cleanly with 0 errors.
- [ ] PR merged to `develop`, Issue #4 closed.
