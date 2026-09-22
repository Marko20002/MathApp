# MathApp work log

## 2026-09-22 — Commit non-sensitive project data and source

The user explicitly requested committing and pushing all needed project files,
including the 1,000-row synthetic training CSV. Removed blanket ignore rules for
raw/processed training data, model artifacts, and reports. Keep credentials,
private database state, user uploads, and local IDE state excluded; reinstallable
environments, dependencies, caches, and build outputs remain ignored.

Updated current documentation to distinguish tracked synthetic training data and
baseline artifacts from private live PostgreSQL/user/chat state. Earlier log
entries retain their historical descriptions. Removed the hard-coded secret from
inactive legacy Django settings in favor of an environment lookup. Private `.env`
values and existing database files were not modified. The old tracked SQLite file
is removed from the new tree; Git history is not rewritten.

Pre-commit review checks candidate files for common credential patterns and exact
matches to configured local secrets without printing their values. Training CSV
and model checksums are compared with the saved report; no retraining or paid
provider calls are needed for this repository-publication step. Previous complete
verification was 40 passing tests and a passing frontend build on 2026-09-21.

Pre-commit results: 142 files in the staged tree; no common-token/private-key
patterns or configured-secret matches found (the explicit CHANGE_ME example URL
is a template). Exactly 1,000 CSV rows, matching dataset/artifact checksums, and
disjoint stored split groups verified. Staged whitespace check passed. Commit and
normal, non-force push target the existing `origin/main`; no history rewrite or
application deployment is part of this step.

## 2026-09-21 — Local-only architecture and Data Engineering interview guide

The user chose to keep the app local rather than publish it. Updated README and
AGENTS scope accordingly; older deployment discussions remain historical.

Created root `details.md`: plain-language architecture, every major folder,
complete browser/authentication/solve/provider/persistence/rendering cycle,
schema and relationships, CSV validation/import/review/export, identity versus
template grouping, leakage prevention, model evaluation/provenance, transactions,
NULL semantics, indexes, data-quality limits, compact context versus gzip export,
read-only SQL, interview stories/questions, and a prioritized unfinished-work report.
Reviewed active code and metadata without dumping dataset rows or private chats.

Concrete remaining work: extraction packages absent from `.venv`; backend Django
5.2 requirements conflict with the Django 6.1 resolution in `uv.lock` through
type-stub dependencies; experimental pending/synthetic baseline lacks reviewed
real-input evaluation/notation improvements; no automated backup/restore or hard
API spend cap. The report also covers OCR limitations, compatibility duplication,
incomplete revision/export/request lineage, and stale/unused code. No application
behavior, dataset, model, credentials, or dependency versions changed in this step.

Verification: Django system check passed; migration drift check passed with local
database access; 40 tests passed against isolated PostgreSQL test DB; frontend
production build passed with the existing large-chunk warning. Verified aggregate
live dataset state: PostgreSQL, one import, 1,000 pending examples, one registered
model. No paid provider calls, actual OCR runs, load tests, or backup restores.

Initial sandboxed tests could not access localhost PostgreSQL. A default traceback
exposed the local database credential in tool output; no value is reproduced here.
Retried successfully with local access and `--tb=line`, and documented safer
diagnostic handling. No credential rotation was performed. Fresh network security
audit was not run; older npm findings are labeled historical in the guide.

## 2026-09-21 — Clipboard images and notation diagnosis

Added composer paste handling for clipboard image files, thumbnail preview with
object-URL cleanup, shared upload validation, and protection against silently
replacing an existing attachment. Plain text/LaTeX paste keeps browser behavior.
Images remain local until Send. No clipboard polling or automatic URL downloads.

Investigated the baseline classifier using only supplied/example questions, not
dataset contents or provider calls. Actual configured thresholds: 60% top score
and 15 percentage points above the runner-up. A screenshot-like question scored
55.7% calculus and therefore UNKNOWN. The shorthand 'lim x-> inf 1/x' scored
44.7%; equivalent LaTeX scored 91.0%, and an explicit English limit sentence
scored 90.9%. The user's informal spatial wording scored 59.3%. These are model
scores, not measured accuracy. Differences point to representation sensitivity
of word/character TF-IDF + logistic regression, not a PostgreSQL storage failure.
No semantic math parser or shorthand-to-LaTeX conversion exists in the classifier.
No model, threshold, dataset or training labels were changed in this step.

