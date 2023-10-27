from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import chessy.core as c
import chessy.core.board as cb
import chessy.core.movegen as cm


class EvaluationInfoReporter(ABC):
    @abstractmethod
    def report_info(
        self, *, depth: int, best_evaluation: float, pv: list[c.Move]
    ) -> None:
        raise NotImplementedError


class _NilInfoReporter(EvaluationInfoReporter):
    def report_info(
        self, *, depth: int, best_evaluation: float, pv: list[c.Move]
    ) -> None:
        pass


class Evaluator:
    _stop_search: bool = False
    _info_reporter: EvaluationInfoReporter

    def __init__(self, info_reporter: EvaluationInfoReporter | None = None) -> None:
        """
        If instantiated without an `info_reporter`, all infos are suppressed.
        """

        if info_reporter is None:
            self._info_reporter = _NilInfoReporter()
        else:
            self._info_reporter = info_reporter
        self._reset_search_params()

    def start_search(
        self,
        board: cb.Board,
        *,
        max_depth: int,
    ) -> c.Move | None:
        self._reset_search_params()

        if max_depth < 1:
            raise ValueError("The minimum allowed depth is 1")

        subdepth_bestmove: c.Move | None = None
        for subdepth in range(1, max_depth + 1):
            if self._stop_search:
                break

            if (result := self._perform_search(board, subdepth)) is not None:
                pv, evaluation = result
                assert len(pv) >= 1
                subdepth_bestmove = pv[0]
                self._info_reporter.report_info(
                    depth=subdepth, best_evaluation=evaluation, pv=pv
                )

        return subdepth_bestmove

    def _perform_search(
        self, board: cb.Board, depth: int
    ) -> tuple[list[c.Move], float] | None:
        maximizing = board.active_color == c.Color.WHITE
        best_value = float("-inf") if maximizing else float("inf")
        pv: list[c.Move] = []

        for move in cm.generate_all_legal_moves(board):
            if self._stop_search:
                return None

            board.make_move(move)
            new_pv: list[c.Move] = []
            move_value = self._minimax(board, depth - 1, not maximizing, new_pv)
            board.unmake_move()

            if (maximizing and move_value > best_value) or (
                not maximizing and move_value < best_value
            ):
                best_value = move_value
                pv = [move, *new_pv]

        return pv, best_value

    def stop_search(self) -> None:
        self._stop_search = True

    def _reset_search_params(self) -> None:
        self._stop_search = False

    def _minimax(
        self, board: cb.Board, depth: int, maximizing: bool, current_pv: list[c.Move]
    ) -> float:
        assert depth >= 0

        local_best_pv: list[c.Move] = []
        previous_evaluation = float("-inf") if maximizing else float("inf")

        if self._stop_search:
            return previous_evaluation

        if depth == 0:
            # TODO: quiescence search instead of evaluating right away.
            return self._evaluate_score(board)

        for move in cm.generate_all_legal_moves(board):
            if self._stop_search:
                return previous_evaluation

            board.make_move(move)
            new_pv: list[c.Move] = []
            evaluation = self._minimax(board, depth - 1, not maximizing, new_pv)
            board.unmake_move()

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
        # We must reset en passant target, otherwise the board can count the en passant
        # as a possible move for the other side.
        prev_en_passant_tg = board.en_passant_target
        board.active_color = board.active_color.invert()
        board.en_passant_target = None

        other_side_legal_moves = cm.generate_all_legal_moves(board)
        board.en_passant_target = prev_en_passant_tg
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

        return piece_counts

    @classmethod
    def _evaluate_score(cls, board: cb.Board) -> float:
        # TODO: Enhance evaluation for openings and endgames.
        # TODO: Account for doubled / blocked / isolated pawns.

        white_mobility, black_mobility = cls._calculate_mobility(board)
        piece_counts = cls._calculate_piece_counts(board)

        if (
            board.active_color == c.Color.WHITE
            and white_mobility == 0
            and piece_counts[c.Color.WHITE][c.Type.KING] == 1
        ) or (
            board.active_color == c.Color.BLACK
            and black_mobility == 0
            and piece_counts[c.Color.BLACK][c.Type.KING] == 1
        ):
            # Stalemate
            return 0

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
