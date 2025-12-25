# Railway Deployment Troubleshooting

## 502 Bad Gateway Error

If you're seeing 502 errors, it means Railway's edge server can't reach your backend service. The backend application isn't running or isn't responding.

### 1. Check Deployment Logs (MOST IMPORTANT)
- Go to your backend service in Railway
- Click on "Deployments" tab
- Click on the latest deployment
- Click "View Logs" or "View Build Logs"
- **Look for**:
  - "Starting FastAPI application..."
  - "App imported successfully"  
  - "Starting server on port XXXX"
  - Any Python errors or tracebacks
- **If you see errors**, that's why it's not starting

### 2. Verify Start Command
- Go to your backend service → **Settings** → **Deploy** tab
- Check the **Start Command** field
- It should be: `python main.py`
- OR: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Make sure there are no typos

### 2. Start Command
Verify your start command in Railway:
- Go to your backend service → Settings → Deploy
- **Start Command** should be: `python main.py`
- OR: `uvicorn app:app --host 0.0.0.0 --port $PORT`

### 3. Root Directory
- Go to Settings → Source
- **Root Directory** should be: `/backend`

### 4. Port Configuration
- Railway automatically sets the `PORT` environment variable
- Your app should listen on `0.0.0.0:$PORT`
- The `main.py` file handles this automatically

### 5. Check Logs
- Go to your backend service → Deployments → Latest deployment → View Logs
- Look for:
  - "Starting FastAPI application..."
  - "App imported successfully"
  - "Starting server on port XXXX"
  - Any error messages

## CORS Issues

### Verify CORS_ORIGINS Environment Variable
1. Go to your backend service → Variables
2. Ensure `CORS_ORIGINS` is set to: `https://frontend-production-8087.up.railway.app`
3. **Important**: No spaces, exact URL match
4. After updating, redeploy the service

### Test CORS Configuration
1. Visit: `https://backend-production-cc44d.up.railway.app/debug/cors`
2. This will show your CORS configuration
3. Check if your frontend origin is in the `configured_origins` list

### Check if Backend is Running
1. Visit: `https://backend-production-cc44d.up.railway.app/health`
2. Should return: `{"status": "healthy"}`
3. If you get 502, the backend isn't running (see 502 troubleshooting above)

## Common Issues

### Issue: "Nothing different in deploy logs"
- **Cause**: Backend might be crashing silently
- **Solution**: Check the logs more carefully, look for Python tracebacks
- The enhanced logging in `main.py` should help

### Issue: CORS works locally but not on Railway
- **Cause**: Different domains, Railway edge server interference
- **Solution**: 
  1. Ensure service type is "Web Service"
  2. Verify CORS_ORIGINS includes exact frontend URL
  3. Check that both services use HTTPS

### Issue: Backend starts but returns 502
- **Cause**: Railway edge server can't reach the backend
- **Solution**: 
  1. Verify the service is listening on `0.0.0.0:$PORT`
  2. Check that PORT environment variable is set
  3. Ensure service type is "Web Service"

## Quick Checklist

- [ ] Backend service type is "Web Service"
- [ ] Root directory is `/backend`
- [ ] Start command is `python main.py` or `uvicorn app:app --host 0.0.0.0 --port $PORT`
- [ ] `CORS_ORIGINS` environment variable is set correctly
- [ ] `CORS_ORIGINS` matches your frontend URL exactly (no trailing slash)
- [ ] Both services are using HTTPS
- [ ] Backend health endpoint returns 200: `/health`
- [ ] Backend debug endpoint works: `/debug/cors`

## Testing Steps

1. **Test backend health**:
   ```bash
   curl https://backend-production-cc44d.up.railway.app/health
   ```
   Should return: `{"status": "healthy"}`

2. **Test CORS preflight**:
   ```bash
   curl -X OPTIONS https://backend-production-cc44d.up.railway.app/api/auth/login \
     -H "Origin: https://frontend-production-8087.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -v
   ```
   Should return 200 with CORS headers

3. **Check Railway logs**:
   - Look for CORS-related log messages
   - Check for any Python errors or tracebacks

