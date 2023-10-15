# cheese
A simple chess engine.

## Getting started
1. Create a venv with `python -m venv .venv`.
2. Install [poetry](https://python-poetry.org/) and run `$ poetry install` to install dependencies.
3. Run it with `$ poetry run cheese` or manually with `$ .venv/bin/activate` followed by `$ python -m cheese`.

## Development utils
- If you're using VSCode, we have a [.vscode](./.vscode) with recommended extensions / settings,
and launch profiles.
- Alternatively, use [tools/format_lint_test.bash](./tools/format_lint_test.bash) to run all available lints.
Check the script source code if you want to run any of these lints separately.

## License
cheese is licensed under the GNU Affero General Public License, either version 3 or any later versions
at your choice. See [LICENSE.txt](./LICENSE.txt) for more details.
