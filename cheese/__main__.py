import cheese.board as cb
import cheese.movegen as cm


def main() -> None:
    b = cb.Board.from_fen("4k2r/r2Nn3/7p/8/1Pp5/B5p1/4Q2P/R3K2R b KQk b3 0 1")
    b.draw_ascii()
    print(cm.generate_all_legal_moves(b))


if __name__ == "__main__":
    main()
