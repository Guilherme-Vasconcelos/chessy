from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import cheese as c
import cheese.fen_parser as cf
import cheese.movegen as cm

BOARD_SIZE = 64


class BoardError(Exception):
    pass


class IllegalMoveError(BoardError):
    legal_moves: Iterable[c.Move]

    def __init__(self, message: str, legal_moves: Iterable[c.Move]) -> None:
        super().__init__(message)
        self.legal_moves = legal_moves


class UnreachablePositionError(BoardError):
    pass


@dataclass
class MoveResult:
    is_capture: bool
    moved_piece: c.Piece


@dataclass
class Board:
    state: list[c.Piece | None]
    active_color: c.Color
    castling_availability: c.CastlingAvailability
    en_passant_target: c.Square | None
    halfmove_clock: int
    fullmove_number: int

    def __post_init__(self) -> None:
        self._validate_current_position()

    def _validate_current_position(self) -> None:
        def assert_position_cond(cond: bool, message: str) -> None:
            if not cond:
                raise UnreachablePositionError(message)

        assert_position_cond(
            (stlen := len(self.state)) == BOARD_SIZE,
            f"Board has invalid size {stlen}, expected {BOARD_SIZE}",
        )

        assert_position_cond(
            self.halfmove_clock >= 0,
            f"Invalid halfmove_clock {self.halfmove_clock}, "
            "expected a non-negative integer",
        )

        assert_position_cond(
            self.fullmove_number >= 1,
            f"Invalid fullmove_number {self.fullmove_number}, "
            "expected a strictly positive integer",
        )

        # TODO:
        # - 1 king for each side.
        # - no pawns on ranks 0 and 7 (they would need to have promoted).
        # - Only at most 1 player can be in check. And if someone is in check,
        #   that someone must be `self.active_color`.

    @staticmethod
    def from_fen(fen: str) -> Board:
        result = cf.parse(fen)

        return Board(
            result.piece_placement,
            result.active_color,
            result.castling_availability,
            result.en_passant_target,
            result.halfmove_clock,
            result.fullmove_number,
        )

    def get_piece_by_square(self, square: c.Square) -> c.Piece | None:
        return self.state[square.value]

    def _set_piece_by_square(self, square: c.Square, piece: c.Piece | None) -> None:
        self.state[square.value] = piece

    def _get_king_position_by_color(self, color: c.Color) -> c.Square:
        king_position: c.Square | None = None
        for i, p in enumerate(self.state):
            if p is not None and p.ptype == c.Type.KING and p.color == color:
                king_position = c.Square(i)
                break
        assert king_position is not None
        return king_position

    def is_in_check(self, color: c.Color | None = None) -> bool:
        """
        Verify if the `color` is currently in check.

        If `color` is None, the verification is based on `self.active_color`.
        """

        if color is None:
            color = self.active_color

        king_position = self._get_king_position_by_color(color)
        possible_attackers_positions = cm.generate_attacks(
            self, king_position, c.Piece(c.Type.QUEEN, color)
        ) | cm.generate_attacks(self, king_position, c.Piece(c.Type.KNIGHT, color))
        for position in possible_attackers_positions:
            if (
                (attacker := self.state[position.value]) is not None
                and attacker.color == color.invert()
                # TODO (perf): We don't need to generate every single attack, but rather
                # just the ones that are likely to attack `king_position`.
                and king_position in cm.generate_attacks(self, position, attacker)
            ):
                return True

        return False

    def _validate_move(self, move: c.Move) -> None:
        legal_moves = cm.generate_legal_moves(self, move.source)

        if move not in legal_moves:
            raise IllegalMoveError(
                f"Move from {move.source} to {move.target} is illegal. "
                f"See `legal_moves` for available moves starting from {move.source}.",
                legal_moves,
            )

    def _move_is_castling(self, move: c.Move) -> bool:
        initial_white_king_position = c.Square.e1
        initial_black_king_position = c.Square.e8
        white_king_castling_targets = {c.Square.g1, c.Square.c1}
        black_king_castling_targets = {c.Square.g8, c.Square.c8}

        return (
            (source_piece := self.get_piece_by_square(move.source)) is not None
            and source_piece.ptype == c.Type.KING
            and (
                (
                    move.source == initial_white_king_position
                    and move.target in white_king_castling_targets
                )
                or (
                    move.source == initial_black_king_position
                    and move.target in black_king_castling_targets
                )
            )
        )

    def _move_is_en_passant(self, move: c.Move) -> bool:
        return (
            # If we are moving a pawn to an en passant target, we can't possibly
            # have anything other than an en passant. Otherwise, a double pawn push
            # could not have happened.
            (source_piece := self.get_piece_by_square(move.source)) is not None
            and source_piece.ptype == c.Type.PAWN
            and self.en_passant_target is not None
            and move.target == self.en_passant_target
        )

    def _make_move__state_target_update_by_promotion(self, move: c.Move) -> None:
        source_piece = self.get_piece_by_square(move.source)

        assert source_piece is not None
        assert move.promotion is not None

        self._set_piece_by_square(
            move.target, c.Piece(color=source_piece.color, ptype=move.promotion)
        )

    def _make_move__state_target_and_rook_update_by_castling(
        self, move: c.Move
    ) -> None:
        source_piece = self.get_piece_by_square(move.source)
        assert source_piece is not None

        previous_rook_positions_by_move_target = {
            # White
            c.Square.g1: c.Square.h1,
            c.Square.c1: c.Square.a1,
            # Black
            c.Square.g8: c.Square.h8,
            c.Square.c8: c.Square.a8,
        }
        assert move.target in previous_rook_positions_by_move_target

        new_rook_positions_by_move_target = {
            # White
            c.Square.g1: c.Square.f1,
            c.Square.c1: c.Square.d1,
            # Black
            c.Square.g8: c.Square.f8,
            c.Square.c8: c.Square.d8,
        }

        previous_rook_position = previous_rook_positions_by_move_target[move.target]
        self._set_piece_by_square(move.target, source_piece)
        self._set_piece_by_square(
            new_rook_positions_by_move_target[move.target],
            self.get_piece_by_square(previous_rook_position),
        )
        self._set_piece_by_square(previous_rook_position, None)

    def _make_move__state_target_update_by_en_passant(self, move: c.Move) -> None:
        source_piece = self.get_piece_by_square(move.source)
        assert self.en_passant_target is not None
        assert source_piece is not None

        direction_factor = -1 * source_piece.direction_factor()
        single_step = 8 * direction_factor

        self._set_piece_by_square(move.target, source_piece)
        self._set_piece_by_square(
            c.Square(self.en_passant_target.value + single_step), None
        )

    def _make_move__state_update(self, move: c.Move) -> MoveResult:
        is_capture = self.get_piece_by_square(move.target) is not None
        source_piece = self.get_piece_by_square(move.source)
        assert source_piece is not None

        is_promotion = move.promotion is not None
        is_castling = self._move_is_castling(move)
        is_en_passant = self._move_is_en_passant(move)

        if is_promotion:
            self._make_move__state_target_update_by_promotion(move)
        elif is_castling:
            self._make_move__state_target_and_rook_update_by_castling(move)
        elif is_en_passant:
            is_capture = True
            self._make_move__state_target_update_by_en_passant(move)
        else:
            self._set_piece_by_square(move.target, source_piece)

        self._set_piece_by_square(move.source, None)

        return MoveResult(is_capture, source_piece)

    def _update_castling_availability_after_move(
        self, moved_piece: c.Piece, move_source: c.Square
    ) -> None:
        if moved_piece.ptype == c.Type.KING:
            self.castling_availability.disable_for_color(moved_piece.color)
        elif moved_piece.ptype == c.Type.ROOK:
            self.castling_availability.disable_for_square(move_source)

    def _update_en_passant_target_after_move(
        self, moved_piece: c.Piece, performed_move: c.Move
    ) -> None:
        self.en_passant_target = None
        if moved_piece.ptype != c.Type.PAWN:
            return

        direction_factor = moved_piece.direction_factor()
        single_step = 8 * direction_factor
        double_step = 2 * single_step
        did_double_push = (
            performed_move.source.value + double_step == performed_move.target.value
        )

        if not did_double_push:
            return

        en_passant_square = c.Square(performed_move.source.value + single_step)
        target_file = performed_move.target.file()
        for offset in [-1, 1]:
            # If we are at an edge file, prevent wrapping around the board.
            if 0 <= target_file + offset <= 7:
                neighbor = self.get_piece_by_square(
                    c.Square(performed_move.target.value + offset)
                )
                if neighbor and neighbor.ptype == c.Type.PAWN:
                    self.en_passant_target = en_passant_square
                    return

    def _update_board_clocks_after_move(
        self, moved_piece: c.Piece, move_was_capture: bool
    ) -> None:
        is_halfmove_reset = move_was_capture or moved_piece.ptype == c.Type.PAWN
        is_fullcount_increment = moved_piece.color == c.Color.BLACK
        self.halfmove_clock = 0 if is_halfmove_reset else self.halfmove_clock + 1
        if is_fullcount_increment:
            self.fullmove_number += 1

    def make_move(self, move: c.Move, *, bypass_validation: bool = False) -> None:
        """
        Validate and perform the move.

        IllegalMoveError is raised if the move is illegal.

        If `bypass_validation` is set to True, illegal moves will be accepted.
        Be very careful with this option, as it may lead to a bad state. For example,
        depending on how you move a pawn, the board may think you're allowing
        an en passant. You should only use this if you have already used other means
        to figure out that the move is pseudolegal.
        """

        if not bypass_validation:
            self._validate_move(move)

        move_result = self._make_move__state_update(move)
        is_capture = move_result.is_capture
        moved_piece = move_result.moved_piece

        self._update_castling_availability_after_move(moved_piece, move.source)
        self._update_en_passant_target_after_move(moved_piece, move)
        self._update_board_clocks_after_move(moved_piece, is_capture)
        self.active_color = self.active_color.invert()

    def draw_ascii(self) -> None:
        """
        Draw an ASCII representation of the Board, useful for debugging.
        """

        print("Color to play:", self.active_color)
        print("Castling availability:", self.castling_availability)
        print("En passant target:", self.en_passant_target)
        print("Halfmove clock:", self.halfmove_clock)
        print("Fullmove number:", self.fullmove_number)
        print("Board:")

        print("    a  b  c  d  e  f  g  h")
        print("   -----------------------")

        for i in range(c.Square.a8.value, c.Square.a1.value - 1, -8):
            friendly_rank = c.Square(i).rank() + 1
            print(f"{friendly_rank} |", end="")

            for j in range(8):
                if (piece := self.get_piece_by_square(c.Square(i + j))) is None:
                    print(" - ", end="")
                else:
                    print(f" {piece.to_letter()} ", end="")
            print()
