#!/bin/bash
cd "$(dirname "$0")"
if [ ! -f .env ]; then cp .env.example .env; fi
python3 app.py
