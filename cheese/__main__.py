import cheese as c
import cheese.board as cb


def main() -> None:
    b = cb.Board.from_fen(
        "rnbqkbnr/ppp1pppp/8/3pP3/8/P7/1PPP1PPP/RNBQKBNR w KQkq d6 0 2"
    )
    b.draw_ascii()
    # FIXME: this loses the pawn
    b.make_move(
        c.Move(c.Square.e5, c.Square.d6),
    )
    b.draw_ascii()


if __name__ == "__main__":
    main()
