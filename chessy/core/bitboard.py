from __future__ import annotations

from numpy import uint64

import chessy.core as c

Bitboard = uint64


def _sq_uint_value(square: c.Square) -> uint64:
    return uint64(square.value)


def reverse_by_square(bitboard: Bitboard, square: c.Square) -> Bitboard:
    v = _sq_uint_value(square)
    return bitboard ^ (uint64(1) << v)


def get_by_square(bitboard: Bitboard, square: c.Square) -> Bitboard:
    v = _sq_uint_value(square)
    return ((uint64(1) << v) & bitboard) >> v


def set_by_square(bitboard: Bitboard, square: c.Square) -> Bitboard:
    return bitboard | (uint64(1) << _sq_uint_value(square))


def pop_by_square(bitboard: Bitboard, square: c.Square) -> Bitboard:
    return bitboard & ~(uint64(1) << _sq_uint_value(square))


def make_ascii_repr(bitboard: Bitboard) -> str:
    red = "\x1b[0;31m"
    green = "\x1b[0;32m"
    reset = "\x1b[0m"
    margin = "------------------------------------"
    columns = "     a   b   c   d   e   f   g   h\n"

    result = f"Value (bin): 0b{bitboard:_b}\n"
    result += f"Value (hex): 0x{bitboard:_X}\n"
    result += "Board-like representation:\n"
    result += f"{margin}\n"
    for rank in range(c.Square.last_rank() + 1):
        result += f" {8 - rank} |"

        for file in range(c.Square.last_file() + 1):
            square_idx = (7 - rank) * 8 + file
            bit = get_by_square(bitboard, c.Square(square_idx))
            color = green if bit else red
            result += f" {color}{bit}{reset} |"

        result += "\n"

    result += columns
    result += margin

    return result
