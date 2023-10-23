from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import chessy.core as c
import chessy.core.board as cb
import chessy.core.movegen as cm


class Evaluator:
    last_best_move: c.Move | None
    last_best_evaluation: float
    last_best_pv: list[c.Move]
    _stop_search: bool = False

    def start_search(
        self,
        board: cb.Board,
        *,
        depth: int,
        on_search_completed: Callable[[], None] | None = None,
    ) -> None:
        self.reset_search_results()

        if depth < 1:
            raise ValueError("The minimum allowed depth is 1")

        maximizing = board.active_color == c.Color.WHITE
        best_value = float("-inf") if maximizing else float("inf")

        for move in cm.generate_all_legal_moves(board):
            if self._stop_search:
                return

            # TODO (perf): Make a `Board.unmake_last_move` so we don't have to deepcopy board.
            new_board = deepcopy(board)
            new_board.make_move(move)
            new_pv: list[c.Move] = []
            move_value = self._minimax(new_board, depth - 1, not maximizing, new_pv)

            if (maximizing and move_value > best_value) or (
                not maximizing and move_value < best_value
            ):
                best_value = move_value
                self.last_best_move = move
                self.last_best_evaluation = best_value
                self.last_best_pv = [move, *new_pv]

        if on_search_completed is not None:
            on_search_completed()

    def stop_search(self) -> None:
        self._stop_search = True

    def reset_search_results(self) -> None:
        self._stop_search = False
        self.last_best_move = None
        self.last_best_evaluation = 0.0
        self.last_best_pv = []

    def _minimax(
        self, board: cb.Board, depth: int, maximizing: bool, current_pv: list[c.Move]
    ) -> float:
        assert depth >= 0

        if self._stop_search:
            return self.last_best_evaluation

        if depth == 0:
            # TODO: quiescence search instead of evaluating right away.
            return Evaluator._evaluate_score(board)

        local_best_pv: list[c.Move] = []
        previous_evaluation = float("-inf") if maximizing else float("inf")

        for move in cm.generate_all_legal_moves(board):
            if self._stop_search:
                return self.last_best_evaluation

            # TODO (perf): Make a `Board.unmake_last_move` so we don't have to deepcopy board.
            new_board = deepcopy(board)
            new_board.make_move(move)
            new_pv: list[c.Move] = []
            evaluation = self._minimax(new_board, depth - 1, not maximizing, new_pv)

            if (maximizing and evaluation > previous_evaluation) or (
                not maximizing and evaluation < previous_evaluation
            ):
                previous_evaluation = evaluation
                local_best_pv = [move, *new_pv]

        current_pv[:] = local_best_pv
        return previous_evaluation

    @staticmethod
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

    @staticmethod
    def _calculate_piece_counts(board: cb.Board) -> dict[c.Color, dict[Any, int]]:
        piece_counts = {
            color: {key: 0 for key in c.Type}
            for color in [c.Color.WHITE, c.Color.BLACK]
        }

        for square in c.Square:
            if (piece := board.get_piece_by_square(square)) is not None:
                piece_counts[piece.color][piece.ptype] += 1

                # TODO: Account for doubled / blocked / isolated pawns.

        return piece_counts

    @staticmethod
    def _evaluate_score(board: cb.Board) -> float:
        # TODO: Enhance evaluation for openings and endgames.

        white_mobility, black_mobility = Evaluator._calculate_mobility(board)
        piece_counts = Evaluator._calculate_piece_counts(board)

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
