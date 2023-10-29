from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from functools import cached_property

import chessy.core as c
import chessy.core.bitboard as cb


@dataclass(frozen=True, slots=True)
class _DirectionalAdd:
    shift: int
    prevented_files: Iterable[int] | None

    def __post_init__(self) -> None:
        if self.prevented_files is not None:
            assert all(
                0 <= file <= c.Square.last_file() for file in self.prevented_files
            )


# TODO: Remove all this apply_directional_add thing. We can now just magics for
# sliding pieces generations here.
def _apply_directional_add(
    start: c.Square,
    directional_add: _DirectionalAdd,
    add_cycles_limit: int | None = None,
    blockers: cb.Bitboard | None = None,
) -> set[c.Square]:
    result: set[c.Square] = set()

    if add_cycles_limit is None:
        add_cycles_limit = 7

    for _ in range(add_cycles_limit):
        try:
            new_square = c.Square(start.value + directional_add.shift)
        except ValueError:
            # Rank/board overflow
            break

        def _ok_next() -> None:
            nonlocal start
            # False positive, see https://github.com/astral-sh/ruff/issues/7847
            result.add(new_square)  # noqa: B023
            start = new_square  # noqa: B023

        if (
            directional_add.prevented_files is not None
            and new_square.file() in directional_add.prevented_files
        ):
            break

        if blockers is not None:
            is_blocker_hit = cb.get_by_square(blockers, new_square)
            if is_blocker_hit:
                _ok_next()
                break

        _ok_next()

    return result


def _apply_multidirectional_add(
    directions: Iterable[_DirectionalAdd],
    square: c.Square,
    add_cycles_limit: int | None = None,
    blockers: cb.Bitboard | None = None,
) -> set[c.Square]:
    return {
        atk
        for direction in directions
        for atk in _apply_directional_add(square, direction, add_cycles_limit, blockers)
    }


class _AttackTables:
    @cached_property
    def pawn_tables(self) -> tuple[list[set[c.Square]], list[set[c.Square]]]:
        white_tables: list[set[c.Square]] = []
        black_tables: list[set[c.Square]] = []

        for sq in c.Square:
            if sq.rank() in {c.Square.last_rank(), c.Square.first_rank()}:
                white_tables.append(set())
                black_tables.append(set())
                continue

            for piece in (
                c.Piece(c.Type.PAWN, c.Color.WHITE),
                c.Piece(c.Type.PAWN, c.Color.BLACK),
            ):
                attacks = self._generate_pawn_attacks(sq, piece)
                if piece.color == c.Color.WHITE:
                    white_tables.append(attacks)
                else:
                    black_tables.append(attacks)

        return white_tables, black_tables

    @cached_property
    def knight_tables(self) -> list[set[c.Square]]:
        tables: list[set[c.Square]] = []

        for sq in c.Square:
            attacks = self._generate_knight_attacks(sq)
            tables.append(attacks)

        return tables

    @cached_property
    def king_tables(self) -> list[set[c.Square]]:
        tables: list[set[c.Square]] = []

        for sq in c.Square:
            attacks = self._generate_king_attacks(sq)
            tables.append(attacks)

        return tables

    @staticmethod
    def _generate_pawn_attacks(square: c.Square, piece: c.Piece) -> set[c.Square]:
        direction_factor = piece.direction_factor()
        prevented_files = {
            # When adding 7/9, we can either be going left or right depending on
            # direction_factor.
            7: _H,
            9: _A,
            -7: _A,
            -9: _H,
        }
        side1 = direction_factor * 7
        side2 = direction_factor * 9
        directions = (
            _DirectionalAdd(side1, prevented_files[side1]),
            _DirectionalAdd(side2, prevented_files[side2]),
        )

        return _apply_multidirectional_add(directions, square, add_cycles_limit=1)

    @staticmethod
    def _generate_knight_attacks(square: c.Square) -> set[c.Square]:
        directions = (
            _DirectionalAdd(6, _H_G),
            _DirectionalAdd(10, _A_B),
            _DirectionalAdd(-6, _A_B),
            _DirectionalAdd(-10, _H_G),
            _DirectionalAdd(15, _H),
            _DirectionalAdd(17, _A),
            _DirectionalAdd(-15, _A),
            _DirectionalAdd(-17, _H),
        )
        return _apply_multidirectional_add(directions, square, add_cycles_limit=1)

    @staticmethod
    def _generate_king_attacks(square: c.Square) -> set[c.Square]:
        directions = (
            _DirectionalAdd(-7, _A),
            _DirectionalAdd(-8, None),
            _DirectionalAdd(-9, _H),
            _DirectionalAdd(-1, _H),
            _DirectionalAdd(1, _A),
            _DirectionalAdd(7, _H),
            _DirectionalAdd(8, None),
            _DirectionalAdd(9, _A),
        )
        return _apply_multidirectional_add(directions, square, add_cycles_limit=1)


