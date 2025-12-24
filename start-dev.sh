#!/bin/bash

# Start backend and frontend in separate terminals
# Usage: ./start-dev.sh

echo "Starting development servers..."
echo ""
echo "Backend will run on: http://localhost:8000"
echo "Frontend will run on: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Start backend in background
cd backend
uvicorn app:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend in background
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait for user to stop
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM
wait

