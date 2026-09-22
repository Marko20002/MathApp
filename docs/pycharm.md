# Run MathApp in PyCharm

This project has two applications: the Django API and the React/Vite frontend.
Open the repository folder itself, `/home/marko/Desktop/MathApp`, as one PyCharm
project. Do not open `backend/` alone, because imports also use `ml/src/`.

## One-time setup

1. In **Settings → Project → Python Interpreter**, select the existing interpreter:
   `/home/marko/Desktop/MathApp/.venv/bin/python`.
2. Mark `backend` and `ml/src` as **Sources Root** in the Project panel. This makes
   imports such as `core.pipeline` and `mathapp_ml` resolve in the editor.
3. In the PyCharm terminal, from the repository root, verify the database:

   ```bash
   .venv/bin/python scripts/local_db.py status
   .venv/bin/python backend/manage.py migrate
   ```

   If status says it is stopped, use `scripts/local_db.py start`. It starts only
   the private PostgreSQL database stored in `data/runtime/` on this computer.
4. Copy values only into `backend/.env`; this file is private and ignored by Git.
   Add `OPENAI_API_KEY=...` there only when you are ready to make a paid test.

## PyCharm run configurations

Create these two configurations. Set **Working directory** to
`/home/marko/Desktop/MathApp` for both.

| Name | Type | Script / command | Arguments |
|---|---|---|---|
| Django API | Python | `backend/manage.py` | `runserver 127.0.0.1:8002` |
| Vite frontend | npm | `frontend/package.json` | `run dev` |

Start **Django API**, then **Vite frontend**. Open the local Vite URL shown in the
Run panel (normally `http://localhost:3001`). The Vite development proxy forwards
`/api` calls to Django at port 8002, so the browser does not need an API URL or an
OpenAI key.

For local manual testing, create an owner account once:

```bash
.venv/bin/python backend/manage.py createsuperuser
```

Then use the app to register/login or use `/ms-admin-panel/` for dataset review.
Do not use a real provider key in test code. The automated tests mock OpenAI.

## Checks before and after edits

Run these from PyCharm's terminal. They do not call OpenAI:

```bash
.venv/bin/python backend/manage.py check
.venv/bin/python backend/manage.py makemigrations --check --dry-run
.venv/bin/pytest -q
npm --prefix frontend run build
git diff --check
```

To test a real solve, add a key to `backend/.env`, restart the Django run
configuration, log in locally, and submit one small math question. The response
is saved to your local PostgreSQL database and the token counts are saved in
`SolveEvent`; the API key is not stored.

## View PostgreSQL inside PyCharm

First make sure the project database is running and its migrations are applied:

```bash
.venv/bin/python scripts/local_db.py start
.venv/bin/python backend/manage.py migrate
```

Open **View → Tool Windows → Database**, click **+**, and choose
**Data Source → PostgreSQL**. Configure the source as follows:

| Field | Local value |
|---|---|
| Name | `MathApp Local` |
| Host | `127.0.0.1` |
| Port | `55432` |
| Database | `mathapp` |
| User | `mathapp` |
| Password | Read it from the private `DATABASE_URL` in `backend/.env` |

The JDBC URL should become `jdbc:postgresql://127.0.0.1:55432/mathapp`.
If PyCharm offers **Download missing driver files**, accept it, then click
**Test Connection**. After a successful test, select the `public` schema and
click **OK**. Expand `MathApp Local → mathapp → public → tables` to inspect the
Django tables. Use the table viewer for inspection; edit application data through
the app or Django admin so validation and ownership rules still run.
