import os
from sys import argv
from time import sleep

import cheese.board as cb
import cheese.evaluator as ce


def main() -> None:
    if len(argv) == 1:
        # Initial position
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    else:
        fen = argv[1]

    b = cb.Board.from_fen(fen)
    while True:
        os.system("clear")  # noqa: S605, S607 (this is just temporary code)
        print("Current position:")
        b.draw_ascii()
        sleep(2)
        print("Generating best move...")
        best = ce.best_move(b, 2)
        if best is None:
            break
        print(f"Best move is {best}. Playing it.")
        sleep(2)
        b.make_move(best)

    print("Game is over")


if __name__ == "__main__":
    main()
