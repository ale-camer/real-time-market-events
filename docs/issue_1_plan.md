# Development Plan — Issue #1: CoinGecko WebSocket Extractor

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-1-coingecko-ws`  
**Milestone:** M1 — Ingestion & Kafka  
**GitHub Issue:** [#1](https://github.com/ale-camer/real-time-market-events/issues/1)

---

## Objective

Implement an async WebSocket client that connects to CoinGecko's real-time API to consume market events (price, trades, etc.) for configured crypto asset pairs. Output should be structured log entries — no Kafka integration yet (that's Issue #3).

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
git checkout -b feature/issue-1-coingecko-ws

# 4. Link the branch to GitHub Issue #1
gh issue develop 1 --checkout
# If the above fails (branch already created), just push and link manually:
git push -u origin feature/issue-1-coingecko-ws
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-1-coingecko-ws
gh issue view 1             # should show issue #1 details
```

---

## Step 1 — Fix Build Config & Install Dependencies

Antes de instalar dependencias, corrige la configuración de Hatch en `pyproject.toml` agregando al final del archivo para que detecte los paquetes dentro de `src`:

```toml
# --- Hatch Build ---
[tool.hatch.build.targets.wheel]
packages = [
    "src/api",
    "src/consumers",
    "src/extractors",
    "src/loaders",
    "src/producers",
    "src/schemas",
    "src/transformers"
]
```

Luego, descomenta las dependencias de este issue:

```toml
# pyproject.toml → [project] dependencies
"websockets>=12.0",
"pydantic>=2.7.0",
"pydantic-settings>=2.3.0",
```

Then install:
```bash
pip install -e ".[dev]"
```

**Verify:**
```bash
pip show websockets pydantic pydantic-settings   # check versions
python -c "import websockets; print(websockets.__version__)"
```

---

## Step 2 — Review CoinGecko WebSocket API

Before writing any code, understand the API contract:
- Review the [CoinGecko API docs](https://www.coingecko.com/en/api/documentation) for WebSocket endpoint, subscription payloads, and message formats.
- Confirm if auth headers / API key are needed (check `.env.example`).
- Note the exact JSON payload structure for price update events.

Add any needed API keys to `.env.example` (without real values) and to your local `.env`.

---

## Step 3 — Implement the Extractor (`src/extractors/coingecko.py`)

Create `src/extractors/coingecko.py` with an async client class:

**Key responsibilities:**
- Connect to the CoinGecko WebSocket URL.
- Send subscription payload for configured coin pairs.
- Read messages in a continuous async loop.
- Normalize raw JSON into a plain dict with: `symbol`, `price`, `volume`, `timestamp`.
- Log structured output using Python's `logging` module.
- Implement exponential backoff reconnection on disconnect or error.
- Support clean `shutdown` via a cancellation token / asyncio.Event.

**Verify (manual smoke test):**
```bash
# Run a quick manual test from the project root
python -c "
import asyncio
from src.extractors.coingecko import CoinGeckoExtractor

async def main():
    ext = CoinGeckoExtractor(pairs=['bitcoin', 'ethereum'])
    await ext.run()

asyncio.run(main())
"
# You should see structured log output with price events.
# Press Ctrl+C to stop — verify graceful shutdown message appears.
```

**Lint & type-check:**
```bash
ruff check src/extractors/coingecko.py
mypy src/extractors/coingecko.py
```

---

## Step 4 — Write Unit Tests (`tests/unit/extractors/test_coingecko.py`)

Create tests using `pytest-asyncio` and `unittest.mock` to mock the WebSocket:

**Test cases to cover:**
1. Successful connection + message parsing returns expected dict.
2. Message with unexpected format → logs warning, does not crash.
3. `ConnectionClosedError` triggers reconnect after backoff delay.
4. Calling `shutdown()` stops the loop cleanly.

**Run tests:**
```bash
# Run only this test file
pytest tests/unit/extractors/test_coingecko.py -v

# Run with coverage report
pytest tests/unit/extractors/test_coingecko.py -v --cov=src/extractors --cov-report=term-missing
```

**Lint the test file:**
```bash
ruff check tests/unit/extractors/test_coingecko.py
mypy tests/unit/extractors/test_coingecko.py
```

---

## Step 5 — Full Lint & Type Check Pass

Run the full suite before committing:

```bash
ruff check src/ tests/
ruff format src/ tests/
mypy src/
pytest tests/unit/ -v --cov=src --cov-report=term-missing
```

All checks must pass (coverage ≥ 80% for `src/extractors/`).

---

## Step 6 — Commit, Push & Open PR

```bash
# Stage all new files
git add src/extractors/coingecko.py tests/unit/extractors/test_coingecko.py pyproject.toml docs/issue_1_plan.md

# Commit (reference Issue #1 in the message)
git commit -m "feat(extractor): add CoinGecko async WebSocket extractor (#1)

- Implements CoinGeckoExtractor with exponential backoff reconnection
- Normalizes raw WS messages to structured dicts
- Full unit test coverage with mocked WebSocket"

# Push the branch
git push origin feature/issue-1-coingecko-ws
```

Open the Pull Request:
```bash
gh pr create \
  --title "feat(extractor): CoinGecko WebSocket extractor (#1)" \
  --body "Closes #1. Implements async WebSocket client for CoinGecko with reconnection logic and unit tests." \
  --base develop \
  --head feature/issue-1-coingecko-ws
```

**Verify PR was created:**
```bash
gh pr list
gh pr view   # shows the PR details + CI status
```

---

## Step 7 — Merge & Close Issue

After the PR is approved (or self-reviewed):

```bash
# Merge PR (squash for a clean develop history)
gh pr merge --squash --delete-branch

# Close the issue explicitly (if not auto-closed by PR)
gh issue close 1 --comment "Implemented in feat(extractor): CoinGecko WebSocket extractor — merged to develop."

# Pull develop locally
git checkout develop
git pull origin develop
```

**Verify issue is closed:**
```bash
gh issue list       # #1 should no longer appear
gh issue view 1     # should show status: CLOSED
```

---

## Acceptance Criteria

- [ ] venv is active before any work starts.
- [ ] Feature branch `feature/issue-1-coingecko-ws` created from `develop`.
- [ ] `websockets`, `pydantic`, `pydantic-settings` installed and tracked in `pyproject.toml`.
- [ ] `src/extractors/coingecko.py` implements async WebSocket client.
- [ ] Client subscribes to ≥1 coin pair and logs received events.
- [ ] Exponential backoff reconnection works on forced disconnect.
- [ ] Unit tests cover: success, bad message, disconnect, shutdown.
- [ ] `pytest` passes with coverage ≥ 80% for `src/extractors/`.
- [ ] `ruff` and `mypy` pass with zero errors.
- [ ] PR opened, merged to `develop`, Issue #1 closed.

---

## References

- [CoinGecko API Documentation](https://www.coingecko.com/en/api/documentation)
- [websockets library docs](https://websockets.readthedocs.io/)
- [pytest-asyncio docs](https://pytest-asyncio.readthedocs.io/)
- [Issue #1 on GitHub](https://github.com/ale-camer/real-time-market-events/issues/1)
