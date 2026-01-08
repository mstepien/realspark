#!/bin/bash

# Exit on error
set -e

echo "Generating Python models..."
CODEGEN_BIN="./venv/bin/datamodel-codegen"

if [ ! -f "$CODEGEN_BIN" ]; then
    echo "datamodel-codegen not found at $CODEGEN_BIN. Attempting to install..."
    ./venv/bin/pip install datamodel-code-generator
fi

if [ -f "$CODEGEN_BIN" ]; then
    if ! "$CODEGEN_BIN" --input openapi.yaml --output app/models.py; then
        echo "Error: Python model generation failed. Check openapi.yaml for syntax errors."
        exit 1
    fi
else
    echo "Error: Could not find or install datamodel-codegen. Please check your venv."
    exit 1
fi

echo "Generating JavaScript client SDK..."
npx @openapitools/openapi-generator-cli generate \
    -i openapi.yaml \
    -g javascript \
    -o app/static/js/client \
    --additional-properties=useES6=true

echo "API Generation Complete!"
