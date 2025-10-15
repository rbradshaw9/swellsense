#!/bin/bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --break-system-packages
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
