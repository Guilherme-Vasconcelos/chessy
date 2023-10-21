# cheese
A simple chess engine.

This is a learning project. It is much slower than other production-ready engines and may have bugs, but
feel free to contribute if you wish to.

## Features

- Minimal UCI support

## Planned features

- Improve move evaluation and search (quiescence search, optimize performance, etc.)
- Increase UCI support (report more information, allow some level of customization through options, etc.)
- Lichess integration

## Getting started
1. Create a venv with `python -m venv .venv`. The exact Python required version can be found at
[pyproject.toml](./pyproject.toml).
2. Install [poetry](https://python-poetry.org/) and run `$ poetry install` to install dependencies.
3. Run it with `$ poetry run cheese` or manually with `$ .venv/bin/activate` followed by `$ python -m cheese.core`.
    - If you are trying to debug some problem, you can use the `--debug` (`-d` for short) flag to increase log level: `$ poetry run cheese -d`.

## Development utils
- If you're using VSCode, we have a [.vscode](./.vscode) with recommended extensions / settings,
and launch profiles.
- Alternatively, use [tools/format_lint_test.bash](./tools/format_lint_test.bash) to run all available lints.
Check the script source code if you want to run any of these lints separately.

## License
cheese is licensed under the GNU Affero General Public License, either version 3 or any later versions
at your choice. See [LICENSE.txt](./LICENSE.txt) for more details.
