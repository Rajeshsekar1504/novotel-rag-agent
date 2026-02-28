#!/bin/bash

PROJECT_DIR="/d/novotel-rag-agent/frontend"
LOG_FILE="/d/novotel-rag-agent/backend/logs/rag_system"
PID_FILE="/d/novotel-rag-agent/backend/logs/frontend.pid"

echo "🎨 Starting Frontend"

cd "$PROJECT_DIR" || exit

if [ ! -d "node_modules" ]; then
  npm install
fi

nohup npm run dev >> "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"

echo "Frontend running at http://localhost:5175/"