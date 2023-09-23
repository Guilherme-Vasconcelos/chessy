#!/usr/bin/env bash

# Stop if any commands fail.
set -e

poetry run black .
poetry run ruff --fix .
poetry run mypy .
poetry run pytest
