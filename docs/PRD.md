## AI SQL Agent (Amazon Bedrock + Function Calling) — Product Requirements Document

### TL;DR

Build a production-ready AI SQL Agent that converts natural language into safe, validated SQL against a well-modeled dataset, executes it, and presents results in a polished Streamlit UI. The agent uses Amazon Bedrock with function calling for tool-use (schema discovery, SQL generation, error recovery) and is deployable locally, on Hugging Face Spaces, and optionally on AWS.

### Objectives and Success Criteria

- Deliver a recruiter-ready portfolio project with clean architecture, great UX, and CI.
- Run fully on Hugging Face Spaces with secrets, reading a reproducible dataset hosted on the Hub.
- Showcase Amazon Bedrock function calling to orchestrate schema-aware SQL generation and safe execution.
- Provide robust validation (only SELECT; bounded results; schema constraints) and a golden-test suite.
- Make onboarding trivial: one-command setup, demo data, and example queries.

### Non-Goals

- Full enterprise features (RBAC, multi-tenant auth) and write operations (INSERT/UPDATE/DELETE).
- Complex query optimizations beyond EXPLAIN-based sanity checks.

### Primary Users and Use Cases

- Recruiters/engineers evaluating portfolio projects: quick demo on HF Space, skim code quality and tests.
- Data-minded users: ask NL questions about a known dataset and inspect the generated SQL.
- Developers: learn how to integrate Bedrock tool-use and Streamlit in a clean reference app.

### System Overview

- Input: Natural language query.
- Agent: Uses Bedrock model with function calling to gather schema context, propose SQL, validate, refine upon errors.
- Data: SQLite (default) seeded from a clean dataset hosted on Hugging Face. Optional Postgres backend via Docker.
- UI: Streamlit app with schema browser, sample queries, SQL preview, results table, export, and history.

### High-level Architecture

- App/UI (Streamlit): query input; show SQL; results; metadata; history.
- Agent Orchestrator: prompt templates; tool-use policy; retries/refinement; guardrails.
- LLM Client: Amazon Bedrock Converse API with tool-use (function calling) abstraction.
- Tools (functions invoked by model):
  - list_tables(), list_columns(table), get_schema_overview(),
  - summarize_schema() (compact, LLM-generated summary cached),
  - execute_sql_readonly(sql, limit, timeout_ms),
  - explain_error(error_message, sql) (optional refinement helper).
- SQL Validator: blocks non-SELECT, unsafe keywords, long runtime; enforces LIMIT.
- DB Layer: SQLAlchemy-based adapters for SQLite and Postgres; Alembic migrations; seeders.
- Data Validation: lightweight checks or Great Expectations for row counts, fks, value ranges.

### Repository Structure

- app/: Streamlit app (entrypoint `app.py` for HF Space)
- src/
  - agent/: orchestration, prompts, tool definitions, guardrails
  - data/: schema DDL, migrations (Alembic), loaders, seeders, expectations
  - clients/: bedrock client, hf hub loader
  - db/: sqlalchemy session, adapters (sqlite/postgres)
  - utils/: config, logging, error types
- tests/: unit, integration, golden tests (input → expected SQL)
- infra/: docker, space.yaml, gh actions, optional aws deployment scripts
- docs/: PRD, architecture diagrams, ERD, screenshots
- examples/: queries.json, sample use-cases

### Data Modeling & Validation

- Dataset: Baseball (Hall of Fame, players, salaries, awards). Publish CSVs to Hugging Face Datasets for reproducibility.
- DB: SQLite default for HF Space; Postgres optional for realism.
- Migrations: Alembic to define schema and enable upgrades.
- Seed: Deterministic seeding from HF Dataset or included CSV snapshot.
- Validation: basic checks (row counts; primary/foreign keys; null/value ranges). Great Expectations optional.
- ERD: include diagram in docs and UI schema browser.

### AI Design (Bedrock + Function Calling)

