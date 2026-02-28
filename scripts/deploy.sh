#!/bin/bash

PROJECT_DIR="/d/novotel-rag-agent"
ENV_NAME="novotel-rag"

cd "$PROJECT_DIR" || exit

source ~/miniconda3/etc/profile.d/conda.sh
conda activate "$ENV_NAME"

echo "Installing backend dependencies..."
pip install -r backend/requirements.txt

echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

./scripts/ingest.sh
./scripts/start_backend.sh
./scripts/start_frontend.sh

echo "Deployment complete"