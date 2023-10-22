import threading
from typing import NoReturn

stdout_lock = threading.Lock()


def thread_exclusive_print(message: str) -> None:
    with stdout_lock:
        # UCI protocol relies on stdout, and as such, print statements are required in
        # some portions of the program. The reason I turned on T20 is because, for the
        # most part, we should be using a thread_exclusive_print, as it ensures lines
        # won't mix up multiple commands simultaneously.
        print(message, flush=True)  # noqa: T201


class UnreachableError(Exception):
    pass


def unreachable() -> NoReturn:
    raise UnreachableError(
        "Unreachable code detected. This should never happen. Please report a bug at https://github.com/Guilherme-Vasconcelos/chessy/issues"
    )
