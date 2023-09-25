from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from functools import total_ordering


class Color(Enum):
    WHITE = auto()
    BLACK = auto()

    def invert(self) -> Color:
        match self:
            case Color.WHITE:
                return Color.BLACK
            case Color.BLACK:
                return Color.WHITE


class Type(Enum):
    PAWN = auto()
    KNIGHT = auto()
    BISHOP = auto()
    ROOK = auto()
    QUEEN = auto()
    KING = auto()


@dataclass
class Piece:
    ptype: Type
    color: Color

    @staticmethod
    def from_letter(letter: str) -> Piece:
        """Create a Piece from a given letter code."""

        assert len(letter) == 1 and letter.lower() in {"p", "k", "q", "r", "n", "b"}

        t: Type
        match letter.lower():
            case "p":
                t = Type.PAWN
            case "k":
                t = Type.KING
            case "q":
                t = Type.QUEEN
            case "r":
                t = Type.ROOK
            case "n":
                t = Type.KNIGHT
            case "b":
                t = Type.BISHOP
            case _:
                assert False, "unreachable"

        return Piece(ptype=t, color=Color.WHITE if letter.isupper() else Color.BLACK)

    def to_letter(self) -> str:
        """Convert the current Piece into a letter code."""

        ret: str
        match self.ptype:
            case Type.PAWN:
                ret = "p"
            case Type.KING:
                ret = "k"
            case Type.QUEEN:
                ret = "q"
            case Type.ROOK:
                ret = "r"
            case Type.KNIGHT:
                ret = "n"
            case Type.BISHOP:
                ret = "b"

        return ret.upper() if self.color.value == Color.WHITE.value else ret.lower()


@total_ordering
class Square(Enum):
    a1 = 0  # To make sure we can index Board through squares.
    b1 = auto()
    c1 = auto()
    d1 = auto()
    e1 = auto()
    f1 = auto()
    g1 = auto()
    h1 = auto()

    a2 = auto()
    b2 = auto()
    c2 = auto()
    d2 = auto()
    e2 = auto()
    f2 = auto()
    g2 = auto()
    h2 = auto()

    a3 = auto()
    b3 = auto()
    c3 = auto()
    d3 = auto()
    e3 = auto()
    f3 = auto()
    g3 = auto()
    h3 = auto()

    a4 = auto()
    b4 = auto()
    c4 = auto()
    d4 = auto()
    e4 = auto()
    f4 = auto()
    g4 = auto()
    h4 = auto()

    a5 = auto()
    b5 = auto()
    c5 = auto()
    d5 = auto()
    e5 = auto()
    f5 = auto()
    g5 = auto()
    h5 = auto()

    a6 = auto()
    b6 = auto()
    c6 = auto()
    d6 = auto()
    e6 = auto()
    f6 = auto()
    g6 = auto()
    h6 = auto()

    a7 = auto()
    b7 = auto()
    c7 = auto()
    d7 = auto()
    e7 = auto()
    f7 = auto()
    g7 = auto()
    h7 = auto()

    a8 = auto()
    b8 = auto()
    c8 = auto()
    d8 = auto()
    e8 = auto()
    f8 = auto()
    g8 = auto()
    h8 = auto()

    def rank(self) -> int:
        """Get the rank, from 0 to 7. Ranks are horizontal rows."""
        return self.value // 8

    def file(self) -> int:
        """Get the file, from 0 to 7. Files are vertical rows."""
        return self.value % 8

    def __lt__(self, other: Square) -> bool:
        return self.value < other.value


@dataclass
class CastlingAvailability:
    white_kingside: bool
    white_queenside: bool
    black_kingside: bool
    black_queenside: bool

    def disable_for_color(self, color: Color) -> None:
        if color == Color.WHITE:
            self.white_kingside = False
            self.white_queenside = False
        else:
            self.black_kingside = False
            self.black_queenside = False

    def disable_for_square(self, square: Square) -> None:
        if square == Square.a1:
            self.white_queenside = False
        elif square == Square.h1:
            self.white_kingside = False
        elif square == Square.a8:
            self.black_queenside = False
        elif square == Square.h8:
            self.black_kingside = False


@dataclass
class Move:
    source: Square
    target: Square
    promotion: Type | None = None

    def __post_init__(self) -> None:
        if self.promotion is not None:
            target_rank = self.target.rank()
            assert target_rank in {0, 7}
            assert self.promotion not in {Type.KING, Type.PAWN}
