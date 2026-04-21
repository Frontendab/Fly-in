from collections import defaultdict
from typing import List, Dict, Any
from re import match
from enum import Enum
from sys import stderr, exit
from classes import ZoneTypes


def display_errors_msg(msg: str) -> None:
    """
    Display an error message to stderr and exit the program.

    Args:
        msg (str): The error message to display.

    Exits:
        With code 1 after printing the error.
    """
    print(f"[ERROR] {msg}", file=stderr)
    exit(1)


class ConfigKeyTypes(Enum):
    """
    Enumeration of configuration key types used in parsing.

    Defines the prefixes for different configuration elements in the file.
    """
    NB = "nb_drones:"
    START = "start_hub:"
    END = "end_hub:"
    HUBS = "hub:"
    CONN = "connection:"


class FileParser:
    """
    Parser for Fly-in configuration files.

    Parses map files to extract drone counts, zones (start, end, hubs),
    and connections with their metadata and validation.
    """

    def __init__(self, file_name: str) -> None:
        """
        Initialize a FileParser instance.

        Args:
            file_name (str): Path to the configuration file to parse.
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
        """
        Parse the configuration file and extract all elements.

        Reads the file line by line, validates format, and extracts
        drone count, zones, and connections. Performs duplicate checks
        and metadata validation.

        Returns:
            Dict[str, Any]: Dictionary containing parsed data with keys
                for nb_drones, start_hub, end_hub, hubs, and connections.

        Raises:
            SystemExit: If validation errors are found, displays error
                messages and exits.
        """

        finding = {
            ConfigKeyTypes.NB.value: 0,
            ConfigKeyTypes.START.value: 0,
            ConfigKeyTypes.END.value: 0,
        }
        blocked_lines = defaultdict(int)
        with open(self.file_name, "r") as file:
            lines = file.readlines()

            if not lines:
                display_errors_msg(
                    "File is empty!"
                )

            for num, line in enumerate(lines, start=1):
                connection = {}
                hub = {}
                metadata_dict = {}
                if line[-1] == '\n':
                    line = line[:-1]

                if line.startswith("#"):
                    continue

                if not line.strip():
                    continue

                if ConfigKeyTypes.NB.value in line:
                    is_match = match(r"^nb_drones: [0-9]+$", line)
                    finding[ConfigKeyTypes.NB.value] += 1
                    if finding.get(ConfigKeyTypes.NB.value, 0) > 1:
                        display_errors_msg(
                            f"Line {num}: Duplicate {ConfigKeyTypes.NB.value}"
                        )
                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "The first file must start with the following"
                            " pattern:\n-> nb_drones: <integer>\n"
                            "Please check your input file and try again."
                        )
                    nb_drones = line.split(" ", 1)[1]
                    self.nb_drones = int(nb_drones)
                    if self.nb_drones == 0:
                        display_errors_msg(
                            f"Line: {num}, nb_drones it must be greater then 0"
                        )

                if (ConfigKeyTypes.HUBS.value in line
                        or ConfigKeyTypes.START.value in line
                        or ConfigKeyTypes.END.value in line
                        or "connection" in line):

                    type_hub = ""
                    is_match = None
                    if ConfigKeyTypes.START.value in line:
                        is_match = match(
                            r"^start_hub: (\w+) (-?\d+) (-?\d+)(?:(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.START.value
                        finding[ConfigKeyTypes.START.value] += 1
                        if finding.get(ConfigKeyTypes.START.value, 0) > 1:
                            display_errors_msg(
                                f"Line {num}: Duplicate " +
                                f"{ConfigKeyTypes.START.value}"
                            )
                    elif ConfigKeyTypes.END.value in line:
                        is_match = match(
                            r"^end_hub: (\w+) (-?\d+) (-?\d+)(?:(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.END.value
                        finding[ConfigKeyTypes.END.value] += 1
                        if finding.get(ConfigKeyTypes.END.value, 0) > 1:
                            display_errors_msg(
                                f"Line {num}: Duplicate " +
                                F"{ConfigKeyTypes.END.value}"
                            )
                    elif ConfigKeyTypes.CONN.value in line:
                        is_match = match(
                            r"^connection: (\w+)-(\w+)(?:(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.CONN.value
                    else:
                        is_match = match(
                            r"^hub: (\w+) (-?\d+) (-?\d+)(?:(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.HUBS.value

                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
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
                        metadata = metadata.strip()
                        is_format_metadata = match(
                            r"\[(.*)\]", metadata
                        )

                        if not is_format_metadata:
                            display_errors_msg(
                                f"Line {num}: Invalid {metadata} metadata" +
                                " format!"
                            )

                        if is_format_metadata:
                            metadata_items = (
                                is_format_metadata.group()[1:-1].split(" ")
                            )

                        for meta in metadata_items:
                            if meta:
                                if "=" not in meta or meta.count("=") > 1:
                                    display_errors_msg(
                                        f"Line {num}: Invalid ({meta})"
                                        " metadata format!"
                                    )
                                key, value = meta.split("=", 1)
                                if (type_hub != ConfigKeyTypes.CONN.value
                                        and key not in self.__metadata_zones):
                                    display_errors_msg(
                                        f"Line {num}: Invalid zones's" +
                                        " metadata, " +
                                        f"expected: {self.__metadata_zones}!"
                                    )
                                elif (type_hub == ConfigKeyTypes.CONN.value
                                        and
                                        key not in self.__metadata_connection):
                                    display_errors_msg(
                                        f"Line {num}: Invalid connection's"
                                        " metadata, " +
                                        "expected: " +
                                        f"{self.__metadata_connection}!"
                                    )
                                metadata_dict[key] = value

                        if self.is_duplicate_metadata_key(metadata_items):
                            display_errors_msg(
                                f"Line {num}: Duplicate metadata key!"
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
                            display_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        s_zone_type = metadata_dict.get("zone")
                        if (
                            s_zone_type
                            and s_zone_type == ZoneTypes.BLOCKED.value
                        ):
                            display_errors_msg(
                                f"Line: {num} You can't specific start's zone"
                                f" as type {s_zone_type}, "
                                "Because drones must "
                                "not enter or pass through this zone."
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
                            display_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        e_zone_type = metadata_dict.get("zone")
                        if (
                            e_zone_type
                            and e_zone_type == ZoneTypes.BLOCKED.value
                        ):
                            display_errors_msg(
                                f"Line: {num} You can't specific end's zone as"
                                f" type {e_zone_type}, because Drones must "
                                "not enter or pass through this zone."
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
                            display_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        if (
                            metadata_dict
                            and (
                                metadata_dict.get("zone")
                                == ZoneTypes.BLOCKED.value
                            )
                        ):
                            blocked_lines[name] = num
                        self.hubs.append(hub)
                    elif ConfigKeyTypes.CONN.value in line:
                        connection.update({
                            "name_a": name_a,
                            "name_b": name_b,
                            "metadata": metadata_dict
                        })
                        msg = self.is_duplicate_connection(connection)
                        if msg:
                            display_errors_msg(
                                f"Line {num}: {msg}"
                            )
                        self.connections.append(connection)

                elif ConfigKeyTypes.NB.value not in line:
                    display_errors_msg(
                        f"Line {num}: Unsupported line: {line}"
                    )

            if finding.get(ConfigKeyTypes.NB.value, 0) == 0:
                display_errors_msg(
                    f"{ConfigKeyTypes.NB.value} doesn't exist!"
                )

            if finding.get(ConfigKeyTypes.START.value) == 0:
                display_errors_msg(
                    f"{ConfigKeyTypes.START.value} doesn't exist!"
                )

            if finding.get(ConfigKeyTypes.END.value) == 0:
                display_errors_msg(
                    f"{ConfigKeyTypes.END.value} doesn't exist!"
                )

        for hub in self.hubs:
            metadata = hub.get("metadata", {})
            name = hub.get("name")
            if metadata and metadata.get("zone") == ZoneTypes.BLOCKED.value:
                msg = self.is_duplicate_zone_coordinates(hub)
                if msg:
                    display_errors_msg(
                        f"Line {blocked_lines[name]}: {msg}"
                    )

        return {
            ConfigKeyTypes.NB.value: self.nb_drones,
            ConfigKeyTypes.START.value: self.start_zone,
            ConfigKeyTypes.END.value: self.end_zone,
            ConfigKeyTypes.HUBS.value: self.hubs,
            ConfigKeyTypes.CONN.value: self.connections
        }

    def is_duplicate_zone(self, hub: Dict[str, Any]) -> bool | str:
        """
        Check if a zone is a duplicate based on name or coordinates.

        Args:
            hub (Dict[str, Any]): Zone data to check.

        Returns:
            bool | str: False if no duplicate,
                error message string if duplicate.
        """

        if self.start_zone:
            if self.start_zone.get("name") == hub.get("name"):
                return (
                    f"Duplicate \"{hub.get('name')}\" name!"
                )
        if self.end_zone:
            if self.end_zone.get("name") == hub.get("name"):
                return (
                    f"Duplicate \"{hub.get('name')}\" name!"
                )
        for zone in self.hubs:
            if zone.get("name") == hub.get("name"):
                return f"Duplicate \"{hub.get('name')}\" name!"
        return False

    def is_duplicate_metadata_key(self, metadata: List[str]) -> bool:
        """
        Check if metadata contains duplicate keys.

        Args:
            metadata (List[str]): List of metadata key-value pairs.

        Returns:
            bool: True if duplicates found, False otherwise.
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
        """
        Check if a connection is duplicate or references non-existent zones.

        Args:
            connection (Dict[str, Any]): Connection data to check.

        Returns:
            bool | str: False if valid, error message string if invalid.
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
        """
        Check if a zone with the given name exists.

        Args:
            name (str): Name of the zone to check.

        Returns:
            bool: True if zone exists, False otherwise.
        """
        if self.start_zone.get("name") == name:
            return True
        elif self.end_zone.get("name") == name:
            return True

        for zone in self.hubs:
            if zone.get("name") == name:
                return True

        return False

    def is_duplicate_zone_coordinates(self, hub: Dict[str, Any]) -> bool | str:
        """
        Check if a zone has duplicate coordinates with existing zones.

        Args:
            hub (Dict[str, Any]): Zone data to check.
        Returns:
            bool | str: False if no duplicate coordinates,
                error message string if duplicate coordinates found.
        """
        for zone in self.hubs:
            if zone is hub:
                continue
            if (zone.get("x") == hub.get("x")
                    and zone.get("y") == hub.get("y")):
                return (
                    "Blocked zone hasn't unique coordinates(x, y)"
                )
            if (
                self.start_zone and
                (
                    self.start_zone.get("x") == hub.get("x")
                    and self.start_zone.get("y") == hub.get("y")
                )
            ):
                return (
                    "Blocked zone hasn't unique coordinates(x, y)"
                )

            if (
                self.end_zone and
                (
                    self.end_zone.get("x") == hub.get("x")
                    and self.end_zone.get("y") == hub.get("y")
                )
            ):
                return (
                    "Blocked zone hasn't unique coordinates(x, y)"
                )

        return False
