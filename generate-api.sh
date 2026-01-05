#!/bin/bash

# Exit on error
set -e

echo "Generating Python models..."
if ! ./venv/bin/datamodel-codegen --input openapi.yaml --output app/models.py; then
    echo "datamodel-codegen not found. Installing..."
    ./venv/bin/pip install datamodel-code-generator
    ./venv/bin/datamodel-codegen --input openapi.yaml --output app/models.py
fi

echo "Generating JavaScript client SDK..."
npx @openapitools/openapi-generator-cli generate \
    -i openapi.yaml \
    -g javascript \
    -o app/static/js/client \
    --additional-properties=useES6=true

echo "API Generation Complete!"
