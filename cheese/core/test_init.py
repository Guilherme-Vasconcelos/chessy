import pytest

import cheese.core as c


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ("e2e4", c.Move(c.Square.e2, c.Square.e4)),
        ("e7e8n", c.Move(c.Square.e7, c.Square.e8, c.Type.KNIGHT)),
    ],
)
def test_move_from_long_algebraic_notation(test_input: str, expected: c.Move) -> None:
    move = c.Move.from_long_algebraic_notation(test_input)
    assert move == expected


@pytest.mark.parametrize("test_input", ["e2e44", "e2e4k", "e2e", "e2", "e"])
def test_invalid_moves_from_long_algebraic_notation(test_input: str) -> None:
    with pytest.raises(ValueError):
        c.Move.from_long_algebraic_notation(test_input)
