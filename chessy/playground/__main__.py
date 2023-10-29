# This module is a "debugging playground". Nothing here matters, feel free to ignore any
# lint warnings etc.

import chessy.core as c
import chessy.core.bitboard as cb


def main() -> None:
    bb = cb.Bitboard()
    print(cb.make_ascii_repr(bb))  # noqa: T201
    print(cb.make_ascii_repr(cb.set_by_square(bb, c.Square.d4)))  # noqa: T201


if __name__ == "__main__":
    main()
