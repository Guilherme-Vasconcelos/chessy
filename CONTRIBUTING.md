## Building and running
1. Create a venv with `python -m venv .venv`. The exact Python required version can be found at
[pyproject.toml](./pyproject.toml).
2. Install [poetry](https://python-poetry.org/) and run `$ poetry install` to install dependencies.
3. Run it with `$ poetry run chessy` or manually with `$ .venv/bin/activate` followed by `$ python -m chessy.core`.
    - To increase log level (useful for debugging), use the `--debug` flag (`-d` for short), e.g.: `$ poetry run chessy -d`.

## Development utils
- If you're using VSCode, we have a [.vscode](./.vscode) with recommended extensions / settings,
and launch profiles.
- Alternatively, use [tools/format_lint_test.bash](./tools/format_lint_test.bash) to run all available lints.
Check the script source code if you want to run any of these lints separately.
