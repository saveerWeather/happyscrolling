# Happy Scrolling

A social media-style feed aggregator that extracts links from emails and displays them in a beautiful feed interface.

## Architecture

- **Backend**: FastAPI (Python) - REST API with JWT authentication
- **Frontend**: Nuxt 3 (Vue.js) with SSR and Tailwind CSS
- **Worker**: Email processor that monitors Gmail and extracts links
- **Database**: PostgreSQL (production) / SQLite (local)

## Project Structure

```
happyscrolling/
├── backend/              # Python FastAPI application
│   ├── app.py           # FastAPI app entry point
│   ├── worker.py        # Email processing worker
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas
│   ├── config.py        # Configuration
│   ├── routes/          # API routes
│   └── utils/           # Utilities
├── frontend/            # Nuxt 3 application
│   ├── pages/          # Route pages
│   ├── components/     # Vue components
│   ├── composables/    # Composables
│   ├── stores/         # Pinia stores
│   └── utils/          # Utilities
└── Procfile            # Railway deployment config
```

## Setup

### Backend

1. Install dependencies:
```bash
cd backend
pip install -r ../requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL="postgresql://..."
export JWT_SECRET="your-secret-key"
export GMAIL_USER="your-email@gmail.com"
export GMAIL_PASSWORD="your-app-password"
export CORS_ORIGINS="http://localhost:3000"
```

3. Run the API:
```bash
cd backend
uvicorn app:app --reload --port 8000
```

4. Run the worker (in separate terminal):
```bash
cd backend
python worker.py
```

### Frontend

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set environment variables:
```bash
export NUXT_PUBLIC_API_URL="http://localhost:8000"
```

3. Run development server:
```bash
npm run dev
```

## Railway Deployment

The project is configured for Railway with three services in one project:

1. **Backend API Service**: FastAPI application (Root: `/backend`)
2. **Worker Service**: Email processor (Root: `/backend`)
3. **Frontend Service**: Nuxt SSR application (Root: `/frontend`)

### Setting Up Services on Railway

1. Create a new Railway project
2. Add three services:
   - **Backend API**: Connect to repo, set root directory to `/backend`
   - **Worker**: Connect to same repo, set root directory to `/backend`  
   - **Frontend**: Connect to same repo, set root directory to `/frontend`

3. For each service, set the start command:
   - **Backend API**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Worker**: `python worker.py`
   - **Frontend**: `npm run build && npm run preview -- --port $PORT --host 0.0.0.0`

### Environment Variables

Set these in Railway for each service:

**Backend API & Worker:**
- `DATABASE_URL` - PostgreSQL connection string (auto-provided by Railway)
- `JWT_SECRET` - Secret key for JWT tokens (generate a strong random string)
- `GMAIL_USER` - Gmail account to monitor
- `GMAIL_PASSWORD` - Gmail app password
- `CORS_ORIGINS` - Comma-separated list of allowed origins (include your frontend URL)
- `CHECK_INTERVAL` - Email check interval in seconds (default: 30)

**Frontend:**
- `NUXT_PUBLIC_API_URL` - Backend API URL (e.g., `https://your-backend.railway.app`)

### Procfile (for local development)

Root Procfile:
```
web: cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT
worker: cd backend && python worker.py
```

Frontend Procfile (for Railway):
```
web: npm run build && npm run preview -- --port $PORT --host 0.0.0.0
```

## Features

- ✅ User registration and authentication (JWT)
- ✅ Email link extraction from Gmail
- ✅ Link preview generation (Open Graph metadata)
- ✅ Social media-style feed interface
- ✅ Email address linking (users can link multiple emails)
- ✅ Pagination and infinite scroll
- ✅ Responsive design with Tailwind CSS

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### Feed
- `GET /api/feed` - Get user's feed (paginated)
  - Query params: `page`, `limit`, `email` (filter)

### Settings
- `GET /api/settings/emails` - Get linked emails
- `POST /api/settings/emails` - Add linked email
- `DELETE /api/settings/emails/{id}` - Remove linked email

## Development

### Database Migrations

The app uses SQLAlchemy with auto-creation. For production, consider using Alembic for migrations.

### Adding Link Previews

Link previews are automatically generated when emails are processed. The worker fetches Open Graph metadata and stores it in the database.

## License

MIT