_singleton_attack_tables = _AttackTables()


def force_init_all_tables() -> None:
    """
    Force all attack tables to initialize right now. This isn't explicitly required,
    since they are initialized whenever necessary, but it can be used if you
    want to make sure they are eagerly initialized.

    If they have already been initialized before, calling this function is very
    cheap. It will not initialize the tables a second time.
    """

    _ = _generate_pawn_attacks_precalc(c.Square.a2, c.Piece(c.Type.PAWN, c.Color.WHITE))
    _ = _generate_knight_attacks_precalc(c.Square.a1)
    _ = _generate_king_attacks_precalc(c.Square.a1)


# Common files in attack generation.
_A = (0,)
_H = (7,)
_H_G = (7, 6)
_A_B = (0, 1)


def _generate_pawn_attacks_precalc(square: c.Square, piece: c.Piece) -> set[c.Square]:
    assert square.rank() not in {c.Square.first_rank(), c.Square.last_rank()}
    white_tables, black_tables = _singleton_attack_tables.pawn_tables
    if piece.color == c.Color.WHITE:
        return white_tables[square.value]
    else:
        return black_tables[square.value]


def _generate_rook_attacks(blockers: cb.Bitboard, square: c.Square) -> set[c.Square]:
    directions = (
        _DirectionalAdd(8, None),
        _DirectionalAdd(-8, None),
        _DirectionalAdd(-1, _H),
        _DirectionalAdd(1, _A),
    )
    return _apply_multidirectional_add(directions, square, blockers=blockers)


def _generate_bishop_attacks(blockers: cb.Bitboard, square: c.Square) -> set[c.Square]:
    directions = (
        _DirectionalAdd(7, _H),
        _DirectionalAdd(9, _A),
        _DirectionalAdd(-7, _A),
        _DirectionalAdd(-9, _H),
    )
    return _apply_multidirectional_add(directions, square, blockers=blockers)


def _generate_knight_attacks_precalc(square: c.Square) -> set[c.Square]:
    knight_tables = _singleton_attack_tables.knight_tables
    return knight_tables[square.value]


def _generate_queen_attacks(blockers: cb.Bitboard, square: c.Square) -> set[c.Square]:
    return _generate_bishop_attacks(blockers, square) | _generate_rook_attacks(
        blockers, square
    )


def _generate_king_attacks_precalc(square: c.Square) -> set[c.Square]:
    king_tables = _singleton_attack_tables.king_tables
    return king_tables[square.value]


def generate_attacks(
    blockers: cb.Bitboard, square: c.Square, piece: c.Piece
) -> set[c.Square]:
    """
    Assuming `blockers` is a board indicating which pieces can block `piece`'s
    movements, generate all legal squares `piece` would be able to attack if placed at
    `square`.

    Special conditions:
    - For knights, kings and pawns, blockers do not matter.
    - Pawn is the only piece in which `piece.color` matters.
    """

    # TODO (perf): We will probably need to switch to a bitboard implementation to
    # precalc for sliding pieces. Without bitboards, we would probably not gain too
    # much performance (I haven't tested, but I believe we would need a huge iter
    # effort to empty the irrelevant blockers (in respect to the relevant occupancy),
    # effectively making it not too much different (if not worse) to what we already
    # have performance-wise).

    match piece.ptype:
        case c.Type.PAWN:
            return _generate_pawn_attacks_precalc(square, piece)
        case c.Type.KNIGHT:
            return _generate_knight_attacks_precalc(square)
        case c.Type.KING:
            return _generate_king_attacks_precalc(square)
        case c.Type.ROOK:
            return _generate_rook_attacks(blockers, square)
        case c.Type.BISHOP:
            return _generate_bishop_attacks(blockers, square)
        case c.Type.QUEEN:
            return _generate_queen_attacks(blockers, square)