- Models: Prefer `anthropic.claude-3-5-sonnet` (Bedrock) for high-quality tool-use; fallback to a smaller instruct model if needed.
- Tool Specifications:
  - list_tables(): returns table names
  - list_columns(table_name): returns column names and types
  - get_schema_overview(): returns compact human-readable overview
  - execute_sql_readonly(sql, limit=500, timeout_ms=5000): executes SELECT-only
  - explain_error(error_message, sql): returns concise hint for refinement
- Orchestration Policy:
  - The model must first gather relevant schema details before attempting SQL.
  - The model may iterate: propose SQL → validate → on error, call explain_error → refine once or twice.
  - Always include `LIMIT` and avoid non-deterministic functions when possible.
- Prompting:
  - System: objectives, safety rules, schema browsing via tools, response format (show SQL then results).
  - Few-shot examples: 5–10 canonical question→SQL pairs.
  - Schema Summary: cached description to reduce tool calls.
- Safety & Guardrails:
  - Hard block DDL/DML, `ATTACH`, `PRAGMA`, and suspicious tokens.
  - Enforce `SELECT` and add `LIMIT` if missing.
  - Timeouts on DB execution; result row cap; column redaction list (optional).
  - Log tool invocations and decisions for observability.

### User Experience (Streamlit)

- Query input with examples; schema browser (tables, columns, descriptions).
- Generated SQL preview with copy button; execution status; elapsed time.
- Results: table with pagination; CSV download.
- Error handling: readable messages and hints; option to retry/refine.
- Query history in session; clear button; dark/light theme.
- Optional: "Use @web" to augment with a lightweight web/browse tool (e.g., Wren-style) for public docs—off by default.

### Deployment Targets

- Hugging Face Spaces (default demo):
  - `app/app.py` entrypoint (Streamlit).
  - `requirements.txt` includes `boto3`, `anthropic-bedrock`, `sqlalchemy`, `streamlit`, `datasets`/`huggingface_hub`.
  - `space.yaml`: hardware (CPU ok), startup command, Python version.
  - Secrets: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `BEDROCK_MODEL_ID`, optional `HF_TOKEN`.
- Local:
  - `make setup && make db.reset && make run.app` for quickstart.
  - `.env` with AWS and model config.
- Optional AWS:
  - Containerized app on ECS/Fargate or a Lambda backend for SQL execution; API Gateway; CloudWatch logs.

### CI/CD

- GitHub Actions:
  - Lint (ruff/black/isort), type check (mypy optional).
  - Unit and integration tests against ephemeral SQLite seeded from HF dataset.
  - Golden SQL tests (snapshots for canonical questions).
  - Optional: deploy to HF Space on main via `huggingface-cli` and token.

### Testing Strategy

- Unit: validators, prompt builders, Bedrock client wrapper, tool schema.
- Integration: end-to-end generate→validate→execute on sample queries.
- Golden: NL input → expected SQL snapshot; guard against regressions.
- Smoke: Streamlit app starts; core widgets render; one sample query passes.

### Milestones & Timeline

- M1 (1–2 weeks): Repo cleanup, config, Bedrock client, basic tool-use path, minimal UI.
- M2 (2–3 weeks): Data migrations/seeders; schema browser; validator; golden tests.
- M3 (2–3 weeks): Improved prompting; error-refinement loop; UX polish; export/history.
- M4 (1–2 weeks): CI/CD, Space deployment, docs/screenshots, evaluation harness.

### Risks & Mitigations

- Bedrock access/limits on HF Space: ensure secrets; add local `transformers` fallback.
- Schema drift: freeze seed dataset version; migrations tested in CI.
- Query safety: layered checks plus execution sandbox and LIMIT/timeout.

### Open Questions

- Default model (Claude vs smaller model) and cost/latency targets.
- Streamlit vs potential Gradio alternative; keep Streamlit unless required otherwise.
- Include optional Wren-style @web browsing tool or keep it as a stretch?
