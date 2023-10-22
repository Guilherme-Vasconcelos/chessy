# chessy
A simple chess engine.

This is a learning project. It is much slower than other production-ready engines and may have bugs, but
feel free to contribute if you wish to.

## Features

- Minimal UCI support.
- Lichess integration (see [this repository](https://github.com/Guilherme-Vasconcelos/lichess-bot)).

## Getting started
1. Create a venv with `python -m venv .venv`. The exact Python required version can be found at
[pyproject.toml](./pyproject.toml).
2. Install [poetry](https://python-poetry.org/) and run `$ poetry install` to install dependencies.
3. Run it with `$ poetry run chessy` or manually with `$ .venv/bin/activate` followed by `$ python -m chessy.core`.
    - If you are trying to debug some problem, you can use the `--debug` (`-d` for short) flag to increase log level: `$ poetry run chessy -d`.

## Planned features

### Short term:

- Improve move evaluation and search.
    - Be able to process at least depth 10 within a reasonable time.
        - Right now, with my Ryzen 5 machine, it takes about ~10 seconds to process depth 2, and ~2 minutes to process depth 3. The goal is to be able to process depth 10 in around 10-15 seconds.
    - Quiescence search (as soon as we get some performance improvements - not right now because it will slow down things too much).

### Long term:

- Advanced UCI support
    - Adapt playstyle according to `wtime` and `btime`.
    - Ponder.
    - Maybe support customization options.

## Development utils
- If you're using VSCode, we have a [.vscode](./.vscode) with recommended extensions / settings,
and launch profiles.
- Alternatively, use [tools/format_lint_test.bash](./tools/format_lint_test.bash) to run all available lints.
Check the script source code if you want to run any of these lints separately.

## License
chessy is licensed under the GNU Affero General Public License, either version 3 or any later versions
at your choice. See [LICENSE.txt](./LICENSE.txt) for more details.
