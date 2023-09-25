from __future__ import annotations

import cheese as c
import cheese.board as cb


class Movegen:
    @staticmethod
    def generate_legal_moves(board: cb.Board, square: c.Square) -> list[c.Move]:
        """
        Generate all strictly legal moves starting from `square`.
        """
        # TODO: this becomes a giant match case for each ptype
        # TODO 2: do not forget to handle moves for special cases. specifically: promotions
        # (in case of pawn moves), castling (in case of king moves - read availabilty
        # from board.castling_availability) and en passant (in case of pawn moves - read
        # availability from board.en_passant_target)
        # TODO 3: if game has ended (checkmate, stalemate, etc.), remember no move is legal.
        if board.get_piece(square) is None:
            return []

        return []
