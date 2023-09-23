from cheese.board import Board


def main() -> None:
    b = Board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    print(b)


if __name__ == "__main__":
    main()
