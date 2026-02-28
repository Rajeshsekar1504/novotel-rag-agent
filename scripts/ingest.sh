#!/bin/bash

PROJECT_DIR="/d/novotel-rag-agent"
ENV_PATH="/d/novotel-rag-agent/novotel-rag"
LOG_FILE="$PROJECT_DIR/backend/logs/rag_system"

echo "Running ingestion..."

cd "$PROJECT_DIR" || exit

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "$ENV_PATH"

python backend/rag/ingestor.py >> "$LOG_FILE" 2>&1

echo "Ingestion complete"