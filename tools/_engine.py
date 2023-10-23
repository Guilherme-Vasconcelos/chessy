"""
If you need to write a tool that needs to call chessy for whatever reason, this
is a stdin/stdout wrapper to communicate with the engine through the UCI protocol.
"""


from atexit import register
from subprocess import PIPE, Popen


class Engine:
    _engine: Popen[str]

    def __init__(self) -> None:
        chessy_command = "/usr/bin/env python -m chessy"
        self._engine = Popen(
            chessy_command.split(),  # noqa: S603
            bufsize=1,
            stdin=PIPE,
            stdout=PIPE,
            text=True,
        )
        register(self._cleanup)

    def send_command(self, c: str) -> None:
        assert self._engine.stdin is not None
        self._engine.stdin.write(c)

    def read_response(self) -> str:
        assert self._engine.stdout is not None
        return self._engine.stdout.readline()

    def wait_for_response(self, value: str) -> None:
        while self.read_response() != value:
            pass

    def wait_for_response_containing(self, value: str) -> None:
        while value not in self.read_response():
            pass

    def handshake(self) -> None:
        self.send_command("uci\n")
        self.wait_for_response("uciok\n")
        self.send_command("ucinewgame\n")
        self.send_command("isready\n")
        self.wait_for_response("readyok\n")

    def _cleanup(self) -> None:
        # This ensures we don't get an EOFError when the caller process terminates.
        # I think the reason of the EOFError is because stdin closes before the process.
        self._engine.terminate()
