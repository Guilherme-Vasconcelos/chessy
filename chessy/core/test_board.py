import pytest

import chessy.core as c
import chessy.core.board as cb


def assert_eq_after_move(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    initial = cb.Board.from_fen(initial_fen)
    initial.make_move(move)
    final = cb.Board.from_fen(expected_fen)
    # `_previous_moves` do not matter here, since we are doing a FEN comparison.
    initial._previous_moves.clear()  # pyright: ignore[reportPrivateUsage]
    assert initial == final


@pytest.mark.parametrize(
    "initial_fen,move,expected_fen",
    [
        (
            # White double pawn push.
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.e2, c.Square.e4),
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        ),
        (
            # White knight move.
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.g1, c.Square.f3),
            "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1",
        ),
        (
            # White bishop move.
            "rnbqkbnr/ppp2ppp/8/3pp3/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3",
            c.Move(c.Square.c1, c.Square.h6),
            "rnbqkbnr/ppp2ppp/7B/3pp3/3PP3/8/PPP2PPP/RN1QKBNR b KQkq - 1 3",
        ),
        (
            # White king move that loses castling rights for white.
            "rnbqkbnr/ppp2p1p/7p/3pp3/3PP3/8/PPP2PPP/RN1QKBNR w KQkq - 0 4",
            c.Move(c.Square.e1, c.Square.e2),
            "rnbqkbnr/ppp2p1p/7p/3pp3/3PP3/8/PPP1KPPP/RN1Q1BNR b kq - 1 4",
        ),
        (
            # Black double pawn push.
            "rnbqkbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            c.Move(c.Square.e7, c.Square.e5),
            "rnbqkbnr/pppp1ppp/8/4p3/8/4P3/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
        ),
        (
            # Black double push pawn with a white pawn on the other side.
            # This is to ensure en passant target update does not wrap around the board.
            "rnbqkbnr/pppppppp/8/P7/8/8/1PPPPPPP/RNBQKBNR b KQkq - 0 1",
            c.Move(c.Square.h7, c.Square.h5),
            "rnbqkbnr/ppppppp1/8/P6p/8/8/1PPPPPPP/RNBQKBNR w KQkq - 0 2",
        ),
        (
            # Same as previous but for white.
            "rnbqkbnr/ppppppp1/8/8/7p/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.a2, c.Square.a4),
            "rnbqkbnr/ppppppp1/8/8/P6p/8/1PPPPPPP/RNBQKBNR b KQkq - 0 1",
        ),
    ],
)
def test_regular_moves(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    assert_eq_after_move(initial_fen, move, expected_fen)


@pytest.mark.parametrize(
    "initial_fen,move,expected_fen",
    [
        (
            # White pawn capturing black pawn.
            "rnbqkbnr/pppppppp/8/8/8/3p4/PPP1PPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.e2, c.Square.d3),
            "rnbqkbnr/pppppppp/8/8/8/3P4/PPP2PPP/RNBQKBNR b KQkq - 0 1",
        ),
        (
            # Black pawn capturing white bishop.
            "rnbqkbnr/ppp2ppp/7B/3pp3/3PP3/8/PPP2PPP/RN1QKBNR b KQkq - 1 3",
            c.Move(c.Square.g7, c.Square.h6),
            "rnbqkbnr/ppp2p1p/7p/3pp3/3PP3/8/PPP2PPP/RN1QKBNR w KQkq - 0 4",
        ),
        (
            # Capture that loses castling rights for black.
            "r3k3/1B6/2n5/8/8/8/4K3/8 w q - 0 9",
            c.Move(c.Square.b7, c.Square.a8),
            "B3k3/8/2n5/8/8/8/4K3/8 b - - 0 9",
        ),
    ],
)
def test_captures(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    assert_eq_after_move(initial_fen, move, expected_fen)


@pytest.mark.parametrize(
    "initial_fen,move,expected_fen",
    [
        (
            # White castling kingside.
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQK2R w KQkq - 0 1",
            c.Move(c.Square.e1, c.Square.g1),
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQ1RK1 b kq - 1 1",
        ),
        (
            # Black castling queenside.
            "r3kbnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            c.Move(c.Square.e8, c.Square.c8),
            "2kr1bnr/pppppppp/8/8/8/4P3/PPPP1PPP/RNBQKBNR w KQ - 1 2",
        ),
    ],
)
def test_castling(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    assert_eq_after_move(initial_fen, move, expected_fen)


@pytest.mark.parametrize(
    "initial_fen,move,expected_fen",
    [
        (
            # White promoting a pawn into queen
            "rnbqkbnr/ppppppPp/8/8/8/8/PPPPPP1P/RNBQKBNR w - - 0 1",
            c.Move(c.Square.g7, c.Square.f8, promotion=c.Type.QUEEN),
            "rnbqkQnr/pppppp1p/8/8/8/8/PPPPPP1P/RNBQKBNR b - - 0 1",
        ),
        (
            # Black promoting a pawn into knight
            "rnbqkbnB/pppppp1p/8/8/8/8/PPPPPPpP/RNBQKBNR b KQq - 0 1",
            c.Move(c.Square.g2, c.Square.f1, promotion=c.Type.KNIGHT),
            "rnbqkbnB/pppppp1p/8/8/8/8/PPPPPP1P/RNBQKnNR w KQq - 0 2",
        ),
    ],
)
def test_promotions(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    assert_eq_after_move(initial_fen, move, expected_fen)


@pytest.mark.parametrize(
    "initial_fen,move,expected_fen",
    [
        (
            # Black does a double pawn push in the center, allowing en passant.
            "rnbqkbnr/pppppppp/8/4P3/8/P7/1PPP1PPP/RNBQKBNR b KQkq - 0 1",
            c.Move(c.Square.d7, c.Square.d5),
            "rnbqkbnr/ppp1pppp/8/3pP3/8/P7/1PPP1PPP/RNBQKBNR w KQkq d6 0 2",
        ),
        (
            # Prev. pos: white accepts en passant.
            "rnbqkbnr/ppp1pppp/8/3pP3/8/P7/1PPP1PPP/RNBQKBNR w KQkq d6 0 2",
            c.Move(c.Square.e5, c.Square.d6),
            "rnbqkbnr/ppp1pppp/3P4/8/8/P7/1PPP1PPP/RNBQKBNR b KQkq - 0 2",
        ),
        (
            # White does a double pawn push in the h file, allowing en passant.
            "rnbqkbnr/pppppp1p/8/8/6p1/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.h2, c.Square.h4),
            "rnbqkbnr/pppppp1p/8/8/6pP/8/PPPPPPP1/RNBQKBNR b KQkq h3 0 1",
        ),
        (
            # Prev. pos: black accepts en passant.
            "rnbqkbnr/pppppp1p/8/8/6pP/8/PPPPPPP1/RNBQKBNR b KQkq h3 0 1",
            c.Move(c.Square.g4, c.Square.h3),
            "rnbqkbnr/pppppp1p/8/8/8/7p/PPPPPPP1/RNBQKBNR w KQkq - 0 2",
        ),
        (
            # White double pushed a pawn to be next to its own color. Should NOT
            # allow en passant.
            "4k3/8/8/8/3P4/8/4PP2/5K2 w - - 0 1",
            c.Move(c.Square.e2, c.Square.e4),
            "4k3/8/8/8/3PP3/8/5P2/5K2 b - - 0 1",
        ),
        (
            # White double pushed a pawn to be next to its own color but also
            # next to an opposite color. Should allow en passant.
            "4k3/8/8/8/3P1p2/8/4PP2/5K2 w - - 0 1",
            c.Move(c.Square.e2, c.Square.e4),
            "4k3/8/8/8/3PPp2/8/5P2/5K2 b - e3 0 1",
        ),
    ],
)
def test_en_passant(initial_fen: str, move: c.Move, expected_fen: str) -> None:
    assert_eq_after_move(initial_fen, move, expected_fen)


@pytest.mark.parametrize(
    "fen,is_check",
    [
        ("8/5k2/8/8/3K4/8/8/8 w - - 0 1", False),
        ("8/3q1k2/8/8/3K4/8/8/8 w - - 0 1", True),
        ("n7/5k2/8/8/3K4/8/8/8 w - - 0 1", False),
        ("8/5k2/8/6N1/3K4/8/8/8 b - - 0 1", True),
        ("8/8/3k4/4P3/4K3/8/8/8 b - - 0 1", True),
    ],
)
def test_king_in_check(fen: str, is_check: bool) -> None:
    b = cb.Board.from_fen(fen)
    assert b.is_in_check() == is_check


@pytest.mark.parametrize(
    "initial_fen,move",
    [
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            c.Move(c.Square.e2, c.Square.e5),
        )
    ],
)
def test_illegal_moves(initial_fen: str, move: c.Move) -> None:
    with pytest.raises(cb.IllegalMoveError):
        b = cb.Board.from_fen(initial_fen)
        b.make_move(move)


@pytest.mark.parametrize(
    "initial_fen,moves",
    [
        (
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            [
                # Simple knight move by white
                c.Move(c.Square.b1, c.Square.a3),
                # Simple b pawn push by black
                c.Move(c.Square.b7, c.Square.b6),
            ],
        ),
        (
            "rn1qkbnr/pbppp1pp/1p3p2/4P3/8/N7/PPPP1PPP/R1BQKBNR w KQkq - 0 1",
            [
                # Pawn capture by white
                c.Move(c.Square.e5, c.Square.f6),
                # Pawn capture by black
                c.Move(c.Square.e7, c.Square.f6),
            ],
        ),
        (
            "rn1qkbnr/pbpppppp/1p6/4P3/8/N7/PPPP1PPP/R1BQKBNR b KQkq - 0 1",
            [
                # Double pawn push by black
                c.Move(c.Square.f7, c.Square.f5),
                # En passant by white
                c.Move(c.Square.e5, c.Square.f6),
                # Knight capture by black
                c.Move(c.Square.g8, c.Square.f6),
            ],
        ),
        (
            "4k2r/R4p2/8/8/8/8/8/4K2R w Kk - 0 1",
            [
                # Castling by white
                c.Move(c.Square.e1, c.Square.g1),
                # Castling by black
                c.Move(c.Square.e8, c.Square.g8),
                # Capture pawn by white
                c.Move(c.Square.f1, c.Square.f7),
            ],
        ),
        (
            "rnbqkbnr/pPpppppp/8/8/8/8/PPPPPPpP/RNBQKB1R b KQkq - 0 1",
            [
                # Promotion by black
                c.Move(c.Square.g2, c.Square.g1, promotion=c.Type.ROOK),
                # Promotion by white with capture
                c.Move(c.Square.b7, c.Square.a8, promotion=c.Type.KNIGHT),
            ],
        ),
    ],
)
def test_move_rollback(initial_fen: str, moves: list[c.Move]) -> None:
    b = cb.Board.from_fen(initial_fen)
    for move in moves:
        b.make_move(move)
    for _ in moves:
        b.unmake_move()
    expected = cb.Board.from_fen(initial_fen)
    assert b == expected


@pytest.mark.parametrize(
    "fen,expected_err",
    [
        (
            "rnbqqbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR w KQkq - 0 1",
            cb.NoKingError,
        )
    ],
)
def test_unreachable_positions(
    fen: str, expected_err: type[cb.UnreachablePositionError]
) -> None:
    with pytest.raises(expected_err):
        cb.Board.from_fen(fen)
