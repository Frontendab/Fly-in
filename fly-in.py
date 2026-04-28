#! /usr/bin/env python3

# TODO: I have to fix the flake-docstrings

from classes import Engine, Utils
from sys import argv

if __name__ == "__main__":
    utils: Utils = Utils()

    if len(argv) != 2:
        utils.display_errors_msg(
            "[WARNING]: Usage (make run MAP=path)"
        )

    file_name: str = argv[1]

    engine = Engine(file_name, utils)

    engine.start_engine()
