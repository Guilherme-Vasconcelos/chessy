import logging
import sys
from dataclasses import dataclass
from enum import Enum, auto
from threading import Thread
from typing import NoReturn

import chessy
import chessy.core as c
import chessy.core.board as cb
import chessy.core.evaluator as ce
import chessy.core.fen_parser as fp
import chessy.utils as ut

logger = logging.getLogger(__name__)


class _Command:
    pass


class _UserCommand(_Command):
    pass


class _EngineCommand(_Command):
    pass


##


class _Uci(_UserCommand):
    pass


class _IsReady(_UserCommand):
    pass


class _UciNewGame(_UserCommand):
    pass


@dataclass
class _Position(_UserCommand):
    initial_fen: str
    initial_moves: list[c.Move]


class _GoMode(Enum):
    INFINITE = auto()
    BY_DEPTH = auto()


@dataclass
class _Go(_UserCommand):
    mode: _GoMode
    depth: int  # Only meaningful if `mode` is `BY_DEPTH`.


class _Stop(_UserCommand):
    pass


class _Quit(_UserCommand):
    pass


##


@dataclass
class _Id(_EngineCommand):
    name: str
    author: str


class _UciOk(_EngineCommand):
    pass


class _ReadyOk(_EngineCommand):
    pass


@dataclass
class _BestMove(_EngineCommand):
    move: c.Move


@dataclass
class _Info(_EngineCommand):
    depth: int
    cp: int
    pv: list[c.Move]


initial_position_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


