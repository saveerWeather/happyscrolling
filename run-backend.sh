#!/bin/bash
# Run backend - works from any directory
cd "$(dirname "$0")"
cd backend
python main.py
