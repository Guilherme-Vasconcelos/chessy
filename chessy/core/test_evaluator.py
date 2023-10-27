import pytest

import chessy.core as c
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


@pytest.mark.parametrize(
    "fen,expected_bestmove",
    [
        # Because move search is a more heuristic algorithm, we can't always guarantee
        # the same results. So we only test positions where there is a very clear
        # winning move.
        #
        # Mate in 1: ensure we don't stalemate.
        ("6k1/4Q3/5K2/8/8/8/8/8 w - - 0 1", c.Move(c.Square.e7, c.Square.g7)),
        ("6K1/4q3/5k2/8/8/8/8/8 b - - 0 1", c.Move(c.Square.e7, c.Square.g7)),
    ],
)
def test_move_search(fen: str, expected_bestmove: c.Move) -> None:
    ev = ce.Evaluator()
    b = cb.Board.from_fen(fen)
    bestmove = ev.start_search(b, max_depth=1)
    if bestmove != expected_bestmove:
        bestmove = ev.start_search(b, max_depth=2)
    assert bestmove == expected_bestmove
