#!/usr/bin/env bash

# Stop if any commands fail.
set -e

poetry run ruff format .
poetry run ruff --fix .
poetry run mypy .
poetry run pytest
