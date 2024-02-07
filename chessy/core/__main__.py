import argparse
import logging
import logging.config
from dataclasses import dataclass
from typing import Literal, NoReturn

import chessy.core.uci


def setup_logging(
    log_level: Literal['DEBUG', "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "detailed": {
                "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(message)s"
            },
        },
        "handlers": {
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": "chessy.log",
                "formatter": "detailed",
                "encoding": "utf-8",
            },
        },
        "root": {"level": log_level, "handlers": ["file"]},
    }

    logging.config.dictConfig(logging_config)


@dataclass(frozen=True, slots=True)
class CliArgs:
    debug: bool


def parse_cli_args() -> CliArgs:
    parser = argparse.ArgumentParser(description="chessy chess engine")
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        default=False,
        help="include extra debug logs",
    )
    args = parser.parse_args()
    return CliArgs(debug=args.debug)


def main() -> NoReturn:
    cli_args = parse_cli_args()
    log_level: Literal["DEBUG", "INFO"] = "DEBUG" if cli_args.debug else "INFO"
    setup_logging(log_level=log_level)

    engine = chessy.core.uci.UciEngine()
    engine.main_loop()


if __name__ == "__main__":
    main()
