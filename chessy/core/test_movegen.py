import pytest

import chessy.core as c
import chessy.core.board as cb
import chessy.core.movegen as cm


@pytest.mark.parametrize(
    "initial_fen,expected_moves",
    [
        (
            "4k2r/r2Nn3/7p/8/1Pp5/B5p1/4Q2P/R3K2R b KQk b3 0 1",
            {
                # Black king
                c.Move(c.Square.e8, c.Square.d8),
                c.Move(c.Square.e8, c.Square.d7),
                c.Move(c.Square.e8, c.Square.f7),
                # Black rook (left)
                c.Move(c.Square.a7, c.Square.b7),
                c.Move(c.Square.a7, c.Square.c7),
                c.Move(c.Square.a7, c.Square.d7),
                c.Move(c.Square.a7, c.Square.a6),
                c.Move(c.Square.a7, c.Square.a5),
                c.Move(c.Square.a7, c.Square.a4),
                c.Move(c.Square.a7, c.Square.a3),
                c.Move(c.Square.a7, c.Square.a8),
                # Black rook (right)
                c.Move(c.Square.h8, c.Square.h7),
                c.Move(c.Square.h8, c.Square.g8),
                c.Move(c.Square.h8, c.Square.f8),
                # h pawn
                c.Move(c.Square.h6, c.Square.h5),
                # g pawn
                c.Move(c.Square.g3, c.Square.h2),
                c.Move(c.Square.g3, c.Square.g2),
                # c pawn
                c.Move(c.Square.c4, c.Square.c3),
                c.Move(c.Square.c4, c.Square.b3),
            },
        ),
        (
            "4k2r/r2Nn3/7p/8/1Pp5/B5p1/4Q2P/R3K2R w KQk b3 0 1",
            {
                # White king
                c.Move(c.Square.e1, c.Square.f1),
                c.Move(c.Square.e1, c.Square.g1),
                c.Move(c.Square.e1, c.Square.d2),
                c.Move(c.Square.e1, c.Square.d1),
                c.Move(c.Square.e1, c.Square.c1),
                # White rook (left)
                c.Move(c.Square.a1, c.Square.a2),
                c.Move(c.Square.a1, c.Square.b1),
                c.Move(c.Square.a1, c.Square.c1),
                c.Move(c.Square.a1, c.Square.d1),
                # White rook (right)
                c.Move(c.Square.h1, c.Square.g1),
                c.Move(c.Square.h1, c.Square.f1),
                # White queen
                c.Move(c.Square.e2, c.Square.d1),
                c.Move(c.Square.e2, c.Square.f1),
                c.Move(c.Square.e2, c.Square.f2),
                c.Move(c.Square.e2, c.Square.g2),
                c.Move(c.Square.e2, c.Square.d2),
                c.Move(c.Square.e2, c.Square.c2),
                c.Move(c.Square.e2, c.Square.b2),
                c.Move(c.Square.e2, c.Square.a2),
                c.Move(c.Square.e2, c.Square.d3),
                c.Move(c.Square.e2, c.Square.c4),
                c.Move(c.Square.e2, c.Square.f3),
                c.Move(c.Square.e2, c.Square.g4),
                c.Move(c.Square.e2, c.Square.h5),
                c.Move(c.Square.e2, c.Square.e3),
                c.Move(c.Square.e2, c.Square.e4),
                c.Move(c.Square.e2, c.Square.e5),
                c.Move(c.Square.e2, c.Square.e6),
                c.Move(c.Square.e2, c.Square.e7),
                # h pawn
                c.Move(c.Square.h2, c.Square.h3),
                c.Move(c.Square.h2, c.Square.h4),
                c.Move(c.Square.h2, c.Square.g3),
                # White bishop
                c.Move(c.Square.a3, c.Square.b2),
                c.Move(c.Square.a3, c.Square.c1),
                # b pawn
                c.Move(c.Square.b4, c.Square.b5),
                # White knight
                c.Move(c.Square.d7, c.Square.b8),
                c.Move(c.Square.d7, c.Square.b6),
                c.Move(c.Square.d7, c.Square.c5),
                c.Move(c.Square.d7, c.Square.e5),
                c.Move(c.Square.d7, c.Square.f6),
                c.Move(c.Square.d7, c.Square.f8),
            },
        ),
        (
            "6nk/5Pp1/6K1/8/8/8/8/8 w - - 0 1",
            {
                # White pawn
                c.Move(c.Square.f7, c.Square.g8, promotion=c.Type.BISHOP),
                c.Move(c.Square.f7, c.Square.g8, promotion=c.Type.KNIGHT),
                c.Move(c.Square.f7, c.Square.g8, promotion=c.Type.QUEEN),
                c.Move(c.Square.f7, c.Square.g8, promotion=c.Type.ROOK),
                c.Move(c.Square.f7, c.Square.f8, promotion=c.Type.BISHOP),
                c.Move(c.Square.f7, c.Square.f8, promotion=c.Type.KNIGHT),
                c.Move(c.Square.f7, c.Square.f8, promotion=c.Type.QUEEN),
                c.Move(c.Square.f7, c.Square.f8, promotion=c.Type.ROOK),
                # White king
                c.Move(c.Square.g6, c.Square.f5),
                c.Move(c.Square.g6, c.Square.g5),
                c.Move(c.Square.g6, c.Square.h5),
            },
        ),
        (
            "4k3/8/8/8/3PP3/8/5P2/5K2 b - - 0 1",
            {
                c.Move(c.Square.e8, c.Square.d8),
                c.Move(c.Square.e8, c.Square.d7),
                c.Move(c.Square.e8, c.Square.e7),
                c.Move(c.Square.e8, c.Square.f8),
                c.Move(c.Square.e8, c.Square.f7),
            },
        ),
        (
            "4k3/8/8/8/3PPp2/8/5P2/5K2 b - e3 0 1",
            {
                # King moves
                c.Move(c.Square.e8, c.Square.d8),
                c.Move(c.Square.e8, c.Square.d7),
                c.Move(c.Square.e8, c.Square.e7),
                c.Move(c.Square.e8, c.Square.f8),
                c.Move(c.Square.e8, c.Square.f7),
                # Black pawn en passant
                c.Move(c.Square.f4, c.Square.e3),
                c.Move(c.Square.f4, c.Square.f3),
            },
        ),
    ],
)
def test_moves(initial_fen: str, expected_moves: set[c.Move]) -> None:
    b = cb.Board.from_fen(initial_fen)
    moves = cm.generate_all_legal_moves(b)
    assert moves == expected_moves


@pytest.mark.parametrize(
    "initial_fen",
    [
        # Castling blocked
        "rn2k3/p7/3B4/2K1P3/8/8/8/8 b q - 0 9",
        # King in check
        "rn2k3/p7/2B5/2K1P3/8/8/8/8 b q - 0 9",
        # Castling path in check
        "rn2k3/p7/4B3/2K1P3/8/8/8/8 b q - 0 9",
    ],
)
def test_impossible_castling_positions(initial_fen: str) -> None:
    b = cb.Board.from_fen(initial_fen)
    moves = cm.generate_all_legal_moves(b)
    assert c.Move(c.Square.e1, c.Square.g1) not in moves
    assert c.Move(c.Square.e1, c.Square.c1) not in moves
    assert c.Move(c.Square.e8, c.Square.g8) not in moves
    assert c.Move(c.Square.e8, c.Square.c8) not in moves
