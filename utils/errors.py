from sys import stderr, exit


def display_errors_msg(msg: str) -> None:
    print(f"[ERROR] {msg}", file=stderr)
    exit(1)
