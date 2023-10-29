import pytest

import chessy.core as c
import chessy.core.bitboard as cb


@pytest.mark.parametrize(
    "bb,square,expected_bb",
    [
        (
            cb.Bitboard(0xFFFF_FFFF_FFFF_FFFF),
            c.Square.e4,
            cb.Bitboard(0xFFFF_FFFF_EFFF_FFFF),
        ),
        (
            cb.Bitboard(0xFFFF_FFFF_EFFF_FFFF),
            c.Square.e4,
            cb.Bitboard(0xFFFF_FFFF_FFFF_FFFF),
        ),
        (cb.Bitboard(), c.Square.a1, cb.Bitboard(0x1)),
        (cb.Bitboard(), c.Square.h8, cb.Bitboard(0x8000_0000_0000_0000)),
    ],
)
def test_reverse_by_square(
    bb: cb.Bitboard, square: c.Square, expected_bb: cb.Bitboard
) -> None:
    prev = cb.get_by_square(bb, square)
    result = cb.reverse_by_square(bb, square)
    assert result == expected_bb
    assert cb.get_by_square(result, square) == (1 if prev == 0 else 0)


@pytest.mark.parametrize(
    "bb,square,expected_bb",
    [
        (
            cb.Bitboard(),
            c.Square.g2,
            cb.Bitboard(0x4000),
        ),
        (
            cb.Bitboard(0x4000),
            c.Square.g2,
            cb.Bitboard(0x4000),
        ),
    ],
)
def test_set_by_square(
    bb: cb.Bitboard, square: c.Square, expected_bb: cb.Bitboard
) -> None:
    result = cb.set_by_square(bb, square)
    assert result == expected_bb


@pytest.mark.parametrize(
    "bb,square,expected_bb",
    [
        (
            cb.Bitboard(),
            c.Square.d4,
            cb.Bitboard(),
        ),
        (
            cb.Bitboard(0x800_0000),
            c.Square.d4,
            cb.Bitboard(),
        ),
    ],
)
def test_pop_by_square(
    bb: cb.Bitboard, square: c.Square, expected_bb: cb.Bitboard
) -> None:
    result = cb.pop_by_square(bb, square)
    assert result == expected_bb
