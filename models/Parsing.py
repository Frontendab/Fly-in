from typing import List, Dict, Any, Union
from re import match
from enum import Enum


class ConfigKeyTypes(Enum):
    """ConfigKeyTypes: Is Enum class that contain const variables
        to use them in any part of project

    Args:
        Enum (_type_): It Enum class we inherits from it
            to be this class as enum's class
    """
    NB = "nb_drones:"
    START = "start_hub:"
    END = "end_hub:"
    HUBS = "hub:"
    CONN = "connection:"


class FileParser:
    """FileParser is the class responsible on the parsing
    """
    def __init__(self, file_name: str) -> None:
        """__init__ is use to assign values to the current instance
        """
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_zone: Dict[str, Any] = {}
        self.end_zone: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.__metadata_zones = ("color", "zone", "max_drones")
        self.__metadata_connection = ("max_link_capacity")

    def parse(self) -> Dict[str, Any]:
        """parse's method is used to parsing and check
            all the content of the file name

        Returns:
            Dict[str, Any]: return Dict of the file's data after paring it
        """
        from utils import raise_errors_msg

        finding = {
            ConfigKeyTypes.NB.value: 0,
            ConfigKeyTypes.START.value: 0,
            ConfigKeyTypes.END.value: 0,
        }
        with open(self.file_name, "r") as file:
            lines = file.readlines()

            if not lines:
                raise_errors_msg(
                    "File is empty!"
                )

            for num, line in enumerate(lines, start=1):
                connection = {}
                hub = {}
                metadata_dict: Dict[str, Union[str, int]] = {}
                if line[-1] == '\n':
                    line = line[:-1]

                if line.startswith("#"):
                    continue

                if not line.strip():
                    continue

                if ConfigKeyTypes.NB.value in line:
                    is_match = match(r"^nb_drones: [0-9]+$", line)
                    finding[ConfigKeyTypes.NB.value] += 1
                    count_find_nb_drones = finding.get(ConfigKeyTypes.NB.value)
                    if count_find_nb_drones and count_find_nb_drones > 1:
                        raise_errors_msg(
                            f"Line {num}: Duplicate {ConfigKeyTypes.NB.value}"
                        )
                    if not is_match:
                        raise_errors_msg(
                            f"Line {num}: Invalid line Format\n"
                            "The first line must start with the following"
                            " pattern:\n-> nb_drones: <number>\n"
                            "Please check your input file and try again."
                        )
                    nb_drones = line.split(" ", 1)[1]
                    self.nb_drones = int(nb_drones)

                if (ConfigKeyTypes.HUBS.value in line
                        or ConfigKeyTypes.START.value in line
                        or ConfigKeyTypes.END.value in line
                        or "connection" in line):

                    type_hub = ""
                    is_match = None
                    pattern_hub = r"^start_hub:\s(\w+)\s(-?\d+)\s(-?\d+)"
                    pattern_hub += r"(?:\s+\[(.*)\])?"
                    if ConfigKeyTypes.START.value in line:
                        is_match = match(
                            pattern_hub,
                            line
                        )
                        type_hub = ConfigKeyTypes.START.value
                        finding[ConfigKeyTypes.START.value] += 1
                        count_find_start = finding.get(
                            ConfigKeyTypes.START.value
                        )
                        if count_find_start and count_find_start > 1:
                            raise_errors_msg(
                                f"Line {num}: Duplicate " +
                                f"{ConfigKeyTypes.START.value}"
                            )
                    elif ConfigKeyTypes.END.value in line:
                        pattern_end = r"^end_hub:\s(\w+)\s(-?\d+)\s(-?\d+)"
                        pattern_end += r"(?:\s+\[(.*)\])?"
                        is_match = match(
                            pattern_end,
                            line
                        )
                        type_hub = ConfigKeyTypes.END.value
                        finding[ConfigKeyTypes.END.value] += 1
                        count_find_end = finding.get(ConfigKeyTypes.END.value)
                        if count_find_end and count_find_end > 1:
                            raise_errors_msg(
                                f"Line {num}: Duplicate " +
                                F"{ConfigKeyTypes.END.value}"
                            )
                    elif ConfigKeyTypes.CONN.value in line:
                        is_match = match(
                            r"^connection:\s(\w+)-(\w+)(?:\s+\[(.*)\])?",
                            line
                        )
                        type_hub = ConfigKeyTypes.CONN.value
                    else:
                        is_match = match(
                            r"^hub:\s(\w+)\s(-?\d+)\s(-?\d+)(?:\s+\[(.*)\])?",
                            line
                        )
                        type_hub = ConfigKeyTypes.HUBS.value

                    if not is_match:
                        raise_errors_msg(
                            f"Line {num}: Invalid line Format\n"
                            "it must be following this pattern\n"
                            f"-> {type_hub} <name> <number> <number> " +
                            "[color=green]\n"
                            "Metadata is optional, Please check your "
                            "input file and try again."
                        )

                    if type_hub != ConfigKeyTypes.CONN.value and is_match:
                        name, x, y, metadata = is_match.groups()
                    elif type_hub == ConfigKeyTypes.CONN.value and is_match:
                        name_a, name_b, metadata = is_match.groups()

                    if metadata:
                        if (
                            type_hub != ConfigKeyTypes.CONN.value
                            and not line.split(" ")[3].isdigit()
                        ):
                            raise_errors_msg(
                                f"Line {num}: Invalid"
                                " metadata format!"
                            )

                        metadata_items = (
                            metadata.split(" ")
                        )
                        for meta in metadata_items:
                            if meta:
                                if "=" not in meta or meta.count("=") > 1:
                                    raise_errors_msg(
                                        f"Line {num}: Invalid ({meta})"
                                        " metadata format!"
                                    )
                                key, value = meta.split("=", 1)
                                if not value:
                                    raise_errors_msg(
                                        f"Line {num}: Value({key}) of the " +
                                        "key must be not empty!"
                                    )
                                if (type_hub != ConfigKeyTypes.CONN.value
                                        and key not in self.__metadata_zones):
                                    raise_errors_msg(
                                        f"Line {num}: Invalid zones's" +
                                        " metadata, " +
                                        f"expected: {self.__metadata_zones}!"
                                    )
                                elif (type_hub == ConfigKeyTypes.CONN.value
                                        and
                                        key not in self.__metadata_connection):
                                    raise_errors_msg(
                                        f"Line {num}: Invalid connection's"
                                        " metadata, " +
                                        "expected: " +
                                        f"{self.__metadata_connection}!"
                                    )
                                metadata_dict[key] = value
                                if "max_drones" in key:
                                    metadata_dict[key] = int(value)
                        if self.is_duplicate_metadata_key(metadata_items):
                            raise_errors_msg(
                                f"Line {num}: Duplicate metadata key!"
                            )
                    else:
                        if len(line.split(" ")) > 4:
                            raise_errors_msg(
                                f"Line {num}: Invalid"
                                " metadata format!"
                            )

                    if ConfigKeyTypes.START.value in line:
                        hub.update({
                            "name": name,
                            "x": int(x),
                            "y": int(y),
                            "metadata": metadata_dict
                        })
                        msg = self.is_duplicate_zone(hub)
                        if msg:
                            raise_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        self.start_zone = hub
                    elif ConfigKeyTypes.END.value in line:
                        hub.update({
                            "name": name,
                            "x": int(x),
                            "y": int(y),
                            "metadata": metadata_dict
                        })
                        msg = self.is_duplicate_zone(hub)
                        if msg:
                            raise_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        self.end_zone = hub
                    elif ConfigKeyTypes.HUBS.value in line:
                        hub.update({
                            "name": name,
                            "x": int(x),
                            "y": int(y),
                            "metadata": metadata_dict
                        })
                        msg = self.is_duplicate_zone(hub)
                        if msg:
                            raise_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        self.hubs.append(hub)
                    elif ConfigKeyTypes.CONN.value in line:
                        connection.update({
                            "name_a": name_a,
                            "name_b": name_b,
                            "metadata": metadata_dict
                        })
                        msg = self.is_duplicate_connection(connection)
                        if msg:
                            raise_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        self.connections.append(connection)

                elif ConfigKeyTypes.NB.value not in line:
                    raise_errors_msg(
                        f"Line {num}: Unsupported line: {line}"
                    )

            if finding.get(ConfigKeyTypes.NB.value, 0) == 0:
                raise_errors_msg(
                    f"{ConfigKeyTypes.NB.value} doesn't exist!"
                )

            if finding.get(ConfigKeyTypes.START.value) == 0:
                raise_errors_msg(
                    f"{ConfigKeyTypes.START.value} doesn't exist!"
                )

            if finding.get(ConfigKeyTypes.END.value) == 0:
                raise_errors_msg(
                    f"{ConfigKeyTypes.END.value} doesn't exist!"
                )

        metadata_start = self.start_zone.get("metadata")
        start_max, end_max = 1, 1
        if metadata_start:
            start_max = metadata_start.get("max_drones", 1)
        metadata_end = self.start_zone.get("metadata")
        if metadata_end:
            end_max = metadata_end.get("max_drones", 1)

        if start_max < self.nb_drones or end_max < self.nb_drones:
            raise_errors_msg(
                "'max_drones' in start/end zones must be qual or " +
                "greater than 'nb_drones'!"
            )

        return {
            ConfigKeyTypes.NB.value: self.nb_drones,
            ConfigKeyTypes.START.value: self.start_zone,
            ConfigKeyTypes.END.value: self.end_zone,
            ConfigKeyTypes.HUBS.value: self.hubs,
            ConfigKeyTypes.CONN.value: self.connections
        }

    def is_duplicate_zone(self, hub: Dict[str, Any]) -> bool | str:
        """is_duplicate_zone: Is used to check if the hub's zone is duplicated

        Args:
            hub (Dict[str, Any]): the zone you want check it is duplicated
                or not

        Returns:
            bool | str: Return(False) if the zone doesn't duplicated
                otherwise return helpful message to display it to user
        """

        if self.start_zone:
            if self.start_zone.get("name") == hub.get("name"):
                return (
                    f"Duplicate \"{hub.get('name')}\" name!"
                )
            elif (self.start_zone.get("x") == hub.get("x")
                    and self.start_zone.get("y") == hub.get("y")):
                return (
                    f"Duplicate \"{hub.get('name')}\" with " +
                    f"\"{self.start_zone.get('name')}\" coordinates!"
                )
        if self.end_zone:
            if self.end_zone.get("name") == hub.get("name"):
                return (
                    f"Duplicate \"{hub.get('name')}\" name!"
                )
            elif (self.end_zone.get("x") == hub.get("x")
                    and self.end_zone.get("y") == hub.get("y")):
                return (
                    f"Duplicate \"{hub.get('name')}\" with " +
                    f"\"{self.end_zone.get('name')}\" coordinates!"
                )
        for zone in self.hubs:
            if zone.get("name") == hub.get("name"):
                return f"Duplicate \"{hub.get('name')}\" name!"
            elif (zone.get("x") == hub.get("x")
                    and zone.get("y") == hub.get("y")):
                return (
                    f"Duplicate \"{hub.get('name')}\" with " +
                    f"\"{zone.get('name')}\" coordinates!"
                )
        return False

    def is_duplicate_metadata_key(self, metadata: List[str]) -> bool:
        # TODO: I think i have to improve this method how i can check if is duplicated key
        # Todo: Because if there are any key in the start and in the end it need to be detected
        """is_duplicate_metadata_key: We use it to check if
            they metadata's keys duplicated or not

        Args:
            metadata (List[str]): Metadata that you want check it

        Returns:
            bool: Return False not found any duplicated otherwise return True
        """
        pre_key, _ = metadata[0].split("=", 1)
        for item in metadata[1:]:
            if item:
                key, _ = item.split("=", 1)
                if pre_key == key:
                    return True
                pre_key = key

        return False

    def is_duplicate_connection(
        self, connection: Dict[str, Any]
    ) -> bool | str:
        """is_duplicate_connection: Is it check if there are
            any duplicate connection

        Args:
            connection (Dict[str, Any]): the connection you want check
                it is duplicated

        Returns:
            bool | str: Return(False) if the connection doesn't duplicated
                otherwise return helpful message to display it to user
        """

        for conn in self.connections:
            if (conn.get("name_a") == connection.get("name_a")
                    and conn.get("name_b") == connection.get("name_b")
                    or conn.get("name_a") == connection.get("name_b")
                    and conn.get("name_b") == connection.get("name_a")):
                return (
                    f"Duplicate \"{connection.get('name_a')}\" with " +
                    f"\"{connection.get('name_b')}\" connection!"
                )

            elif not self.is_exist_zone(connection.get("name_a")):
                return (
                    f"\"{connection.get('name_a')}\" does not exist!"
                )
            elif not self.is_exist_zone(connection.get("name_b")):
                return (
                    f"\"{connection.get('name_b')}\" does not exist!"
                )

        return False

    def is_exist_zone(self, name: str | None) -> bool:
        """is_exist_zone: It used to check if the current zone is exist

        Args:
            name (str | None): the name of the zone

        Returns:
            bool: Return True if is't found otherwise return False
        """
        if self.start_zone.get("name") == name:
            return True
        elif self.end_zone.get("name") == name:
            return True

        for zone in self.hubs:
            if zone.get("name") == name:
                return True

        return False
