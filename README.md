# MathApp

React frontend, Django API, PostgreSQL data layer, and a local question-only math
subject classifier. The current scope is local use; publishing is not planned.
The solver uses OpenAI's Responses API with a configurable
reasoning model. The blue chat UI supports saved conversations, compact memory,
classifier comparisons and compressed transcript exports. API calls still leave
the computer and can incur charges; a hard spending cap is not implemented.

Read [details.md](details.md) for the complete beginner-friendly architecture,
data engineering walkthrough, interview preparation, and unfinished-work report.

See [chat behavior and memory](docs/chat.md) for the new interface and API details.

For future Codex sessions, start with `AGENTS.md` and [the work log](docs/work-log.md).

## Layout

```text
backend/        Active Django API, database models and migrations
frontend/       Active React/Vite interface
ml/src/         Installable classifier, validator, training and prediction CLI
data/raw/       Original non-sensitive training CSV datasets (tracked)
data/processed/ Non-sensitive reviewed training snapshots (track after review)
data/runtime/   Local PostgreSQL data, connection config and logs (gitignored)
data/samples/   Original repository's demonstration PDFs/images/JSON
models/         Versioned trained candidates, splits and evaluation reports (tracked)
tests/          Import, data-integrity, ML and authenticated API tests
scripts/        Local development utilities
docs/           Architecture and training documentation
legacy/         Preserved older prototype; not imported by the active app
```

## Environment

Run commands from this repository root. Use Python 3.12 for the verified local
lockfile. Install uv and PostgreSQL separately if they are not already present.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-local.lock -e .
```

This installs the database/training/test dependencies. To run paid solving and
image/PDF extraction, also install `backend/requirements.txt`. OCR dependencies
are intentionally separate and loaded lazily; training does not require them.
Set `OPENAI_API_KEY` in `backend/.env` before trying a real solve. The default
model is `gpt-5.6-terra`; it can be changed with `OPENAI_MODEL`.

Current environment note: optional image/PDF dependencies are not installed.
Also, `uv.lock` currently disagrees with the backend Django 5.2 requirement through
the type-stub dependency chain in `pyproject.toml`. Avoid automatic project sync
from the verified PyCharm interpreter until the dependency declarations are
reconciled. See the dependency finding in [details.md](details.md).

## Local PostgreSQL

```bash
.venv/bin/python scripts/local_db.py init
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py import_training_csv data/raw/math_subject_classifier_en_1000.csv
```

Initialization creates a dedicated local database on `127.0.0.1:55432`, protected
by a generated password, and writes private settings to `backend/.env`. It never
replaces an existing cluster or `.env`. Data lives in `data/runtime/postgres` on
your computer. This is not Neon and has not been uploaded anywhere.

On later sessions, use `scripts/local_db.py start`; use `stop` to shut it down.
If `.env` already exists, follow `backend/.env.example` to configure a database
manually. Without DATABASE_URL, debug development falls back to SQLite; production
requires a configured database URL and secret. Never commit credentials.

## Training and review

```bash
.venv/bin/mathapp-ml audit data/raw/math_subject_classifier_en_1000.csv
.venv/bin/mathapp-ml train data/raw/math_subject_classifier_en_1000.csv --output models/baseline-v1 --include-pending
.venv/bin/mathapp-ml predict 'Evaluate lim x->2 x^2' --model models/baseline-v1/classifier.joblib
.venv/bin/python backend/manage.py register_model models/baseline-v1
```

If `baseline-v1` is already present, use it or choose a new output version. The
initial synthetic CSV remains pending. To review it locally, create your own admin
account with `backend/manage.py createsuperuser`, then start the backend:

```bash
.venv/bin/python backend/manage.py runserver 127.0.0.1:8002
```

Visit `/ms-admin-panel/` and review individual Training examples. Export reviewed
data with `backend/manage.py export_training_csv data/processed/approved-v1.csv`.
No admin credentials are pre-created or committed.

The authenticated endpoint `POST /api/solver/classify/` accepts
`{"question": "Evaluate lim x->2 x^2"}` and performs only local inference.
For the existing UI, run `npm ci` and `npm run dev` in `frontend/` (port 3001).

## Verification

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py makemigrations --check --dry-run
.venv/bin/pytest -q --tb=line
```

Tests use Django's separate test database; the local PostgreSQL development role
can create it. Tests mock paid-provider calls. See [training](docs/training.md)
for evaluation limits and [data model](docs/data-model.md) for ownership, review,
file storage and production requirements.

For PyCharm setup and a precise local testing sequence, see
[docs/pycharm.md](docs/pycharm.md). The earlier
[hosting discussion](docs/hosting-plan.md) is retained as historical reference;
it is not the current next step.
