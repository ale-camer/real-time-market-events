# Development Plan — Issue #2: Polygon.io Extractor

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-2-polygon-extractor`  
**Milestone:** M1 — Ingestion & Kafka  
**GitHub Issue:** [#2](https://github.com/ale-camer/real-time-market-events/issues/2)

---

## Objective

Implement an async extractor for Polygon.io to consume real-time (or delayed) market events for stocks and forex. The implementation should support WebSocket connections based on the `.env.example` configurations, and utilize `httpx` for any necessary REST API fallback or initial metadata fetching. Output should be structured log entries — no Kafka integration yet.

---

## Step 0 — Activate venv & Create Feature Branch

> Always do this before touching any code.

```bash
# 1. Activate the virtual environment
source .venv/bin/activate

# Verify it's active
which python   # should point to .venv/bin/python
python --version  # should be 3.11.x
```

```bash
# 2. Make sure you are on develop and it's up to date
git checkout develop
git pull origin develop

# 3. Create and switch to the feature branch
git checkout -b feature/issue-2-polygon-extractor

# 4. Link the branch to GitHub Issue #2
gh issue develop 2 --checkout
# If the above fails (branch already created), just push and link manually:
git push -u origin feature/issue-2-polygon-extractor
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-2-polygon-extractor
gh issue view 2             # should show issue #2 details
```

---

## Step 1 — Uncomment & Install Dependencies

Edit `pyproject.toml` to uncomment the `httpx` dependency if not already uncommented, as it might be needed for REST calls:

```toml
# pyproject.toml → [project] dependencies
"httpx>=0.27.0",
```

Then install:
```bash
pip install -e ".[dev]"
```

**Verify:**
```bash
pip show httpx websockets pydantic pydantic-settings
python -c "import httpx; print(httpx.__version__)"
```

---

## Step 2 — Review Polygon.io API Docs & Config

- Review the [Polygon.io Stocks WebSocket Docs](https://polygon.io/docs/stocks/getting-started) to understand the subscription payloads and message formats.
- Update `src/extractors/polygon.py` (which you will create) to define a `PolygonSettings` class that inherits from `BaseSettings` (using Pydantic V2 `model_config = SettingsConfigDict(env_file=".env", extra="ignore")`), pulling `POLYGON_API_KEY` and `POLYGON_WS_URL`.

---

## Step 3 — Implement the Extractor (`src/extractors/polygon.py`)

Create `src/extractors/polygon.py` with an async client class `PolygonExtractor`.

**Key responsibilities:**
- Connect to the Polygon WebSocket URL.
- Send the authentication payload (Polygon requires auth before subscribing).
- Send subscription payload for configured stock/forex symbols (e.g., `T.AAPL`, `T.MSFT`).
- Read messages in a continuous async loop.
- Normalize raw JSON into a plain dict with: `symbol`, `price`, `volume`, `timestamp`.
- Log structured output using Python's `logging` module.
- Implement exponential backoff reconnection.
- Support clean `shutdown` via asyncio.Event.

**Verify (manual smoke test):**
```bash
# Run a quick manual test from the project root
python -c "
import asyncio
from src.extractors.polygon import PolygonExtractor

async def main():
    ext = PolygonExtractor(symbols=['T.AAPL', 'T.MSFT'])
    await ext.run()

asyncio.run(main())
"
# Press Ctrl+C to stop — verify graceful shutdown message appears.
```

**Lint & type-check:**
```bash
ruff check src/extractors/polygon.py --fix
ruff format src/extractors/polygon.py
mypy src/extractors/polygon.py
```

---

## Step 4 — Write Unit Tests (`tests/unit/extractors/test_polygon.py`)

Create tests using `pytest-asyncio` and `unittest.mock` to mock the WebSocket and/or REST calls.

**Test cases to cover:**
1. Successful auth, subscription, and message parsing.
2. Handling of authentication failures.
3. `ConnectionClosedError` triggers reconnect after backoff delay.
4. Calling `shutdown()` stops the loop cleanly.

**Run tests:**
```bash
# Run only this test file
pytest tests/unit/extractors/test_polygon.py -v

# Run with coverage report for all extractors
pytest tests/unit/extractors/ -v --cov=src/extractors --cov-report=term-missing
```

**Lint the test file:**
```bash
ruff check tests/unit/extractors/test_polygon.py --fix
ruff format tests/unit/extractors/test_polygon.py
mypy tests/unit/extractors/test_polygon.py
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
git add src/extractors/polygon.py tests/unit/extractors/test_polygon.py pyproject.toml docs/issue_2_plan.md

# Commit (reference Issue #2 in the message)
git commit -m "feat(extractor): add Polygon.io REST/WS extractor (#2)

- Implements PolygonExtractor with async WebSocket and auth flow
- Normalizes raw market data to structured dictionaries
- Full unit test coverage with mocked endpoints"

# Push the branch
git push origin feature/issue-2-polygon-extractor
```

Open the Pull Request:
```bash
gh pr create \
  --title "feat(extractor): Polygon.io extractor (#2)" \
  --body "Closes #2. Implements async client for Polygon.io stocks/forex with reconnection logic and tests." \
  --base develop \
  --head feature/issue-2-polygon-extractor
```

---

## Step 7 — Merge & Close Issue

```bash
# Merge PR (squash for a clean develop history)
gh pr merge --squash --delete-branch

# Close the issue explicitly (if not auto-closed by PR)
gh issue close 2 --comment "Implemented in feat(extractor): Polygon.io extractor — merged to develop."

# Pull develop locally
git checkout develop
git pull origin develop
```

**Verify issue is closed:**
```bash
gh issue list       # #2 should no longer appear
gh issue view 2     # should show status: CLOSED
```

---

## Acceptance Criteria

- [ ] `httpx` installed and tracked in `pyproject.toml`.
- [ ] `src/extractors/polygon.py` implements async WebSocket/REST client.
- [ ] Client properly authenticates with Polygon.io WebSocket before subscribing.
- [ ] Client logs received normalized events for stocks/forex.
- [ ] Exponential backoff reconnection is fully functional.
- [ ] Unit tests cover authentication success/failure, message parsing, disconnects, and shutdown.
- [ ] `pytest` coverage is ≥ 80% for the new extractor.
- [ ] PR opened, merged to `develop`, and Issue #2 closed.
