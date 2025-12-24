#!/bin/bash
# Run worker from project root
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python backend/worker.py

