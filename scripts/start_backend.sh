#!/bin/bash

PROJECT_DIR="/d/novotel-rag-agent"
ENV_PATH="/d/novotel-rag-agent/novotel-rag"
LOG_FILE="$PROJECT_DIR/backend/logs/rag_system"
PID_FILE="$PROJECT_DIR/backend/logs/backend.pid"

echo "======================================"
echo "🚀 Starting NovaTel Backend"
echo "======================================"

cd "$PROJECT_DIR" || exit

# initialize conda for Git Bash
source ~/miniconda3/etc/profile.d/conda.sh

# activate correct env
conda activate "$ENV_PATH"

echo "✅ Conda environment activated"

nohup uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  >> "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"

echo "Backend running at http://localhost:8000."