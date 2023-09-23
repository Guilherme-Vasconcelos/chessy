from __future__ import annotations

from cheese import Piece
from cheese.fen_parser import parse as parse_fen

BOARD_SIZE = 64


class Board:
    _state: list[Piece | None]

    def __init__(self, state: list[Piece | None]) -> None:
        assert len(state) == BOARD_SIZE

        self._state = state

    @staticmethod
    def from_fen(fen: str) -> Board:
        parsed_fen = parse_fen(fen)

        # TODO: all the other data in the FEN must be in the board too
        return Board(parsed_fen.piece_placement)
