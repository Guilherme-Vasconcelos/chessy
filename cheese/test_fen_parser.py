import pytest

import cheese.fen_parser as fp
from cheese import CastlingAvailability, Color, Piece, Type
from cheese.fen_parser import parse


@pytest.mark.parametrize(
    "test_input",
    [
        # Missing fullmove count.
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0",
        # Missing piece placement.
        "w KQkq - 0 1",
        # Extra field 'a'.
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1 a",
    ],
)
def test_fen_with_incorrect_number_of_groups(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidNumberOfGroupsError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        # First rank only contains 7 letters and no numbers.
        "nbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        # Same thing, but for last rank.
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBN w KQkq - 0 1",
        # First rank has 1 extra letter.
        "rrnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        # Second rank contains invalid letter 'w'.
        "rnbqkbnr/pppwpppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    ],
)
def test_fen_with_incorrect_piece_placements(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidPiecePlacementError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "8/8/8/8/8/8/8/8 W KQkq - 0 1",
        "8/8/8/8/8/8/8/8 B KQq - 0 1",
        "8/8/8/8/8/8/8/8 l KQq - 0 1",
    ],
)
def test_fen_with_incorrect_color(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidActiveColorError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        "8/8/8/8/8/8/8/8 w KQkq a9 0 1",
        "8/8/8/8/8/8/8/8 w KQq 12351235 0 1",
        "8/8/8/8/8/8/8/8 w KQq foobar 0 1",
    ],
)
def test_fen_with_incorrect_en_passant_target(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidEnPassantTargetError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input,expected_output",
    [
        (
            "8/8/8/8/8/8/8/k7 b - - 123 1234",
            fp.FenParseResult(
                [Piece(ptype=Type.KING, color=Color.BLACK)] + [None] * 63,
                Color.BLACK,
                CastlingAvailability(False, False, False, False),
                None,
                123,
                1234,
            ),
        ),
        (
            "8/8/8/8/8/8/8/8 b KQq - 0 1",
            fp.FenParseResult(
                [None] * 64,
                Color.BLACK,
                CastlingAvailability(True, True, False, True),
                None,
                0,
                1,
            ),
        ),
    ],
)
def test_fen_with_correct_piece_placements(
    test_input: str, expected_output: fp.FenParseResult
) -> None:
    result = parse(test_input)
    assert result == expected_output
