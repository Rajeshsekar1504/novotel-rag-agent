#!/bin/bash

LOG_DIR="/d/novotel-rag-agent/backend/logs"

echo "Stopping services..."

if [ -f "$LOG_DIR/backend.pid" ]; then
  kill $(cat "$LOG_DIR/backend.pid") 2>/dev/null
  rm "$LOG_DIR/backend.pid"
  echo "Backend stopped"
fi

if [ -f "$LOG_DIR/frontend.pid" ]; then
  kill $(cat "$LOG_DIR/frontend.pid") 2>/dev/null
  rm "$LOG_DIR/frontend.pid"
  echo "Frontend stopped"
fi