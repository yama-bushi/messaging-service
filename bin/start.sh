#!/bin/bash
set -euo pipefail

echo "Starting the application..."
echo "Environment: ${ENV:-development}"

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

echo "Application started successfully!"