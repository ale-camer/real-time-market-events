# Development Plan — Issue #3: Kafka Producer

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-3-kafka-producer`  
**Milestone:** M1 — Ingestion & Kafka  
**GitHub Issue:** [#3](https://github.com/ale-camer/real-time-market-events/issues/3)

---

## Objective

Implement a resilient Kafka Producer wrapper in `src/producers/kafka_producer.py` using `confluent-kafka`. The producer will be responsible for publishing normalized market event payloads to configured Kafka topics (`market.events.crypto`, `market.events.stocks`, `market.events.forex`). It must handle JSON serialization, delivery report callbacks, error handling, retries, and graceful flush/shutdown.

---

## Step 0 — Activate venv & Create Feature Branch

> Always do this before touching any code.

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# Verify it's active
which python   # should point to .venv/bin/python
python --version  # should be 3.11.x or 3.14.x
```

```bash
# 2. Make sure you are on develop and it's up to date
git checkout develop
git pull origin develop

# 3. Create and switch to the feature branch
git checkout -b feature/issue-3-kafka-producer

# 4. Link the branch to GitHub Issue #3
gh issue develop 3 --checkout
# If the above fails (branch already created), just push and link manually:
git push -u origin feature/issue-3-kafka-producer
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-3-kafka-producer
gh issue view 3             # should show issue #3 details
```

---

## Step 1 — Uncomment & Install Dependencies

Edit `pyproject.toml` to uncomment the `confluent-kafka` dependency under `[project] dependencies`:

```toml
# pyproject.toml → [project] dependencies
"confluent-kafka>=2.4.0",
```

Then install:
```bash
pip install -e ".[dev]"
```

**Verify:**
```bash
pip show confluent-kafka
python -c "import confluent_kafka; print(confluent_kafka.__version__)"
```

---

## Step 2 — Review Kafka Settings & Config

- Check `.env.example` for Kafka settings (`KAFKA_BOOTSTRAP_SERVERS`, topic names, security settings).
- Define a `KafkaProducerSettings` class using `pydantic-settings` (with `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`).

---

## Step 3 — Implement the Kafka Producer (`src/producers/kafka_producer.py`)

Create `src/producers/kafka_producer.py` with the `EventProducer` class.

**Key responsibilities:**
- Initialize `confluent_kafka.Producer` with configuration dictionary (e.g., `bootstrap.servers`, `acks='all'`, `retries=3`, `retry.backoff.ms=100`).
- Provide an `produce(topic: str, key: str, value: dict)` method that serializes payload to JSON string/bytes.
- Implement a delivery report callback function (`_delivery_report(err, msg)`) to log successful deliveries or errors.
- Include a `flush(timeout: float = 5.0)` method for graceful shutdown/draining.
- Ensure proper logging using Python's standard `logging`.

**Verify (manual smoke test with mock/local broker):**
```bash
python -c "
from src.producers.kafka_producer import EventProducer

producer = EventProducer()
print('Producer initialized successfully:', producer)
"
```

**Lint & type-check:**
```bash
ruff check src/producers/kafka_producer.py --fix
ruff format src/producers/kafka_producer.py
mypy src/producers/kafka_producer.py
```

---

## Step 4 — Write Unit Tests (`tests/unit/producers/test_kafka_producer.py`)

Create tests using `pytest` and `unittest.mock` to mock `confluent_kafka.Producer`.

**Test cases to cover:**
1. Successful message production (`produce()` calls underlying producer with correct topic, key, and serialized JSON value).
2. Delivery report callback handles success and error cases appropriately (logs info vs. error).
3. `flush()` calls the underlying producer's `flush()`.
4. Serialization of custom data types or malformed payloads handled gracefully.

**Run tests:**
```bash
# Run unit tests for producer
pytest tests/unit/producers/test_kafka_producer.py -v

# Run full test suite with coverage
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

**Lint & type-check test file:**
```bash
ruff check tests/unit/producers/test_kafka_producer.py --fix
ruff format tests/unit/producers/test_kafka_polygon.py
mypy tests/unit/producers/test_kafka_producer.py
```

---

## Step 5 — Full Lint & Type Check Pass

Run the full suite before committing:

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
# Stage all new files
git add src/producers/kafka_producer.py tests/unit/producers/test_kafka_producer.py pyproject.toml docs/issue_3_plan.md

# Commit (reference Issue #3 in the message)
git commit -m "feat(producer): add Kafka producer with serialization and delivery callbacks (#3)

- Implements EventProducer using confluent-kafka
- Handles JSON serialization, retries, and delivery reports
- Adds unit tests with mocked Kafka producer"

# Push the branch
git push origin feature/issue-3-kafka-producer
```

Open the Pull Request:
```bash
gh pr create \
  --title "feat(producer): Kafka producer with retries (#3)" \
  --body "Closes #3. Implements EventProducer for publishing market events to Kafka topics." \
  --base develop \
  --head feature/issue-3-kafka-producer
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR (squash for a clean develop history)
gh pr merge --squash --delete-branch

# Close the issue explicitly (if not auto-closed by PR)
gh issue close 3 --comment "Implemented in feat(producer): Kafka producer — merged to develop."

# Pull develop locally
git checkout develop
git pull origin develop
```

**Verify issue is closed:**
```bash
gh issue list       # #3 should no longer appear
gh issue view 3     # should show status: CLOSED
```

---

## Acceptance Criteria

- [ ] `confluent-kafka` dependency enabled in `pyproject.toml`.
- [ ] `src/producers/kafka_producer.py` implements `EventProducer`.
- [ ] Support for JSON serialization and key/value routing to topics.
- [ ] Delivery report callback logs message status.
- [ ] `flush()` method implemented for clean shutdown.
- [ ] Unit tests pass with mocked `confluent_kafka.Producer`.
- [ ] `pytest` coverage ≥ 80%.
- [ ] `ruff` and `mypy` pass with 0 errors.
- [ ] PR merged to `develop`, Issue #3 closed.
