#!/bin/bash

set -e

echo "Starting the application..."
echo "Environment: ${ENV:-development}"

# Add your application startup commands here

set -euo pipefail

uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload


echo "Application started successfully!" 