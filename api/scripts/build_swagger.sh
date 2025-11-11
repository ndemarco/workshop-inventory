#!/usr/bin/env bash
set -euo pipefail

# Build script for generating a development OpenAPI JSON
# Intended to be run from the project root as:
#   ./api/scripts/build_swagger.sh
# or from inside the api/scripts directory.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# project root is two levels up from api/scripts
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "Generating OpenAPI JSON (development)..."
PYTHONPATH="$ROOT_DIR/api" python3 "$SCRIPT_DIR/generate_openapi.py"

echo "Done. openapi.json written to ui/dist/openapi.json"
