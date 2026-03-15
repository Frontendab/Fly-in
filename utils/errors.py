import sys


def raise_errors_msg(msg: str) -> None:
    raise ValueError(msg)


def display_errors_msg(msg: str) -> None:
    print(f"[ERROR]: {msg}")
    sys.exit(1)
