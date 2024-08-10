#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$BASH_SOURCE")")"
set -e

echo "Preparing venv ..."
poetry build

python -m venv venv
source venv/bin/activate
pip install dist/omlmd-*.whl

echo "Running E2E test for CLI ..."

omlmd push localhost:5001/mmortari/mlartifact:v1 README.md --metadata tests/data/md.json --plain-http

omlmd pull localhost:5001/mmortari/mlartifact:v1 -o tmp/a --plain-http
file_count=$(find "tmp/a" -type f | wc -l)
if [ "$file_count" -eq 3 ]; then
    echo "Expected 3 files in $DIR, ok."
else
    echo "I was expecting 3 files in $DIR, FAIL."
    exit 1
fi

omlmd pull localhost:5001/mmortari/mlartifact:v1 -o tmp/b --media-types "application/x-mlmodel" --plain-http
file_count=$(find "tmp/b" -type f | wc -l)
if [ "$file_count" -eq 1 ]; then
    echo "Expected 1 files in $DIR, ok."
else
    echo "I was expecting 1 files in $DIR, FAIL."
    exit 1
fi

omlmd get config localhost:5001/mmortari/mlartifact:v1 --plain-http
omlmd crawl localhost:5001/mmortari/mlartifact:v1 localhost:5001/mmortari/mlartifact:v1 --plain-http | jq .
omlmd crawl --plain-http \
    localhost:5001/mmortari/mlartifact:v1 \
    localhost:5001/mmortari/mlartifact:v1 \
    localhost:5001/mmortari/mlartifact:v1 \
    | jq "max_by(.config.customProperties.accuracy).reference"

deactivate