class UciEngine:
    _board: cb.Board
    _evaluator: ce.Evaluator
    _engine_thread: Thread | None
    _last_complete_run_best_move: c.Move | None
    _stop_search: bool

    def __init__(self) -> None:
        self._board = cb.Board.from_fen(initial_position_fen)
        self._evaluator = ce.Evaluator()
        self._engine_thread = None
        self._last_complete_run_best_move = None
        self._stop_search = False

    def _reset_engine_params(self) -> None:
        self._engine_thread = None
        self._last_complete_run_best_move = None
        self._stop_search = False

    def main_loop(self) -> NoReturn:
        logger.info("--- Booting UCI engine: starting main loop ---")

        while True:
            command = self._read_user_cli_command()
            if command is None:
                logger.warning(
                    "%s failed: a user command was likely ignored. "
                    "Make sure this is intentional. Proceeding.",
                    self._read_user_cli_command.__name__,
                )
                continue

            self._handle_user_command(command)

    def _handle_user_command(self, command: _UserCommand) -> None:  # noqa: PLR0915
        match command:
            case _Uci():
                self._send_engine_command(
                    _Id(
                        f"{chessy.__name__} v{chessy.__version__}",
                        chessy.__author__,
                    )
                )
                self._send_engine_command(_UciOk())

            case _IsReady():
                self._send_engine_command(_ReadyOk())

            case _UciNewGame():
                self._reset_engine_params()
                # Resetting board to initial state isn't explicitly required  by the
                # protocol, however, if the person does a ucinewgame followed by a go
                # command, it can be presumed they want to restart the game (even though
                # they should've sent a position command in between).
                logger.info("Resetting board to initial position")
                self._board = cb.Board.from_fen(initial_position_fen)

            case _Position(fen, moves):
                self._reset_engine_params()
                try:
                    logger.info("Making board from fen %s", fen)

                    board = cb.Board.from_fen(fen)
                    self._board = board

                    logger.debug("Current board:\n%s", self._board.make_ascii_repr())
                except (fp.FenValidationError, cb.UnreachablePositionError) as e:
                    logger.info("Unable to set position as it is invalid: %s", e)
                    return

                for move in moves:
                    try:
                        logger.info("Making move %s", move)

                        self._board.make_move(move)
                    except cb.IllegalMoveError as e:
                        logger.info("Ignoring illegal move: %s", e)
                logger.debug(
                    "Current board after making moves:\n%s",
                    self._board.make_ascii_repr(),
                )

            case _Go(mode, upperbound_depth):
                if self._engine_thread is not None and self._engine_thread.is_alive():
                    logger.info(
                        "Unable to start new go command - thread is already busy"
                    )
                    return

                def update_last_best_move(evaluated_depth: int) -> None:
                    best_move = self._evaluator.last_best_move
                    cp = int(self._evaluator.last_best_evaluation * 100)
                    pv = self._evaluator.last_best_pv

                    self._last_complete_run_best_move = best_move
                    # TODO: we should invert the report control. Since the UCI interface
                    # is currently doing the reports, it also has to control stuff about
                    # the evaluator (e.g. which depth is being searched), which will
                    # limit us in the future (will be harder to report seldepth etc.).
                    # Instead, the evaluator should receive a `reporter` object and do
                    # all the info reporting itself. This will also simplify things here
                    # since UCI can just say `start_search(max_depth=N)` and done (no
                    # need to loop from 1 over to max+1 etc.)
                    self._send_engine_command(_Info(evaluated_depth, cp, pv))

                def base_think(inclusive_maxdepth: int) -> None:
                    for d in range(1, inclusive_maxdepth + 1):
                        if self._stop_search:
                            break

                        logger.info("Starting calc for depth %d", d)
                        self._evaluator.start_search(
                            self._board,
                            depth=d,
                            on_search_completed=lambda: update_last_best_move(
                                d  # noqa: B023 (false positive, see other comments)
                            ),
                        )
                    if self._last_complete_run_best_move is None:
                        logger.warning(
                            "Evaluator did not have enough time to calc a move"
                        )
                    else:
                        logger.info(
                            "Either calculation completed, or search was "
                            "aborted. Reporting last best move."
                        )
                        self._send_engine_command(
                            _BestMove(self._last_complete_run_best_move)
                        )
                    self._reset_engine_params()

                match mode:
                    case _GoMode.INFINITE:
                        logger.info("Starting infinite calc")

                        def think() -> None:
                            base_think(99)

                    case _GoMode.BY_DEPTH:
                        if upperbound_depth < 1:
                            logger.error(
                                "A depth of %d was sent for a depth-based go",
                                upperbound_depth,
                            )
                            return None

                        def think() -> None:
                            base_think(upperbound_depth)

                self._engine_thread = Thread(target=think)
                self._engine_thread.start()

            case _Stop():
                self._evaluator.stop_search()
                self._stop_search = True

            case _Quit():
                sys.exit(0)

            case _:
                ut.unreachable()

    def _send_engine_command(self, command: _EngineCommand) -> None:
        match command:
            # Without making thread-exclusive print calls, we could end up mixing
            # commands in the same line. So do not use bare `print` here.
            case _UciOk():
                ut.thread_exclusive_print("uciok")

            case _Id(name, author):
                ut.thread_exclusive_print(f"id name {name}")
                ut.thread_exclusive_print(f"id author {author}")

            case _ReadyOk():
                ut.thread_exclusive_print("readyok")

            case _BestMove(move):
                ut.thread_exclusive_print(
                    f"bestmove {move.to_long_algebraic_notation()}"
                )

            case _Info(depth, cp, pv):
                formatted_pv = " ".join(
                    [move.to_long_algebraic_notation() for move in pv]
                )
                ut.thread_exclusive_print(
                    f"info depth {depth} score cp {cp} pv {formatted_pv}"
                )

            case _:
                ut.unreachable()

    @staticmethod
    def _read_user_cli_command() -> _UserCommand | None:  # noqa: PLR0911
        user_input = input().strip()
        command, *args = user_input.split()

        match command:
            case "uci":
                return _Uci()

            case "isready":
                return _IsReady()

            case "ucinewgame":
                return _UciNewGame()

            case "position":
                try:
                    position_identifier, *rest = args
                except ValueError:
                    logger.info(
                        "Got position command without any args - unable to proceed."
                    )
                    return None
                pos_parse_result = _UciArgParser.parse_position_args(
                    position_identifier, rest
                )
                if pos_parse_result is None:
                    return None
                initial_fen, moves = pos_parse_result

                return _Position(initial_fen, moves)

            case "go":
                go_parse_result = _UciArgParser.parse_go_args(args)
                if go_parse_result is None:
                    return None
                mode, depth = go_parse_result

                return _Go(mode, depth)

            case "stop":
                return _Stop()

            case "quit":
                return _Quit()

            case _:
                logger.info("Invalid user UCI command: '%s', ignoring it.", command)
                return None


