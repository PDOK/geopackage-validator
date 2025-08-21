#!/bin/sh
set -e

# auto-activate venv
. /code/venv/bin/activate

pip install .[test]

echo "🐍 Using Python: $(python --version)"
echo "📦 Pip from: $(which pip)"

# run whatever was passed in (default: shell)
exec "$@"
