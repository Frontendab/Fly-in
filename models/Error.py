from typing import Dict, List, Any
from abc import ABC, abstractmethod
from sys import exit, stderr


class Error(ABC):
    def __init__(self, errors: list) -> None:
        self.errors: list = errors

    @abstractmethod
    def format_errors(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def display_errors(self, errors: List[Dict[str, Any]]) -> None:
        pass


class PydanticError(Error):
    def format_errors(self) -> List[Dict[str, Any]]:
        response: List[Dict[str, Any]] = []
        for error in self.errors:

            msg = error.get('msg', 'Empty!')
            field, = error.get('loc', 'Empty!')
            user_input = (
                error.get('input', "Empty!")
                if error.get('input', "Empty!") else "Empty!"
            )
            if "Value error," in msg:
                msg = msg.split("Value error,")[1].strip()

            response.append({
                "msg": msg,
                "field": field,
                "input": user_input,
            })
        return response

    def display_errors(self, errors: List[Dict[str, Any]]) -> None:
        for error in errors:
            print(
                f"Field: {error.get("field")}, input: {error.get("input")}" +
                f",  error: {error.get("msg")}", file=stderr
            )
        exit(1)
