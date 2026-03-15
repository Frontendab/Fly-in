from .Zone import Zone
from typing import List
from pydantic import (
    BaseModel, Field,  ConfigDict,
    model_validator
)
from pydantic_core import PydanticCustomError


class ValidateDrone(BaseModel):
    """ValidateDrone is class to check if
        the Drone information is valid or not with raise errors

    Args:
        BaseModel: It inherits from BaseModel's pydantic to be
            validator's class
    """

    # ? INFO: We use model_config to create
    # ? Custom type hint(in this case: Zone) with ValidateDrone's class
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: str = Field(
        description="ID of the drone"
    )
    current_zone: Zone = Field(
        description="Current zone of the drone"
    )
    target_zone: List[Zone] = Field(
        description="Target zone of the drone"
    )
    departure_turn: int = Field(
        description="Departure turn of the current drone"
    )

    @model_validator(mode="after")
    def check_valid_id(self) -> 'ValidateDrone':
        """check_valid_id is used to check the id is start with(D)
            when it pass success Validation of ValidateDrone

        Raises:
            PydanticCustomError: is used to raise custom pydantic's error

        Returns:
            ValidateDrone: it return self after check it
                or modified it in need
        """
        if not self.id.startswith("D"):
            raise PydanticCustomError(
                "invalid_color",
                (
                    "Invalid color name. " +
                    "See: https://www.pygame.org/docs/ref/color_list.html"
                )
            )

        return self


class Drone:
    def __init__(
        self, id: str, current_zone: Zone, target_zone: List[Zone],
        departure_turn: int
    ) -> None:
        """__init__ is use to assign values to the current instance

        Args:
            id (str): id unique identifier's drone
            current_zone (Zone): Where the drone is!
            target_zone (List[Zone]): Where the drone is go!
            departure_turn (int): The time of the drone is start moving..
        """
        self.id: str = id
        self.current_zone: Zone = current_zone
        self.target_zone: List[Zone] = target_zone
        self.current_x: int = current_zone.x
        self.current_y: int = current_zone.y
        self.path: List[Zone] = []
        self.target_index: int = 0
        self.departure_turn: int = departure_turn