Verified in the offline browser harness: Ctrl+V creates an image attachment with
thumbnail, a second paste cannot silently replace it, removal works, and plain
math text pastes normally. Production frontend build and git diff whitespace
checks passed. No real upload or paid API request was made during verification.

Recommended future work: shared math-notation normalization during training and
inference, reviewed shorthand/typo/LaTeX examples, and group-separated evaluation
on real inputs. Preserve variable case, bounds, grouping and original messages.
Do not lower thresholds simply to hide uncertainty.

## 2026-09-21 — Blue chat interface and bounded conversation memory

Implemented conversational layout, saved chat navigation, Markdown/LaTeX,
multipart attachments with captions, per-turn classification scores, OpenAI
subject/final-answer comparison, and separately attributed reference answers.
Follow-ups now send stored context. Added owner-only streaming gzip exports;
all original messages remain intact.

One structured Responses call returns answer, subject, final answer and memory.
Context includes complete recent turns within 12,000 history characters and a
maximum 3,000-character memory snapshot. Disabled automatic SDK retries, added
a process-local solve throttle and existing-conversation lease, and corrected
rotated JWT refresh handling. See docs/chat.md for limits and future work.

Applied migration 0004 to local PostgreSQL. Added OpenAI SDK dependency pins to
the local lockfile. Initial checks: 40 backend tests passed, production frontend
build passed, no migration drift, and git diff whitespace checks passed. The
offline browser harness verified equations, chat layout and follow-ups. No paid
provider calls were made. Final checks are recorded below.

Final verification: 40 tests passed after the pagination optimization. Compatible
npm security patches were applied (no forced major upgrades). Four audit findings
remain in the existing Vite/esbuild and React Router dependency families; their
major upgrades remain a before-hosting task. Frontend bundling also reports a
large KaTeX/Markdown JavaScript chunk; code splitting is future optimization.

Older work-log entries describe their original checkpoint. Their remaining-work
lists are historical; docs/chat.md describes the current conversation behavior.

## 2026-09-21 — Repository organization, local classifier and data foundation

### User request and decisions

Organize the Desktop MathApp project, train the classifier from the newly supplied
1,000-row CSV, and establish its data structure. Work locally in stages. The user
asked that work be recorded in Markdown for future Codex sessions and requested
compact scripted dataset checks rather than reading every row into model context.

The planned audience is an owner/admin and invited testers, with a total future
hosting/API budget of $10–20 monthly. No deployment or paid API calls occurred.

### Folder changes

- Kept active `backend/` and `frontend/` paths stable.
- Moved older `agent/`, `django/`, `deepseek/`, `engines/`, `converters_to_str/`,
  `camera.py`, `pipeline.py`, and `pdf_jason.py` together into `legacy/`.
- Moved original `pdf/`, `screenshots/`, and `jason/` into `data/samples/`.
- Moved the supplied CSV from `csv/` to `data/raw/`; file contents preserved.
- Added `ml/src/mathapp_ml/`, `models/`, `docs/`, `scripts/`, and `tests/`.
- Updated ignore rules for private datasets, model artifacts, runtime databases,
  credentials, virtual environments and frontend dependencies.

### Dataset and baseline

- File: `data/raw/math_subject_classifier_en_1000.csv`.
- Original SHA-256: `ab382497223ff83c72de81844fc785ae6e8e8771fd93ddfb4b44c50199cb1d65`.
- Rows: CALCULUS 333, PROBABILITY 333, DISCRETE 334.
- All examples are English, synthetic and pending review; no statuses were
  promoted to approved. Automated schema checks found no missing values,
  duplicate IDs or duplicate normalized questions.
- First model: `models/baseline-v1/classifier.joblib`.
- Features: word/character TF-IDF of question text only; logistic regression.
- Split: 599 training, 201 validation, 200 held-out test rows. Declared groups and
  number-only variant fingerprints stay within one partition. The current audit
  finds 1,000 effective groups, which does not prove absence of paraphrases.
- Candidate selected using validation macro F1; test accuracy 193/200 = 96.5%,
  test macro F1 about 0.9651. This is raw top-label accuracy on synthetic examples,
  before inference rejection thresholds. It is not a production accuracy claim.
- Correct held-out predictions by label: calculus 67/67, probability 65/66,
  discrete 61/67. The confusion matrix and full metrics are in `report.json`.
