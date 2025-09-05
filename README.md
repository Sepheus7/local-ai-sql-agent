# AI SQL Agent (Amazon Bedrock + Function Calling) — Streamlit + HF Space

Build a production-ready AI SQL Agent that turns natural language into safe SQL, executes it, and presents results in a polished Streamlit UI. Orchestrated via Amazon Bedrock with function calling (tool-use). Demo-first for Hugging Face Spaces; runs locally too.

Features

- Bedrock function calling: schema-aware SQL generation with tool-use.
- Safe execution: SELECT-only, LIMIT and timeout enforced, validator.
- Clean data: reproducible dataset from Hugging Face; migrations and seeding.
- Great UX: Streamlit app with schema browser, history, export.
- CI-ready: tests (unit/integration/golden), linting, optional Space deploy.

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

- In the app sidebar, choose the LLM provider:
  - OpenAI: paste your `OPENAI_API_KEY` and the app will call the Chat Completions API.
  - Bedrock: uses your AWS credentials from environment/secrets to call the selected Bedrock model.
- You can also set `LLM_PROVIDER=openai|bedrock` in the environment. Default is `openai` for easy demos.

Hugging Face Spaces

- Entry: `app/app.py` (Streamlit)
- Files: `requirements.txt`, `space.yaml`
- Set secrets: AWS keys/region and `BEDROCK_MODEL_ID`
- Dataset loads from the Hub for reproducibility

Repository layout

```
app/                # Streamlit app (app.py entrypoint)
src/                # agent core, clients, data loaders, db adapters, utils
tests/              # unit, integration, golden sql tests
infra/              # docker, space.yaml, gh actions, optional aws scripts
docs/               # PRD, architecture, ERD, screenshots
examples/           # example queries and flows
```

Status

- M1: Repo structure & PRD docs
- Next: Wire Bedrock function-calling tools and schema browser; add golden tests

License
MIT — see LICENSE
