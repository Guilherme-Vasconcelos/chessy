# chessy
A simple chess engine.

This is a learning project. It is much slower than other production-ready engines and may have bugs, but
feel free to contribute if you wish to.

## Features

- Minimal UCI support.
- Lichess integration (see [this repository](https://github.com/Guilherme-Vasconcelos/lichess-bot)).

## Installation
chessy is available on pypi and can be downloaded as a Python package with: `$ pip install -U chessy`.

If you prefer to build it from source (e.g. when contributing), see [CONTRIBUTING.md](./CONTRIBUTING.md).

## Planned features

- Improve move evaluation and search.
    - Be able to process at least around depth 8 within a reasonable time.
    - Quiescence search (as soon as we get some performance improvements - not right now because it will slow down things too much).

- Advanced UCI support.
    - Adapt playstyle according to `wtime` and `btime`.
    - Ponder.
    - Report more info (e.g. `seldepth`).

## License
chessy is licensed under the GNU Affero General Public License, either version 3 or any later versions
at your choice. See [LICENSE.txt](./LICENSE.txt) for more details.
