#!/bin/bash
# Activate virtual environment and run the command
cd "$(dirname "$0")"
source venv/bin/activate
exec "$@"