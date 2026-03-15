import sys


def raise_errors_msg(msg: str) -> None:
    """Is used to raise message's errors

    Args:
        msg (str): The message you want to raise it

    Raises:
        ValueError: Is value error's exception to raise value's error
    """
    raise ValueError(msg)


def display_errors_msg(msg: str) -> None:
    """We use it to display a message and exit with status error

    Args:
        msg (str): The message you want to print it to the user
    """
    print(f"[ERROR]: {msg}")
    sys.exit(1)
