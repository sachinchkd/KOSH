# COOP Saving App

A full-stack MVP for a small Nepal-style friendly saving/COOP group. It supports members, monthly NPR 1000 contribution entries, receipt/photo upload, admin approval, dashboard summaries, and optional Google Sheets + Google Drive sync.

## Stack

- Frontend: Next.js, React, TypeScript, pnpm, Tailwind CSS, shadcn-style local UI components, TanStack Query, Recharts
- Backend: FastAPI, uv, SQLAlchemy, Pydantic, Alembic-ready structure
- Database: SQLite for local development by default, PostgreSQL-ready for production
- Integrations: Google Sheets API and Google Drive API, optional via environment variables

## Project Structure

```txt
coop-saving-app/
├── apps/
│   ├── web/     # Next.js frontend
│   └── api/     # FastAPI backend
├── docker-compose.yml
├── pnpm-workspace.yaml
└── README.md
```

## 1. Backend Setup

```bash
cd apps/api
cp .env.example .env
uv sync
uv run python -m app.seed
uv run uvicorn app.main:app --reload
```

Backend will run at:

```txt
http://localhost:8000
```

API docs:

```txt
http://localhost:8000/docs
```

Default admin account after seeding:

```txt
Email: admin@coop.local
Password: admin12345
```

Eight sample members are also created. Their default password is:

```txt
member12345
```

## 2. Frontend Setup

Open another terminal:

```bash
cd apps/web
cp .env.example .env.local
pnpm install
pnpm dev
```

Frontend will run at:

```txt
http://localhost:3000
```

## 3. Run with PostgreSQL

Start PostgreSQL:

```bash
docker compose up -d postgres
```

In `apps/api/.env`, change:

```env
DATABASE_URL=postgresql+psycopg2://coop:coop_password@localhost:5432/coop_saving
```

Then seed again:

```bash
cd apps/api
uv run python -m app.seed
```

## 4. Google Sheets + Drive Setup

This app works without Google credentials. To enable Google sync:

1. Create a Google Cloud project.
2. Enable Google Sheets API and Google Drive API.
3. Create a Service Account.
4. Download the service account JSON file.
5. Create a Google Sheet with tabs:
   - `Contributions`
   - `Members`
   - `Monthly Summary`
6. Share the Google Sheet with the service account email.
7. Optional: create a Google Drive folder and share it with the service account email.

Set these in `apps/api/.env`:

```env
GOOGLE_ENABLED=true
GOOGLE_SHEET_ID=your_google_sheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=/absolute/path/to/service-account.json
GOOGLE_DRIVE_FOLDER_ID=your_drive_folder_id
```

The `Contributions` tab should have these columns:

```txt
ID | Member Name | Month | Amount | Payment Method | Status | Photo URL | Submitted At | Approved At | Approved By | Remarks
```

## 5. Main Features

- Login with JWT
- Admin/member roles
- Members list
- Add members as admin
- Submit monthly contribution
- Upload receipt/photo
- Admin approve/reject
- Dashboard totals
- Recent contributions
- Monthly chart
- Unpaid member list
- Optional append to Google Sheets
- Optional receipt upload to Google Drive

## 6. Useful Commands

Root:

```bash
pnpm dev:web
pnpm dev:api
```

Backend:

```bash
cd apps/api
uv run uvicorn app.main:app --reload
uv run python -m app.seed
```

Frontend:

```bash
cd apps/web
pnpm dev
pnpm build
```

## 7. Notes

For production, use PostgreSQL instead of SQLite and set a strong `SECRET_KEY` in the backend `.env` file.
