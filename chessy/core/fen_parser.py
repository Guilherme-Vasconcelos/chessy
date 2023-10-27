from dataclasses import dataclass

import chessy.core as c
import chessy.core.board as cb
import chessy.utils as ut


class FenValidationError(Exception):
    pass


class FenInvalidNumberOfGroupsError(FenValidationError):
    pass


class FenInvalidPiecePlacementError(FenValidationError):
    pass


class FenInvalidActiveColorError(FenValidationError):
    pass


class FenInvalidCastlingAvailabilityError(FenValidationError):
    pass


class FenInvalidEnPassantTargetError(FenValidationError):
    pass


class FenInvalidHalfmoveClockError(FenValidationError):
    pass


class FenInvalidFullmoveNumberError(FenValidationError):
    pass


@dataclass(frozen=True, slots=True)
class FenParseResult:
    piece_placement: list[c.Piece | None]
    active_color: c.Color
    castling_availability: c.CastlingAvailability
    en_passant_target: c.Square | None
    halfmove_clock: int
    fullmove_number: int


def _fen_validation_assert(cond: bool, e: FenValidationError) -> None:
    if not cond:
        raise e


def _parse_piece_placement(v: str) -> list[c.Piece | None]:
    rank_size = 8
    board_size = cb.BOARD_SIZE
    valid_rank_letters = {"p", "P", "k", "K", "q", "Q", "r", "R", "n", "N", "b", "B"}
    piece_placement: list[c.Piece | None] = [None] * board_size
    ranks = v.split("/")

    def _piece_placement_validate_rank(rank: str) -> None:
        rank_has_correct_characters = all(
            c in valid_rank_letters or c.isnumeric() for c in rank
        )
        _fen_validation_assert(
            rank_has_correct_characters,
            FenInvalidPiecePlacementError(f"Rank {rank} contains invalid characters."),
        )
        rank_value = sum([1 if c in valid_rank_letters else int(c) for c in rank])
        _fen_validation_assert(
            rank_value == rank_size,
            FenInvalidPiecePlacementError(
                f"Rank {rank} does not represent {rank_size} squares."
            ),
        )

    for i, rank in enumerate(ranks):
        idx = board_size - rank_size * (i + 1)  # Start of each rank

        _piece_placement_validate_rank(rank)

        for char in rank:
            if char in valid_rank_letters:
                piece_placement[idx] = c.Piece.from_letter(char)
                idx += 1
            elif char.isnumeric():
                idx += int(char)
            else:
                ut.unreachable()

    return piece_placement


def _parse_active_color(v: str) -> c.Color:
    _fen_validation_assert(
        v in {"w", "b"},
        FenInvalidActiveColorError(f"Color {v} is invalid. Try 'w' or 'b'."),
    )

    match v:
        case "w":
            return c.Color.WHITE
        case "b":
            return c.Color.BLACK
        case _:
            ut.unreachable()


def _parse_castling_availability(v: str) -> c.CastlingAvailability:
    availability = c.CastlingAvailability(False, False, False, False)
    if v == "-":
        return availability

    valid_castling_availability_chars = {"K", "k", "Q", "q"}
    max_castling_availability_size = 4
    _fen_validation_assert(
        len(v) <= max_castling_availability_size
        and all(c in valid_castling_availability_chars for c in v)
        and len(set(v)) == len(v),  # No repeated chars
        FenInvalidCastlingAvailabilityError(f"Invalid castling availability {v}."),
    )

    for char in v:
        match char:
            case "K":
                availability.white_kingside = True
            case "k":
                availability.black_kingside = True
            case "Q":
                availability.white_queenside = True
            case "q":
                availability.black_queenside = True
            case _:
                ut.unreachable()

    return availability


def _parse_en_passant_target(v: str) -> c.Square | None:
    if v == "-":
        return None

    try:
        return c.Square[v]
    except KeyError:
        raise FenInvalidEnPassantTargetError(
            f"{v} does not represent a valid square."
        ) from None


def _parse_halfmove_clock(v: str) -> int:
    try:
        parsed_v = int(v)
        _fen_validation_assert(
            parsed_v >= 0,
            FenInvalidHalfmoveClockError(
                f"Expected halfmove clock to be at least 0, got {v}."
            ),
        )
        return parsed_v
    except ValueError:
        raise FenInvalidHalfmoveClockError(
            f"{v} does not represent a correct halfmove clock."
        ) from None


def _parse_fullmove_number(v: str) -> int:
    try:
        parsed_v = int(v)
        _fen_validation_assert(
            parsed_v >= 1,
            FenInvalidFullmoveNumberError(
                f"Expected fullmove number to be at least 1, got {v}."
            ),
        )
        return parsed_v
    except ValueError:
        raise FenInvalidFullmoveNumberError(
            f"{v} does not represent a correct fullmove number."
        ) from None


def parse(value: str) -> FenParseResult:
    """
    Parse `value` as a FEN, extracting all of its information.
    Semantics of the position is not taken into consideration - meaning e.g. a position
    without a king, or a position with more kings than it should, will not fail as long
    as the FEN is well-formed.

    Can raise multiple exceptions, all of which inherit `FenValidationError`.

    For examples and explanations, see https://en.wikipedia.org/wiki/Forsyth-Edwards_Notation.
    """

    groups = value.split()
    expected_ngroups = 6
    _fen_validation_assert(
        (actual_ngroups := len(groups)) == expected_ngroups,
        FenInvalidNumberOfGroupsError(
            f"Expected {expected_ngroups} groups, got {actual_ngroups}."
        ),
    )

    (
        s_piece_placement,
        s_active_color,
        s_castling_availability,
        s_en_passant_target,
        s_halfmove_clock,
        s_fullmove_number,
    ) = groups

    piece_placement = _parse_piece_placement(s_piece_placement)
    active_color = _parse_active_color(s_active_color)
    castling_availability = _parse_castling_availability(s_castling_availability)
    en_passant_target = _parse_en_passant_target(s_en_passant_target)
    halfmove_clock = _parse_halfmove_clock(s_halfmove_clock)
    fullmove_number = _parse_fullmove_number(s_fullmove_number)

    return FenParseResult(
        piece_placement,
        active_color,
        castling_availability,
        en_passant_target,
        halfmove_clock,
        fullmove_number,
    )
