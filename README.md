# cheese
A simple chess engine.

This is a learning project. It is not as fast as other production-ready engines and may have bugs, but
feel free to contribute if you wish to. Some of the planned features include:

- Improve move evaluation and search (quiescence search, optimize performance, etc.)
- UCI support
- Lichess integration

Since it doesn't have support for UCI yet, it doesn't do much at the moment. You can pass it a FEN
as a CLI argument, and it will play a game against itself starting from that FEN. Alternatively, if you
simply evoke it with `poetry run cheese`, it will start a game from the traditional starting position.

## Getting started
1. Create a venv with `python -m venv .venv`. The exact Python required version can be found at
[pyproject.toml](./pyproject.toml).
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
