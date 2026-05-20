# KOSH Saving App

KOSH Saving App is a cooperative monthly saving management system for managing members, monthly contributions, approvals, reports, and Google-based authentication.

The app uses a Next.js frontend, FastAPI backend, Google OAuth login, Google Sheets for data storage, and Google Drive for uploaded receipt/photo storage.

---

## Features

- Google Sign-In authentication
- Member management
- Monthly saving submission
- Receipt/photo upload support
- Admin approval and rejection flow
- Member-wise total paid tracking
- Monthly reports
- Protected dashboard routes
- Google Sheets data storage
- Google Drive file storage

---

## Tech Stack

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- TanStack React Query
- Google OAuth

### Backend

- FastAPI
- Python
- uv
- Google Sheets API
- Google Drive API
- JWT authentication

### Deployment

- Vercel for frontend
- Render for backend
- Google Sheets as the database
- Google Drive for receipt/photo storage

---

## Project Structure

```txt
coop-saving-app/
├── apps/
│   ├── api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routes/
│   │   │   ├── services/
│   │   │   └── core/
│   │   ├── pyproject.toml
│   │   └── uv.lock
│   │
│   └── web/
│       ├── app/
│       ├── components/
│       ├── lib/
│       ├── package.json
│       └── next.config.ts
│
├── .github/
│   └── workflows/
│       └── release.yml
│
└── README.md
```

---

## Google Sheet Setup

Create a Google Sheet with the following tabs.

### Members Sheet

Tab name:

```txt
Members
```

Headers:

```txt
Member ID | Name | Email | Phone | Role | Joined Date | Status | Total Paid
```

Example:

```txt
uuid | name surname | abc@gmail.com | 9800000000 | admin | 2026-05-20 | Active | 0
```

### Contributions Sheet

Tab name:

```txt
Contributions
```

Headers:

```txt
ID | Member Name | Month | Amount | Payment | Status | URL | Submitted_At | Approved_At | Approved_By | Remarks
```



---

## Local Backend Setup

Go to the backend folder:

```bash
cd apps/api
```

Install dependencies using uv:

```bash
uv sync
```

Run the backend:

```bash
uv run uvicorn app.main:app --reload --port 8000
```

Backend URL:

```txt
http://localhost:8000
```

API base URL:

```txt
http://localhost:8000/api
```

FastAPI docs:

```txt
http://localhost:8000/docs
```

---

## Local Frontend Setup

Go to the frontend folder:

```bash
cd apps/web
```

Install dependencies:

```bash
pnpm install
```

Run the frontend:

```bash
pnpm dev
```

Frontend URL:

```txt
http://localhost:3000
```

---

## Environment Variables

### Backend Environment Variables

Create this file:

```txt
apps/api/.env
```



For local development, `GOOGLE_SERVICE_ACCOUNT_FILE` can point to a local JSON file.

Do not commit this file:

```txt
service-account.json
```

### Frontend Environment Variables

Create this file:

```txt
apps/web/.env.local
```

Example for local development:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
```

Example for production:

```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com/api
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your_google_client_id.apps.googleusercontent.com
```

---

## Google OAuth Setup

Go to:

```txt
Google Cloud Console → APIs & Services → Credentials
```

Create or open your OAuth Client ID.

Add these to **Authorized JavaScript origins**:

```txt
http://localhost:3000
https://your-vercel-domain.vercel.app
https://your-custom-domain.com
```

Do not add paths.

Correct:

```txt
https://your-custom-domain.com
```

Wrong:

```txt
https://your-custom-domain.com/login
```

---

## Google Service Account Setup

1. Create a Google Cloud service account.
2. Enable the Google Sheets API.
3. Enable the Google Drive API.
4. Download the service account JSON file.
5. Share your Google Sheet with the service account email.
6. Share your Google Drive folder with the service account email.

The service account email looks like this:

```txt
something@project-id.iam.gserviceaccount.com
```

Give the service account editor access to the Google Sheet and Google Drive folder.

---




## Security Notes

- Never commit `.env` files.
- Never commit `service-account.json`.
- Store secrets in Render environment variables.
- Store frontend public variables only in Vercel.
- Google service account JSON belongs only on the backend.
- JWT secret belongs only on the backend.

---

## License

Private project for KOSH Saving members.
