from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal, TypedDict

import chessy.core as c
import chessy.core.board as cb


@dataclass
class _DirectionalAdd:
    shift: int
    prevented_files: Iterable[int] | None

    def __post_init__(self) -> None:
        if self.prevented_files is not None:
            assert all(
                0 <= file <= c.Square.last_file() for file in self.prevented_files
            )


def _apply_directional_add(
    start: c.Square,
    directional_add: _DirectionalAdd,
    add_cycles_limit: int | None = None,
    blockers: cb.Board | None = None,
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
            is_blocker_hit = blockers.get_piece_by_square(new_square) is not None
            if is_blocker_hit:
                _ok_next()
                break

        _ok_next()

    return result


def _apply_multidirectional_add(
    directions: Iterable[_DirectionalAdd],
    square: c.Square,
    add_cycles_limit: int | None = None,
    blockers: cb.Board | None = None,
) -> set[c.Square]:
    return {
        atk
        for direction in directions
        for atk in _apply_directional_add(square, direction, add_cycles_limit, blockers)
    }


# Common files in move/attack generation.
_A = (0,)
_H = (7,)
_H_G = (7, 6)
_A_B = (0, 1)


def _generate_pawn_attacks(square: c.Square, piece: c.Piece) -> set[c.Square]:
    assert square.rank() not in {0, 7}
    assert piece.ptype == c.Type.PAWN

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
    directions = _DirectionalAdd(side1, prevented_files[side1]), _DirectionalAdd(
        side2, prevented_files[side2]
    )

    return _apply_multidirectional_add(directions, square, add_cycles_limit=1)


def _generate_rook_attacks(blockers: cb.Board, square: c.Square) -> set[c.Square]:
    directions = (
        _DirectionalAdd(8, None),
        _DirectionalAdd(-8, None),
        _DirectionalAdd(-1, _H),
        _DirectionalAdd(1, _A),
    )
    return _apply_multidirectional_add(directions, square, blockers=blockers)


def _generate_bishop_attacks(blockers: cb.Board, square: c.Square) -> set[c.Square]:
    directions = (
        _DirectionalAdd(7, _H),
        _DirectionalAdd(9, _A),
        _DirectionalAdd(-7, _A),
        _DirectionalAdd(-9, _H),
    )
    return _apply_multidirectional_add(directions, square, blockers=blockers)


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


def _generate_queen_attacks(blockers: cb.Board, square: c.Square) -> set[c.Square]:
    return _generate_bishop_attacks(blockers, square) | _generate_rook_attacks(
        blockers, square
    )


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


def _board_would_be_in_check_after_move(board: cb.Board, move: c.Move) -> bool:
    color = board.active_color
    # Validating move requires move generation, and this method is called during move
    # generation. So not bypassing validation would generate an infinite recursion.
    # But this is not a problem since the move generator only generates pseudolegal
    # moves.
    board.make_move(move, bypass_validation=True)
    result = board.is_in_check(color)
    board.unmake_move()
    return result


def generate_attacks(
    blockers: cb.Board, square: c.Square, piece: c.Piece
) -> set[c.Square]:
    """
    Assuming `blockers` is a board indicating which pieces can block `piece`'s
    movements, generate all legal squares `piece` would be able to attack if placed at
    `square`.

    Special conditions:
    - For knights, kings and pawns, blockers do not matter.
    - Pawn is the only piece in which `piece.color` matters.

    How "attacks" differ from "moves":

    1. Attacks do not check legality. A piece can attack a certain square, but not be
    able to move to it e.g. if it results in a check position or if the square is
    already occupied by another piece of the same color.

    2. For pawns, some of its moves are not attacks. Hence, generating attacks for pawns
    will not list all possible pseudo-moves.

    In short, attacks are threats (useful for e.g. king in check verifications), while
    moves are concrete moves that can actually be made in the current position.
    """

    # TODO (perf): Attacks can be precalculated on startup.

    match piece.ptype:
        case c.Type.PAWN:
            return _generate_pawn_attacks(square, piece)
        case c.Type.ROOK:
            return _generate_rook_attacks(blockers, square)
        case c.Type.BISHOP:
            return _generate_bishop_attacks(blockers, square)
        case c.Type.KNIGHT:
            return _generate_knight_attacks(square)
        case c.Type.QUEEN:
            return _generate_queen_attacks(blockers, square)
        case c.Type.KING:
            return _generate_king_attacks(square)


def _generate_nonpawn_pseudolegal_standard_moves(
    board: cb.Board, square: c.Square
) -> set[c.Move]:
    piece = board.get_piece_by_square(square)
    assert piece is not None

    attacks = generate_attacks(board, square, piece)
    result: set[c.Move] = set()
    for attack in attacks:
        maybe_target_piece = board.get_piece_by_square(attack)
        # TODO (perf): For attacks by sliding pieces, we only need to check the edge moves.
        # Every non-edge attack is automatically a move since it is not blocked
        # (hence intermediate squares can only be empty).
        if maybe_target_piece is not None and maybe_target_piece.color == piece.color:
            continue
        else:
            result.add(c.Move(square, attack))
    return result


def _generate_castling_moves(board: cb.Board, color: c.Color) -> set[c.Move]:
    if board.is_in_check():
        return set()

    result: set[c.Move] = set()

    class CastlingPath(TypedDict):
        start: c.Square
        king_path: list[c.Square]
        full_path: list[c.Square]

    class CastlingPaths(TypedDict):
        K: CastlingPath
        Q: CastlingPath
        k: CastlingPath
        q: CastlingPath

    castling_paths: CastlingPaths = {
        "K": {
            "start": c.Square.e1,
            "king_path": [c.Square.f1, c.Square.g1],
            "full_path": [c.Square.f1, c.Square.g1],
        },
        "Q": {
            "start": c.Square.e1,
            "king_path": [c.Square.d1, c.Square.c1],
            "full_path": [c.Square.d1, c.Square.c1, c.Square.b1],
        },
        "k": {
            "start": c.Square.e8,
            "king_path": [c.Square.f8, c.Square.g8],
            "full_path": [c.Square.f8, c.Square.g8],
        },
        "q": {
            "start": c.Square.e8,
            "king_path": [c.Square.d8, c.Square.c8],
            "full_path": [c.Square.d8, c.Square.c8, c.Square.b8],
        },
    }

    def path_is_clear(castling_path: Literal["K", "Q", "k", "q"]) -> bool:
        return all(
            board.get_piece_by_square(s) is None
            for s in castling_paths[castling_path]["full_path"]
        )

    def path_has_no_intermediate_checks(
        castling_path: Literal["K", "Q", "k", "q"]
    ) -> bool:
        return not any(
            _board_would_be_in_check_after_move(
                board, c.Move(castling_paths[castling_path]["start"], s)
            )
            for s in castling_paths[castling_path]["king_path"]
        )

    if color == c.Color.WHITE:
        if (
            board.castling_availability.white_kingside
            and path_is_clear("K")
            and path_has_no_intermediate_checks("K")
        ):
            result.add(c.Move(c.Square.e1, c.Square.g1))

        if (
            board.castling_availability.white_queenside
            and path_is_clear("Q")
            and path_has_no_intermediate_checks("Q")
        ):
            result.add(c.Move(c.Square.e1, c.Square.c1))
    else:
        if (
            board.castling_availability.black_kingside
            and path_is_clear("k")
            and path_has_no_intermediate_checks("k")
        ):
            result.add(c.Move(c.Square.e8, c.Square.g8))

        if (
            board.castling_availability.black_queenside
            and path_is_clear("q")
            and path_has_no_intermediate_checks("q")
        ):
            result.add(c.Move(c.Square.e8, c.Square.c8))
    return result


def _generate_pawns_pseudolegal_moves(board: cb.Board, square: c.Square) -> set[c.Move]:
    pawn = board.get_piece_by_square(square)
    assert pawn is not None

    seventh_rank = 6
    second_rank = 1
    result: set[c.Move] = set()

    def append_maybe_promotion_move(move: c.Move) -> None:
        assert (
            # pylance wants us to be sure it is not none even though it was
            # already not none the first time
            pawn
            is not None
        )
        is_promotion = (
            pawn.color == c.Color.WHITE and square.rank() == seventh_rank
        ) or (pawn.color == c.Color.BLACK and square.rank() == second_rank)
        if is_promotion:
            result.update(
                [
                    c.Move(move.source, move.target, promotion=promotable_type)
                    for promotable_type in [
                        c.Type.BISHOP,
                        c.Type.KNIGHT,
                        c.Type.QUEEN,
                        c.Type.ROOK,
                    ]
                ]
            )
        else:
            result.add(move)

    attacks = generate_attacks(board, square, pawn)
    for attack in attacks:
        if (
            (maybe_attacked_piece := board.get_piece_by_square(attack)) is not None
            and maybe_attacked_piece.color == pawn.color.invert()
        ) or attack == board.en_passant_target:
            move = c.Move(square, attack)
            append_maybe_promotion_move(move)

    direction_factor = pawn.direction_factor()
    single_step = c.Square(square.value + 8 * direction_factor)
    if single_step_is_clear := board.get_piece_by_square(single_step) is None:
        move = c.Move(square, single_step)
        append_maybe_promotion_move(move)

    is_first_pawn_move = (
        pawn.color == c.Color.WHITE and square.rank() == second_rank
    ) or (pawn.color == c.Color.BLACK and square.rank() == seventh_rank)
    if single_step_is_clear and is_first_pawn_move:
        double_step = c.Square(single_step.value + 8 * direction_factor)
        if board.get_piece_by_square(double_step) is None:
            move = c.Move(square, double_step)
            result.add(move)

    return result


def _generate_pseudolegal_moves(board: cb.Board, square: c.Square) -> set[c.Move]:
    if (
        piece := board.get_piece_by_square(square)
    ) is None or piece.color != board.active_color:
        return set()

    match piece.ptype:
        case c.Type.ROOK | c.Type.BISHOP | c.Type.QUEEN | c.Type.KNIGHT | c.Type.KING:
            result = _generate_nonpawn_pseudolegal_standard_moves(board, square)

            if piece.ptype == c.Type.KING:
                result |= _generate_castling_moves(board, piece.color)
        case c.Type.PAWN:
            result = _generate_pawns_pseudolegal_moves(board, square)

    return result


def generate_legal_moves(board: cb.Board, square: c.Square) -> set[c.Move]:
    """
    Generate all strictly legal moves for the piece located at `square`.

    For differences between moves and attacks, see `generate_attacks`.
    """

    result: set[c.Move] = set()
    pseudo_moves = _generate_pseudolegal_moves(board, square)
    for move in pseudo_moves:
        if not _board_would_be_in_check_after_move(board, move):
            result.add(move)

    return result


def generate_all_legal_moves(board: cb.Board) -> set[c.Move]:
    """
    Generate all strictly legal moves that are possible given the current board state.
    """

    return {move for square in c.Square for move in generate_legal_moves(board, square)}
