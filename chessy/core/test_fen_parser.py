import pytest

import chessy.core.fen_parser as fp
from chessy.core import CastlingAvailability, Color, Piece, Square, Type
from chessy.core.fen_parser import parse


def build_fen(  # noqa: PLR0913
    piece_placement: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    active_color: str = "w",
    castling_availability: str = "KQkq",
    en_passant_target: str = "-",
    halfmove_clock: str = "0",
    fullmove_count: str = "1",
) -> str:
    return (
        f"{piece_placement} {active_color} {castling_availability} {en_passant_target} "
        f"{halfmove_clock} {fullmove_count}"
    ).strip()


@pytest.mark.parametrize(
    "test_input",
    [
        build_fen(fullmove_count=""),
        build_fen(piece_placement=""),
        # Extra trailing field
        build_fen() + " a",
    ],
)
def test_fen_with_incorrect_number_of_groups(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidNumberOfGroupsError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        # First rank only contains 7 letters and no numbers.
        build_fen(piece_placement="nbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"),
        # Same thing, but for last rank.
        build_fen(piece_placement="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBN"),
        # First rank has 1 extra letter.
        build_fen(piece_placement="rrnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"),
        # Second rank contains invalid letter 'w'.
        build_fen(piece_placement="rnbqkbnr/pppwpppp/8/8/8/8/PPPPPPPP/RNBQKBNR"),
    ],
)
def test_fen_with_incorrect_piece_placements(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidPiecePlacementError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        build_fen(active_color="W"),
        build_fen(active_color="B"),
        build_fen(active_color="l"),
    ],
)
def test_fen_with_incorrect_color(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidActiveColorError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input",
    [
        build_fen(en_passant_target="a9"),
        build_fen(en_passant_target="12345"),
        build_fen(en_passant_target="foobar"),
    ],
)
def test_fen_with_incorrect_en_passant_target(test_input: str) -> None:
    with pytest.raises(fp.FenInvalidEnPassantTargetError):
        parse(test_input)


@pytest.mark.parametrize(
    "test_input,expected_output",
    [
        (
            build_fen(
                piece_placement="8/8/8/8/8/8/8/k7",
                active_color="b",
                castling_availability="Kq",
                en_passant_target="e3",
                halfmove_clock="123",
                fullmove_count="1234",
            ),
            fp.FenParseResult(
                [Piece(ptype=Type.KING, color=Color.BLACK)] + [None] * 63,
                Color.BLACK,
                CastlingAvailability(True, False, False, True),
                Square.e3,
                123,
                1234,
            ),
        ),
        (
            build_fen(piece_placement="8/8/8/8/8/8/8/8"),
            fp.FenParseResult(
                [None] * 64,
                Color.WHITE,
                CastlingAvailability(True, True, True, True),
                None,
                0,
                1,
            ),
        ),
    ],
)
def test_wellformed_fen(test_input: str, expected_output: fp.FenParseResult) -> None:
    result = parse(test_input)
    assert result == expected_output
