from copy import deepcopy
from typing import Any

import cheese as c
import cheese.board as cb
import cheese.movegen as cm


def _calculate_mobility(board: cb.Board) -> tuple[int, int]:
    current_side_legal_moves = cm.generate_all_legal_moves(board)
    board.active_color = board.active_color.invert()
    other_side_legal_moves = cm.generate_all_legal_moves(board)
    board.active_color = board.active_color.invert()

    if board.active_color == c.Color.WHITE:
        white_mobility = len(current_side_legal_moves)
        black_mobility = len(other_side_legal_moves)
    else:
        white_mobility = len(other_side_legal_moves)
        black_mobility = len(current_side_legal_moves)

    return white_mobility, black_mobility


def _calculate_piece_counts(board: cb.Board) -> dict[c.Color, dict[Any, int]]:
    piece_counts = {
        color: {key: 0 for key in c.Type} for color in [c.Color.WHITE, c.Color.BLACK]
    }

    for square in c.Square:
        if (piece := board.get_piece_by_square(square)) is not None:
            piece_counts[piece.color][piece.ptype] += 1

            # TODO: Account for doubled / blocked / isolated pawns.

    return piece_counts


def evaluate_score(board: cb.Board) -> float:
    """
    Evaluate the score for the current position.
    """

    # TODO: Enhance evaluation for openings and endgames.

    white_mobility, black_mobility = _calculate_mobility(board)
    piece_counts = _calculate_piece_counts(board)

    weight = {
        c.Type.KING: 200,
        c.Type.QUEEN: 9,
        c.Type.ROOK: 5,
        c.Type.BISHOP: 3,
        c.Type.KNIGHT: 3,
        c.Type.PAWN: 1.0,
    }

    score = sum(
        weight[piece_type]
        * (
            piece_counts[c.Color.WHITE][piece_type]
            - piece_counts[c.Color.BLACK][piece_type]
        )
        for piece_type in weight
    )

    mobility_weight = 0.1
    score += mobility_weight * (white_mobility - black_mobility)

    return score


def _minimax(board: cb.Board, depth: int, maximizing: bool) -> float:
    assert depth >= 0

    if depth == 0:
        # TODO: quiescence search instead of evaluating right away.
        return evaluate_score(board)

    if maximizing:
        max_eval = float("-inf")
        for move in cm.generate_all_legal_moves(board):
            new_board = deepcopy(board)
            new_board.make_move(move)
            evaluation = _minimax(new_board, depth - 1, False)
            max_eval = max(max_eval, evaluation)
        return max_eval
    else:
        min_eval = float("inf")
        for move in cm.generate_all_legal_moves(board):
            new_board = deepcopy(board)
            new_board.make_move(move)
            evaluation = _minimax(new_board, depth - 1, True)
            min_eval = min(min_eval, evaluation)
        return min_eval


def best_move(board: cb.Board, depth: int) -> c.Move | None:
    """
    Evaluate the best move for the current position. A return value of `None` indicates
    there are no best moves, which can only happen if the game is over.
    """

    if depth < 1:
        raise ValueError("The minimum allowed depth is 1")

    best: c.Move | None = None
    maximizing = board.active_color == c.Color.WHITE

    if maximizing:
        best_value = float("-inf")
        for move in cm.generate_all_legal_moves(board):
            new_board = deepcopy(board)
            new_board.make_move(move)
            move_value = _minimax(new_board, depth - 1, False)
            if move_value > best_value:
                best_value = move_value
                best = move
    else:
        best_value = float("inf")
        for move in cm.generate_all_legal_moves(board):
            new_board = deepcopy(board)
            new_board.make_move(move)
            move_value = _minimax(new_board, depth - 1, True)
            if move_value < best_value:
                best_value = move_value
                best = move

    return best
