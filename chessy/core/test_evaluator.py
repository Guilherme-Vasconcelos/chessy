import pytest

import chessy.core.board as cb
import chessy.core.evaluator as ce


@pytest.mark.parametrize(
    "fen,expected_wmobility,expected_bmobility",
    [
        (
            # Simple position with a few pawns
            "6k1/8/8/8/3p4/8/2PP4/3K4 w - - 2 18",
            6,
            6,
        ),
        (
            # En passant is allowed, but only for black, even though the white pawn
            # would also be able to reach it.
            "6k1/8/8/8/2Pp4/8/3P4/3K4 b - c3 0 18",
            6,
            7,
        ),
    ],
)
def test_mobility_calc(
    fen: str, expected_wmobility: int, expected_bmobility: int
) -> None:
    b = cb.Board.from_fen(fen)
    ev = ce.Evaluator()
    wmob, bmob = ev._calculate_mobility(b)  # pyright: ignore[reportPrivateUsage]
    assert expected_wmobility == wmob
    assert expected_bmobility == bmob