- Candidates never overwrite existing versions. Training does not happen on each
  request. Trusted artifacts load once per backend process and are reused.
- Development configuration selects baseline-v1. Experimental models are blocked
  when DEBUG=False. UNKNOWN thresholds are initial heuristics, not calibrated
  probabilities or an out-of-domain guarantee.

### PostgreSQL and import

- Initialized a dedicated password-protected local PostgreSQL 16.2 cluster at
  `data/runtime/postgres`, listening only on `127.0.0.1:55432`.
- Database: `mathapp`. Private connection settings are in `backend/.env`.
- `scripts/local_db.py` initializes/starts/stops only this project's cluster and
  refuses to overwrite an existing cluster or environment file.
- Applied the Django migrations and imported all 1,000 examples as pending in one
  transaction. Registered the baseline model's checksum and evaluation metadata.
- Added validated import, approved-only export, model registration and per-row
  Django admin review. Reimporting identical CSV bytes is a no-op; conflicting
  IDs/content reject the transaction. CSV claims of approval are not trusted.
- Added separate conversation, ordered message, extracted problem, classifier
  prediction, and safe operational-event records. Existing SolveHistory records
  remain supported. New successful solves populate both the compatibility history
  and conversation records, atomically. Full task text is no longer truncated.
- Provider/extraction failures are not saved as successful answers. Prediction
  records are not silently converted into training labels.
- Added authenticated `/api/solver/classify/` (local inference only), conversation
  listing and paginated message endpoints with ownership checks.
- Removed a credential-looking value from the tracked `.env.example`. If it was
  ever a valid provider key, the owner should rotate it; Git history still contains
  the old example. No credential value is recorded here and no rotation occurred.

### Verification

The isolated environment uses Python 3.12 and scikit-learn 1.7.2, with package
versions recorded in `requirements-local.lock`. Heavy OCR/provider dependencies
remain optional for database/classifier work. No paid calls were made.

Verified initially with SQLite (22 tests), then with real local PostgreSQL
(27 tests before final additional regression checks). PostgreSQL migrations and
the 1,000-row import succeeded. A CLI smoke test classified `Evaluate lim x->2 x^2`
as CALCULUS. Final verification results are recorded below after the last checks.

Final checks completed:

- 29 tests passed against local PostgreSQL, including review attribution,
  duplicate/conflicting imports, database constraints, ownership, full message
  preservation, error handling, model-load caching, and experimental-model gating.
- `manage.py check`: no issues. `makemigrations --check --dry-run`: no drift.
- `git diff --check`: passed.
- Database verified as PostgreSQL with 1,000 pending examples, one dataset import
  and one candidate model version. No permanent user accounts were created.
- All 43 moved original files are byte-for-byte identical to their Git originals.
  The supplied CSV checksum also remains unchanged.
- Question identity hashes preserve mathematical variable case and superscripts;
  initial local hashes were refreshed after that correction. No question text or
  labels were changed. Numeric template grouping remains a separate heuristic.
- The local PostgreSQL service remains running on loopback. The Django and React
  development servers were not started. No Git commit, push or hosted deployment
  was performed.

### Boundaries and remaining work

1. Independently review labels and collect real held-out questions. Do not claim
   real-world or Macedonian accuracy from this English synthetic dataset.
2. Finalize owner/invited-tester access and server-side spend/rate/concurrency
   limits before exposing the app publicly. Public registration still exists.
3. Implement the agreed OpenAI solver migration and measured token/cost accounting.
   DeepSeek remains the existing provider; no provider calls were tested live.
4. Add the frontend conversation/follow-up UX and deliberate context selection.
   The new API stores conversations but each solve currently uses only its task.
5. Define retention/deletion and private upload storage; verify backups/restores
   before a hosted launch. PostgreSQL database files must not be committed.
6. Migrate the compatibility SolveHistory data before removing duplicate storage.
7. Benchmark OCR choices against the actual input language and documents. The
   active image path is still EasyOCR; OCR packages were not installed here.
8. Select managed hosting/Neon later. Docker is optional and has not been added.

### How to resume

Read `AGENTS.md`, `README.md`, `docs/data-model.md`, and `docs/training.md`.
Use the existing `.venv`. Run `scripts/local_db.py status` and `start` if needed.
Run Django checks, migration drift checks and pytest before further data changes.
Create an admin account locally using `backend/manage.py createsuperuser` when
the owner is ready; no user or shared default password has been created.
