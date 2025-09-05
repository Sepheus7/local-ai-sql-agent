# AI SQL Agent — Streamlit (OpenAI or Amazon Bedrock)

Natural-language to SQL with safe execution against a local SQLite database. Choose OpenAI (easy demo) or Amazon Bedrock. Includes schema-aware prompting, ERD visualization, and a polished Streamlit UI.

Features

- OpenAI or Bedrock provider: pick in the sidebar; OpenAI default for easy demos.
- Schema-aware prompting: compact schema overview is injected for better SQL.
- Safety: SELECT-only, forbidden keyword checks, enforced LIMIT.
- Data model tab: seed Baseball demo data, view ERD, and per-table schema dropdowns.
- Results UX: table preview, CSV download, quick charts (bar/line when suitable).
- Makefile: one-command demo; `db.reset` seeds SQLite automatically.
- Quality: tests, pre-commit (ruff/black/isort/nbstripout), GitHub Actions CI.

Quickstart (local, venv)

1) Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# optional: cp .env.example .env  # fill AWS and model settings (if tracked)
```

2) Database (SQLite by default)

```bash
make db.reset  # recreates the DB and seeds Baseball CSVs
```

3) Run the app

```bash
streamlit run app/app.py
```

Or one command demo:
```bash
make demo
```

Quickstart (conda)

```bash
conda env create -f environment.yml
conda activate ai-sql-agent
make db.reset
streamlit run app/app.py
```

Required environment variables

- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
- BEDROCK_MODEL_ID (e.g., anthropic.claude-3-5-sonnet-20240620-v1:0)
- Optional: HF_TOKEN (if dataset is private)
- Optional (OpenAI provider): OPENAI_API_KEY

Provider selection

- In the app sidebar, choose the provider:
  - OpenAI: paste your `OPENAI_API_KEY` (default path).
  - Bedrock: uses AWS creds from environment to call your model.
- You can also set `LLM_PROVIDER=openai|bedrock` as an environment variable.

How to use
- Open the app → go to the “Data model” tab → click “Seed demo data”.
- Return to “Query” tab → ask a question → Generate SQL → Run SQL.
- Explore charts and export results; view ERD and per-table schemas in “Data model”.

Hugging Face Spaces

- Entry: `app/app.py` (Streamlit)
- Files: `requirements.txt`, `space.yaml`
- Set secrets: AWS keys/region and `BEDROCK_MODEL_ID`
- Dataset loads from the Hub for reproducibility

Repository layout

```
app/                # Streamlit app (app.py entrypoint)
src/                # agent core, providers, db adapters, data seeder, utils
tests/              # unit tests (guardrails, etc.)
infra/              # CI workflow, HF Space config; aws scripts paused under infra/aws
docs/               # PRD and assets
notebooks/          # exploratory notebooks (outputs stripped)
```

Development

- Pre-commit
```bash
pip install pre-commit && pre-commit install
pre-commit run -a
```

- Tests & CI
```bash
pytest -q
```
CI runs ruff/black and pytest on PRs.

License
MIT — see LICENSE
