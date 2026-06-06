# Simple File Helper — AI Agent Instructions

> Full development plan: [simple-file-helper-dev-plan.html](./simple-file-helper-dev-plan.html)

## What This Project Is

A web-based document converter for elderly users. Upload a PDF bank statement, CSV, or Excel file → Gemini AI extracts transactions → auto-downloads a 2-tab Excel workbook (.xlsx). Zero frameworks on the frontend, synchronous processing on the backend.

## Tech Stack

| Layer | Choice |
|-------|--------|
| Backend | Python 3.11+ / FastAPI / Uvicorn |
| Database | SQLite via SQLAlchemy (2 tables: `users` + `jobs`) |
| AI | Gemini 1.5 Flash (free tier) via `google-generativeai` |
| File output | openpyxl (2-tab Excel: Summary + Data) |
| Frontend | Plain HTML + vanilla JS (Fetch API), Tabler Icons CDN |
| Auth | JWT via python-jose + passlib[bcrypt] |
| Templates | Static `.json` files in `backend/templates/`, loaded at startup |

## Run Commands

```bash
# Setup (one-time)
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python seed.py               # Creates tables + default admin (admin / changeme123)

# Run
uvicorn main:app --host 0.0.0.0 --port 8000

# Open: http://localhost:8000/app/index.html
```

## Architecture — Critical Design Decisions

### 1. Synchronous Processing (no polling, no background tasks)
The `POST /process` endpoint is blocking. The browser sends file (PDF/CSV/Excel) + template name in one request, waits (5–20s for Gemini), and receives the `.xlsx` file as the response. The frontend uses a single `fetch()` call with a full-screen spinner. No job IDs, no status polling, no state machine.

**Why:** Gemini 1.5 Flash is fast enough. A browser `fetch()` handles the wait. Background workers only matter with concurrent users — this app is single-user/office use.

### 2. Templates Are JSON Files, Not Database Rows
Templates live as `.json` files in `backend/templates/`. On startup, `main.py` reads them all into an in-memory `TEMPLATES` dict. The `GET /templates` endpoint returns that dict. Adding a template = drop a `.json` file + restart.

**Template JSON format** — see the dev plan for full example, but key fields:
- `name`, `category`, `icon`, `gemini_prompt`
- `columns[]`: `{key, label, type, width}` — maps Gemini output to Excel columns
- `summary_metrics[]`: `{label, column, agg}` — for the Summary tab

### 3. Only Two DB Tables
- **users**: id, username, email, password_hash, role (admin/user), settings_json, created_at
- **jobs**: id, user_id, template_name (plain string, not FK), original_filename, output_excel_path, rows_extracted, created_at

No `templates` table. No `status` column on jobs (a record is only written on success).

### 4. No Admin Panel
Admin functions (user management) are handled inline. No `admin.html` / `admin.js`. Only two pages: `index.html` (login) and `app.html` (main app).

## API Endpoints (10 total)

| Method | Route | Purpose |
|--------|-------|---------|
| POST | `/auth/login` | Login, returns JWT |
| GET | `/auth/me` | Current user info |
| PUT | `/auth/change-password` | Change password |
| PUT | `/auth/settings` | Save user preferences |
| GET | `/templates` | List all templates (from JSON files) |
| POST | `/process` | Upload file (PDF/CSV/Excel) → Excel (sync, blocking) |
| GET | `/jobs` | User's job history (paginated) |
| GET | `/jobs/all` | Admin: all users' jobs |
| GET | `/download/{job_id}` | Re-download past Excel output |

## File Structure

```
simple-file-helper/
├── backend/
│   ├── main.py              # FastAPI entry — routers + static files
│   ├── config.py            # .env settings
│   ├── database.py          # SQLite connection
│   ├── seed.py              # Create tables + default admin
│   ├── templates/           # JSON template files (loaded at startup)
│   ├── models/              # SQLAlchemy: user.py, job.py
│   ├── schemas/             # Pydantic: user.py, job.py
│   ├── routers/             # auth.py, templates.py, process.py, history.py
│   ├── services/            # gemini.py, excel.py
│   ├── outputs/             # Saved .xlsx files for re-download
│   └── requirements.txt
├── frontend/
│   ├── index.html           # Login page
│   ├── app.html             # Main app
│   ├── css/style.css
│   └── js/                  # api.js, auth.js, app.js
├── .env
└── start.bat                # Windows one-click startup
```

## UX Conventions (Elder-Friendly)

- **18px minimum font**, 48px minimum button height
- **Color-coded actions**: amber = action, green = success, red = error
- **Single-focus screens** — no split attention
- **No hover-only interactions** — everything visible at all times
- **Clear empty states** with instructional text
- **Full-screen spinner** during processing (no progress bar needed)

## Key Patterns

- Auth: JWT stored in `localStorage`, added via `api.js` helper. Redirect to login on 401.
- File download: `fetch()` gets blob → `URL.createObjectURL()` → programmatic `<a>` click → revoke
- Template lookup: `TEMPLATES.get(template_name)` — templates are loaded once at startup
- Gemini call: for PDFs, base64-encode bytes and send as `inline_data` with mime type + prompt. For CSV/Excel, read as text/bytes and include directly in the prompt. Parse JSON from response (strip markdown fences if present)
- Excel generation: single workbook, two sheets — Summary (styled header + metadata + computed totals) and Data (header row with template column labels + all rows, alternating shading, frozen top row)

## Dependencies (9 packages)

```
fastapi, uvicorn[standard], python-multipart, sqlalchemy,
python-jose[cryptography], passlib[bcrypt], google-generativeai,
openpyxl, python-dotenv
```

## What Was Removed (v1 → v2)

- `reportlab` (PDF generation) → replaced by Excel Summary tab
- `pdfplumber` (PDF pre-extraction) → Gemini reads PDFs natively
- `aiofiles` → no async file writes needed
- `admin.html`, `admin.js` → no admin panel
- `models/template.py`, `routers/templates.py` (CRUD) → JSON files instead
- Background task system + polling → synchronous processing
