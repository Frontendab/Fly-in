from typing import Dict, List, Any
from abc import ABC, abstractmethod
from sys import exit, stderr


class Error(ABC):
    """Error: Is abstract class(Interface) to inherits from it

    Args:
        ABC (_type_): It inherits from the ABC's class to be abstract
            class as interface of other classes
    """
    def __init__(self, errors: list) -> None:
        """__init__ is use to assign values to the current instance

        Args:
            errors (list): list of errors you want to handle them
        """
        self.errors: list = errors

    @abstractmethod
    def structure_errors(self) -> List[Dict[str, Any]]:
        """structure_errors is used to format the structure
            of the errors

        Returns:
            List[Dict[str, Any]]: return list of dict
                after convert errors structure
        """
        pass

    @abstractmethod
    def display_errors(self, errors: List[Dict[str, Any]]) -> None:
        """display_errors it used to display the errors
            with any format output you want it

        Args:
            errors (List[Dict[str, Any]]): it take the list of the dicts
                as errors after convert them structure
        """
        pass


class PydanticError(Error):
    """PydanticError: we use it to work catching pydantic's errors

    Args:
        Error (_type_): It inherits from Error's abstract
            class to overrides on the methods with custom implementation
    """
    def structure_errors(self) -> List[Dict[str, Any]]:
        """structure_errors is used to create new structure of
            the list's errors

        Returns:
            List[Dict[str, Any]]: Return new structure of errors
        """
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
        """display_errors is used to display the list of errors
            with any custom output format and exit with status error

        Args:
            errors (List[Dict[str, Any]]): It take list
                of new structure's errors
        """
        for error in errors:
            print(
                f"Field: {error.get('field')}, input: {error.get('input')}" +
                f",  error: {error.get('msg')}", file=stderr
            )
        exit(1)
