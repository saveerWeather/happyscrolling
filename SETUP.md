# Setup Instructions

## Local Development

### 1. Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies
```bash
cd frontend
npm install
cd ..
```

### 3. Create Environment Files

**Root `.env` file:**
```bash
GMAIL_USER=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
CHECK_INTERVAL=30
DATABASE_URL=sqlite:///feed.db
JWT_SECRET=any-random-string-here
CORS_ORIGINS=http://localhost:3000
```

**`frontend/.env` file:**
```bash
NUXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run Everything

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Terminal 3 - Worker (optional, for email processing):**
```bash
cd backend
python worker.py
```

### 5. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Railway Deployment

### Step 1: Create Railway Project
1. Go to [railway.app](https://railway.app)
2. Create new project
3. Connect your GitHub repo

### Step 2: Add PostgreSQL Database
1. In Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create `DATABASE_URL` environment variable

### Step 3: Create Backend API Service
1. Click "New" → "GitHub Repo" (select same repo)
2. In service settings:
   - **Root Directory**: `/backend`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
3. Add environment variables:
   - `JWT_SECRET` = (generate a random string)
   - `GMAIL_USER` = your email
   - `GMAIL_PASSWORD` = your app password
   - `CHECK_INTERVAL` = 30
   - `CORS_ORIGINS` = (you'll set this after frontend is deployed)
   - `DATABASE_URL` = (auto-set by Railway from PostgreSQL service)
4. Copy the service URL (e.g., `https://backend-xxxx.railway.app`)

### Step 4: Create Worker Service
1. Click "New" → "GitHub Repo" (select same repo)
2. In service settings:
   - **Root Directory**: `/backend`
   - **Start Command**: `python worker.py`
3. Add same environment variables as Backend API (except CORS_ORIGINS)

### Step 5: Create Frontend Service
1. Click "New" → "GitHub Repo" (select same repo)
2. In service settings:
   - **Root Directory**: `/frontend`
   - **Start Command**: `npm run build && npm run preview -- --port $PORT --host 0.0.0.0`
3. Add environment variable:
   - `NUXT_PUBLIC_API_URL` = (your backend URL from Step 3)
4. Copy the frontend URL (e.g., `https://frontend-xxxx.railway.app`)

### Step 6: Update CORS
1. Go back to Backend API service
2. Update `CORS_ORIGINS` environment variable:
   - Set it to your frontend URL from Step 5

### Step 7: Deploy
Railway will automatically:
- Install dependencies
- Build and deploy
- Keep services running

### Step 8: Access Your App
- Visit your frontend URL
- Register an account
- Add email addresses in Settings
- Start receiving links!

---

## Quick Checklist

### Local:
- [ ] Created root `.env` file
- [ ] Created `frontend/.env` file
- [ ] Installed backend dependencies
- [ ] Installed frontend dependencies
- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000

### Railway:
- [ ] Created Railway project
- [ ] Added PostgreSQL database
- [ ] Created Backend API service (root: `/backend`)
- [ ] Created Worker service (root: `/backend`)
- [ ] Created Frontend service (root: `/frontend`)
- [ ] Set all environment variables
- [ ] Updated CORS_ORIGINS with frontend URL
- [ ] All services deployed and running

