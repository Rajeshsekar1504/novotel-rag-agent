#!/bin/bash

echo "Restarting system..."

./scripts/stop.sh
sleep 2
./scripts/start_backend.sh
./scripts/start_frontend.sh

echo "Restart complete"