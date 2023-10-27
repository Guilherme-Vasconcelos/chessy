import pytest

import chessy.core as c
import chessy.core.atkgen as ca
import chessy.core.board as cb


def make_empty_board() -> cb.Board:
    return cb.Board.from_fen("8/8/8/8/8/8/8/8 w KQkq - 0 1")


def assert_eq_after_atk_gen(
    board_as_fen: str | None,
    initial_square: c.Square,
    piece: c.Piece,
    expected_attacks: set[c.Square],
) -> None:
    board = (
        make_empty_board() if board_as_fen is None else cb.Board.from_fen(board_as_fen)
    )
    attacks = ca.generate_attacks(board, initial_square, piece)
    assert attacks == expected_attacks


@pytest.mark.parametrize(
    "initial_square,pawn_color,expected_attacks",
    [
        (c.Square.e2, c.Color.WHITE, {c.Square.d3, c.Square.f3}),
        (c.Square.h4, c.Color.WHITE, {c.Square.g5}),
        (c.Square.a4, c.Color.WHITE, {c.Square.b5}),
        (c.Square.c7, c.Color.BLACK, {c.Square.d6, c.Square.b6}),
        (c.Square.a6, c.Color.BLACK, {c.Square.b5}),
        (c.Square.h6, c.Color.BLACK, {c.Square.g5}),
    ],
)
def test_pawn_attacks(
    initial_square: c.Square, pawn_color: c.Color, expected_attacks: set[c.Square]
) -> None:
    piece = c.Piece(c.Type.PAWN, pawn_color)
    assert_eq_after_atk_gen(None, initial_square, piece, expected_attacks)


@pytest.mark.parametrize(
    "initial_square,expected_attacks,board_as_fen",
    [
        (
            c.Square.e2,
            {
                c.Square.e3,
                c.Square.e4,
                c.Square.e5,
                c.Square.e6,
                c.Square.e7,
                c.Square.e8,
                c.Square.e1,
                c.Square.d2,
                c.Square.c2,
                c.Square.b2,
                c.Square.a2,
                c.Square.f2,
                c.Square.g2,
                c.Square.h2,
            },
            None,
        ),
        (
            c.Square.c3,
            {
                c.Square.c4,
                c.Square.c2,
                c.Square.b3,
                c.Square.a3,
                c.Square.d3,
                c.Square.e3,
                c.Square.f3,
                c.Square.g3,
                c.Square.h3,
            },
            "8/8/8/8/2r5/2R4r/2r5/8 w - - 0 1",
        ),
        (c.Square.h1, {c.Square.h2, c.Square.g1}, "8/8/8/8/8/8/7q/6qR w - - 0 1"),
    ],
)
def test_rook_attacks(
    initial_square: c.Square,
    expected_attacks: set[c.Square],
    board_as_fen: str | None,
) -> None:
    piece = c.Piece(c.Type.ROOK, color=None)  # type: ignore
    assert_eq_after_atk_gen(board_as_fen, initial_square, piece, expected_attacks)


@pytest.mark.parametrize(
    "initial_square,expected_attacks,board_as_fen",
    [
        (
            c.Square.e2,
            {
                c.Square.f1,
                c.Square.d1,
                c.Square.f3,
                c.Square.g4,
                c.Square.h5,
                c.Square.d3,
                c.Square.c4,
                c.Square.b5,
                c.Square.a6,
            },
            None,
        ),
        (
            c.Square.c3,
            {
                c.Square.b4,
                c.Square.d4,
                c.Square.b2,
                c.Square.a1,
                c.Square.d2,
                c.Square.e1,
            },
            "8/8/8/8/1r1r4/2B5/8/r7 w - - 0 1",
        ),
        (
            c.Square.a8,
            {
                c.Square.b7,
                c.Square.c6,
                c.Square.d5,
                c.Square.e4,
                c.Square.f3,
                c.Square.g2,
                c.Square.h1,
            },
            "b7/8/8/8/8/8/8/8 w - - 0 1",
        ),
    ],
)
def test_bishop_attacks(
    initial_square: c.Square,
    expected_attacks: set[c.Square],
    board_as_fen: str | None,
) -> None:
    piece = c.Piece(c.Type.BISHOP, color=None)  # type: ignore
    assert_eq_after_atk_gen(board_as_fen, initial_square, piece, expected_attacks)


@pytest.mark.parametrize(
    "initial_square,expected_attacks",
    [
        (
            c.Square.e4,
            {
                c.Square.d6,
                c.Square.f6,
                c.Square.c5,
                c.Square.g5,
                c.Square.c3,
                c.Square.d2,
                c.Square.f2,
                c.Square.g3,
            },
        ),
        (c.Square.h8, {c.Square.f7, c.Square.g6}),
        (c.Square.c1, {c.Square.a2, c.Square.b3, c.Square.d3, c.Square.e2}),
    ],
)
def test_knight_attacks(
    initial_square: c.Square,
    expected_attacks: set[c.Square],
) -> None:
    piece = c.Piece(c.Type.KNIGHT, color=None)  # type: ignore
    assert_eq_after_atk_gen(None, initial_square, piece, expected_attacks)


@pytest.mark.parametrize(
    "initial_square,expected_attacks,board_as_fen",
    [
        (
            c.Square.a1,
            {
                c.Square.a2,
                c.Square.a3,
                c.Square.a4,
                c.Square.a5,
                c.Square.a6,
                c.Square.a7,
                c.Square.a8,
                c.Square.b1,
                c.Square.c1,
                c.Square.d1,
                c.Square.e1,
                c.Square.f1,
                c.Square.g1,
                c.Square.h1,
                c.Square.b2,
            },
            "8/8/8/8/8/8/1k6/Q7 w - - 0 1",
        )
    ],
)
def test_queen_attacks(
    initial_square: c.Square,
    expected_attacks: set[c.Square],
    board_as_fen: str | None,
) -> None:
    piece = c.Piece(c.Type.QUEEN, color=None)  # type: ignore
    assert_eq_after_atk_gen(board_as_fen, initial_square, piece, expected_attacks)


@pytest.mark.parametrize(
    "initial_square,expected_attacks",
    [
        (
            c.Square.c6,
            {
                c.Square.b6,
                c.Square.b7,
                c.Square.b5,
                c.Square.c5,
                c.Square.c7,
                c.Square.d5,
                c.Square.d6,
                c.Square.d7,
            },
        ),
        (
            c.Square.g8,
            {c.Square.f8, c.Square.f7, c.Square.g7, c.Square.h7, c.Square.h8},
        ),
        (c.Square.a1, {c.Square.a2, c.Square.b2, c.Square.b1}),
    ],
)
def test_king_attacks(
    initial_square: c.Square, expected_attacks: set[c.Square]
) -> None:
    piece = c.Piece(c.Type.KING, color=None)  # type: ignore
    assert_eq_after_atk_gen(None, initial_square, piece, expected_attacks)
