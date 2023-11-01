from __future__ import annotations

from typing import Literal, TypedDict

import chessy.core as c
import chessy.core.atkgen as ca
import chessy.core.board as cb


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


def _generate_nonpawn_pseudolegal_standard_moves(
    board: cb.Board, square: c.Square
) -> set[c.Move]:
    piece = board.get_piece_by_square(square)
    assert piece is not None and piece.ptype != c.Type.PAWN

    attacks = ca.generate_attacks(board, square, piece)
    result: set[c.Move] = set()
    for attack in attacks:
        maybe_target_piece = board.get_piece_by_square(attack)
        # TODO (perf): We only need to check the edge moves. Every non-edge attack is
        # automatically a move since it is not blocked (hence intermediate
        # squares can only be empty).
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
    assert pawn is not None and pawn.ptype == c.Type.PAWN

    seventh_rank = 6
    second_rank = 1
    result: set[c.Move] = set()

    def append_maybe_promotion_move(move: c.Move) -> None:
        assert (
            # pylance wants us to be sure it is not none even though it was
            # already not none the first time
            pawn is not None
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

    attacks = ca.generate_attacks(board, square, pawn)
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
