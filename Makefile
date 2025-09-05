PY=python

.PHONY: setup run.app db.reset fmt lint

setup:
	$(PY) -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

run.app:
	PYTHONPATH=. streamlit run app/app.py

db.clean:
	$(PY) -c "import os, pathlib; db=os.getenv('SQLITE_PATH','test.db'); p=pathlib.Path(db);\
		(p.exists() and p.unlink()); print('Removed DB', db)"

db.seed:
	$(PY) -m src.data.seed_sqlite

db.reset:
	make db.clean || true
	make db.seed

demo:
	make db.reset
	PYTHONPATH=. streamlit run app/app.py

fmt:
	ruff check --fix || true
	black . || true

lint:
	ruff check . || true


