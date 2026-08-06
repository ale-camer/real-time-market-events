# Development Plan — Issue #6: Faust App skeleton (M2)

**Project:** Real-Time Market Events Stream  
**Branch:** `feature/issue-6-faust-skeleton`  
**Milestone:** M2 — Stream Processing  
**GitHub Issue:** [#6](https://github.com/ale-camer/real-time-market-events/issues/6)

---

## Objective

Configurar la aplicación Faust y su ciclo de vida. Set up the skeleton for the **Faust-Streaming** application. This includes configuring the Faust `App`, defining the Kafka topics, and setting up the basic worker lifecycle (start, stop, logging). No complex transformations yet, just the basic application structure that can consume events from the Kafka topics created in M1.

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
git checkout -b feature/issue-6-faust-skeleton

# 4. Link branch to GitHub Issue #6
gh issue develop 6 --checkout
# If already created, push manually:
git push -u origin feature/issue-6-faust-skeleton
```

**Verify:**
```bash
git branch --show-current   # should print: feature/issue-6-faust-skeleton
gh issue view 6             # should show issue #6 details
```

---

## Step 1 — Configure Faust Dependency (`pyproject.toml`)

Verify or add `faust-streaming` to `pyproject.toml`. This is the fork of Faust that is currently maintained and compatible with modern Python.

```bash
# Install faust-streaming
pip install faust-streaming

# Ensure it's added to pyproject.toml dependencies
```

---

## Step 2 — Create the Faust App Configuration (`src/consumers/app.py`)

Create the main Faust application instance.

**Requirements:**
1. Initialize the `faust.App` with a unique ID (e.g., `market-events-processor`).
2. Configure the Kafka broker URL (read from `KAFKA_BROKER_URL` environment variable, fallback to `kafka://localhost:9092`).
3. Set up appropriate serialization config (e.g., JSON or Avro, leveraging the schemas from M1).
4. Configure basic logging for the worker.

**Verify:**
```bash
python -c "from src.consumers.app import app; print(f'App ID: {app.conf.id}, Broker: {app.conf.broker}')"
```

---

## Step 3 — Define Topic Configurations (`src/consumers/topics.py`)

Define the Faust topics that the app will consume from.

**Requirements:**
1. Import the schemas created in M1 (e.g., `CryptoEvent`, `StockEvent`).
2. Define the `market.crypto`, `market.stocks`, and `market.forex` topics using `app.topic()`.
3. Link the Pydantic/Avro models to the Faust topics so incoming messages can be deserialized properly.

**Verify:**
```bash
# (Assuming topics are named market.crypto, etc.)
python -c "import sys; from src.consumers.topics import *; print('Topics loaded successfully.')"
```

---

## Step 4 — Create a Skeleton Consumer Agent (`src/consumers/agents.py`)

Create dummy agents to verify the app can consume events.

**Requirements:**
1. Decorate async functions with `@app.agent(topic)`.
2. Iterate over the stream and log the received events.
3. No business logic yet, just `logger.info(f"Received event: {event}")`.

**Verify:**
```bash
# Verify the agents are registered with the app
python -c "from src.consumers.agents import app; print([agent.name for agent in app.agents.values()])"
```

---

## Step 5 — Application Entrypoint (`src/consumers/main.py`)

Create the entrypoint to easily run the Faust worker and load the agents.

**Requirements:**
1. Import the `app` from `app.py`.
2. Import the agents from `agents.py` to ensure they are registered with the app.
3. Add an `if __name__ == '__main__':` block to run the app using `app.main()`.

**Verify:**
```bash
# List available agents
faust -A src.consumers.main agents

# Verify the worker starts (use Ctrl+C to stop)
faust -A src.consumers.main worker -l info
```

---

## Step 6 — Full Lint & Type Check Pass

Run full project checks to ensure code quality.

```bash
# Linting & Formatting
ruff check src/consumers/
ruff format src/consumers/

# Static type analysis
mypy src/consumers/
```

---

## Step 7 — Commit, Push & Open PR

```bash
# Stage new files
git add src/consumers/ docs/issue_6_plan.md pyproject.toml

# Commit
git commit -m "feat(m2): implement faust app skeleton and basic agents (#6)

- Adds faust-streaming dependency
- Configures main Faust App with broker connection
- Defines Kafka topics with schema integration
- Creates skeleton consumer agents for logging events"

# Push branch
git push origin feature/issue-6-faust-skeleton
```

Open Pull Request:
```bash
gh pr create \
  --title "feat(m2): Faust App skeleton (#6)" \
  --body "Closes #6. Configures the Faust application, topics, and skeleton agents to consume market events." \
  --base develop \
  --head feature/issue-6-faust-skeleton
```

---

## Step 8 — Merge & Close Issue

```bash
# Merge PR
gh pr merge --squash --delete-branch

# Close issue explicitly
gh issue close 6 --comment "Implemented via PR — Faust app skeleton created."

# Sync local develop
git checkout develop
git pull origin develop
```

---

## Acceptance Criteria

- [ ] `faust-streaming` dependency is added to the project.
- [ ] `src/consumers/app.py` initializes a `faust.App` connecting to the configured Kafka broker.
- [ ] `src/consumers/topics.py` defines the topics and links them to M1 schemas.
- [ ] `src/consumers/agents.py` has at least one agent that logs incoming messages for testing.
- [ ] The Faust worker can be successfully started via CLI (e.g., `faust -A src.consumers.main worker -l info`).
- [ ] Code is clean, passing `ruff` and `mypy` checks.
