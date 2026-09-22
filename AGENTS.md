# Working on MathApp

## Start here

Read `README.md`, `docs/work-log.md`, `docs/data-model.md`, and
`docs/training.md` before making architecture changes. The active code is
`backend/`, `frontend/`, and `ml/src/mathapp_ml/`. `legacy/` is preserved reference
code, not an alternate supported application.

## User preferences and agreed scope

- Work in small understandable stages. Explain results plainly.
- Document substantive changes, commands, checks, decisions and remaining work
  in Markdown, especially `docs/work-log.md`, so future Codex sessions can resume.
- The user does not want all dataset questions read into model context. Use local
  scripts for counts, schema, validation, deduplication and metrics; report compact
  summaries. Do not dump CSV rows or chat data unless explicitly requested.
- Current scope (2026-09-21): keep MathApp local; the user no longer wants to
  publish it. Earlier owner/invited-tester hosting plans are historical. The
  previously discussed API/hosting budget was around $10–20 monthly. No public
  launch, paid API calls, provider account creation or credential rotation is
  implied by local work.
- The OpenAI Responses integration and blue conversation UI are implemented.
  Read docs/chat.md for compact memory, references, and cost-control limitations.
  Live provider quality and hard spend caps still need validation. Read root
  `details.md` for the architecture/interview guide and current unfinished-work
  report, including missing OCR/PDF dependencies and conflicting Python locks.

## Data and ML rules

- Preserve raw CSVs, originals, and full messages. Do not replace equations with
  lossy summaries or change variable case/superscripts during identity checks.
- Features use question text ONLY. Never feed labels, subtopics, group IDs,
  solutions, or review metadata into training features.
- Synthetic/unreviewed data remains pending. Experimental training requires an
  explicit opt-in; predictions never become verified labels automatically.
- Split template groups together. Fit preprocessing only on training data,
  select settings on validation, and reserve test data for final evaluation.
- Synthetic holdout scores are not real-world accuracy. A reviewed real test set
  and independent language evaluation remain required.
- Version datasets/models immutably. Keep checksums, split membership, dependency
  versions and evaluation reports. Never silently overwrite an active artifact.
- Load only trusted operator-selected joblib files. Cache loading per process;
  restart backend processes to adopt a new model version.
- The user explicitly authorized committing non-sensitive project data on
  2026-09-22, including the 1,000-example synthetic CSV, model artifacts, splits,
  and reports. These are tracked. Never commit credentials, runtime PostgreSQL
  files, SQLite databases, private user/chat data, or user uploads. Review future
  datasets/exports for sensitive data before staging. Generated environments,
  dependencies, and caches remain ignored.

## Verification

Use the repository `.venv` and `requirements-local.lock` (verified with Python
3.12). Base database/training tests do not require OCR or a paid provider key.
Run from the repository root:

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py makemigrations --check --dry-run
.venv/bin/pytest -q --tb=line
git diff --check
```

The local PostgreSQL cluster is specific to this project, on loopback port 55432.
Use `.venv/bin/python scripts/local_db.py start|status|stop`. Connection settings
are private in `backend/.env`; never print them. Tests use a separate test database.
Do not modify another project's database or replace an existing `.env`.
Use short test tracebacks: database connection failures can expose credentials
in default pytest local-variable output. Never copy such traces into documentation.

Run frontend checks when changing frontend behavior. Paid solver calls must be
mocked in routine tests. The dev-only offline preview is described in docs/chat.md.
