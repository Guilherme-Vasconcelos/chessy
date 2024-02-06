# This module is a "debugging playground". Nothing here matters, feel free to ignore any
# lint warnings etc.

import chessy.core.board as cb


def main() -> None:
    b = cb.Board.from_fen("rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1")
    print(b.make_ascii_repr())  # noqa: T201


if __name__ == "__main__":
    main()