class _UciArgParser:
    @classmethod
    def parse_position_args(
        cls, position_identifier: str, rest_args: list[str]
    ) -> tuple[str, list[c.Move]] | None:
        result = cls.parse_position_args__fen(position_identifier, rest_args)
        if result is None:
            return None
        (initial_fen, maybe_move_list) = result
        moves = cls.parse_position_args__movelist(maybe_move_list)
        return (initial_fen, moves)

    @staticmethod
    def parse_position_args__fen(
        position_identifier: str, fen_or_movelist: list[str]
    ) -> tuple[str, list[str]] | None:
        if position_identifier == "startpos":
            initial_fen = initial_position_fen

        elif position_identifier == "fen":
            if len(fen_or_movelist) == 0:
                logger.info(
                    "Attempt to set up a position by fen but fen value was not "
                    "provided."
                )
                return None

            try:
                (
                    piece_placement,
                    active_color,
                    castling_availability,
                    en_passant_target,
                    halfmove_clock,
                    fullmove_count,
                    *fen_or_movelist,
                ) = fen_or_movelist
            except ValueError:
                logger.info(
                    "Attempt to set up a position by fen, but fen is incomplete: %s",
                    fen_or_movelist,
                )
                return None
            initial_fen = (
                f"{piece_placement} {active_color} "
                f"{castling_availability} {en_passant_target} {halfmove_clock} "
                f"{fullmove_count}"
            )
        else:
            logger.info(
                "Attempt to set up a position, but option '%s' is unrecognized.",
                position_identifier,
            )
            return None

        return initial_fen, fen_or_movelist

    @staticmethod
    def parse_position_args__movelist(maybe_move_list: list[str]) -> list[c.Move]:
        move_list_min_length = 2
        moves: list[c.Move] = []
        if len(maybe_move_list) >= move_list_min_length:
            if maybe_move_list[0] != "moves":
                logger.info(
                    "Cannot parse move list as it does not start with `moves`: %s",
                    maybe_move_list,
                )
            else:
                for value in maybe_move_list[1:]:
                    try:
                        moves.append(c.Move.from_long_algebraic_notation(value))
                    except ValueError:
                        logger.info(
                            "Move '%s' could not be parsed as long algebraic "
                            "notation. ",
                            value,
                        )
        elif len(maybe_move_list) == 1:
            logger.info(
                "Expected move list to have size 2: `moves` + <at least 1 move> "
                "but got only %s",
                maybe_move_list,
            )
        return moves

    @staticmethod
    def parse_go_args(args: list[str]) -> tuple[_GoMode, int] | None:
        depth = -1
        go_mode: _GoMode | None = None
        for i, value in enumerate(args):
            match value:
                case "infinite":
                    go_mode = _GoMode.INFINITE

                case "depth" if i < len(args) - 1:
                    depth_value = args[i + 1]
                    try:
                        depth = int(depth_value)
                    except ValueError:
                        logger.info("%s is not a valid depth, ignoring.", depth_value)
                        continue
                    go_mode = _GoMode.BY_DEPTH

                case _:
                    logger.info("Unrecognized go arg: %s. Ignoring..", value)

        if go_mode is None:
            logger.info("go command does not specify any mode, unable to proceed")
            return None

        return go_mode, depth
