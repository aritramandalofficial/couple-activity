# Together: Couple Activity Tracker (modular v2)

## Installation (Windows / VS Code)

Extract this ZIP into your existing `COUPLE_ACTIVITY` project folder, replacing Python files.
**Back up and KEEP your existing `couple_activity.db`**; the ZIP intentionally does not include one.
Keep your `venv` as well. Stop Streamlit before replacing files.

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m streamlit run app.py
```

## Architecture

- `app.py`: navigation and delegation only.
- `auth.py`, `partners.py`, `profile.py`: accounts, link requests and sharing switches.
- `database.py`: SQLite connection, migrations, and server-side access checks.
- `repositories/*_repository.py`: database queries / writes for each tracker.
- `pages/*.py`: simple forms and wiring each repository to its view.
- `ui/*_view.py`: chart and table rendering; edit here for UI-only changes.
- `ui/shared.py`: common dataframe and privacy-status display helpers.

After both people accept the connection request, histories are visible both ways, unless a user subsequently disables sharing. Weight and mood have a **single combined two-person chart/table**; notes and periods have combined histories. Existing history is included. Disconnection revokes access.

**Existing partner pairs:** If connected before sharing-all was added, each should visit Privacy & Profile and choose `Share all four histories with partner` to opt in.

**Privacy:** This is a local prototype. It uses email/password signups without email verification, password recovery, login rate limiting or a managed security boundary. Do not expose this version publicly or enter sensitive production health data. Hosting on a single Streamlit server allows separate browser sessions to share the same SQLite DB. Two independent installations do not synchronize.
