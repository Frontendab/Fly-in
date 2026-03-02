from typing import List, Dict, Any
from re import match
from enum import Enum


class ConfigKeyTypes(Enum):
    NB = "nb_drones:"
    START = "start_hub:"
    END = "end_hub:"
    HUBS = "hub:"
    CONN = "connection:"


class FileParser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_zone: Dict[str, Any] = {}
        self.end_zone: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.__metadata_zones = ("color", "zone", "max_drones")
        self.__metadata_connection = ("max_link_capacity")

    def parse(self) -> Dict[str, Any]:
        from utils import display_errors_msg

        finding = {
            ConfigKeyTypes.NB.value: 0,
            ConfigKeyTypes.START.value: 0,
            ConfigKeyTypes.END.value: 0,
        }
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
                line = line[:-1]

                if line.startswith("#"):
                    continue

                if not line.strip():
                    continue

                if ConfigKeyTypes.NB.value in line:
                    is_match = match(r"^nb_drones: [0-9]+$", line)
                    finding[ConfigKeyTypes.NB.value] += 1
                    if finding.get(ConfigKeyTypes.NB.value) > 1:
                        display_errors_msg(
                            f"Line {num}: Duplicate {ConfigKeyTypes.NB.value}"
                        )
                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "The first file must start with the following"
                            " pattern:\n-> nb_drones: <number>\n"
                            "Please check your input file and try again."
                        )
                    nb_drones = line.split(" ", 1)[1]
                    self.nb_drones = int(nb_drones)
                elif finding.get(ConfigKeyTypes.NB.value, 0) > 1:
                    display_errors_msg(
                        f"Line {num}: Duplicate {ConfigKeyTypes.NB.value}"
                    )
                elif finding.get(ConfigKeyTypes.NB.value, 0) == 0:
                    display_errors_msg(
                        f"Line {num}: Drones number must be defined in " +
                        f"the first line\n-> {ConfigKeyTypes.NB.value}" +
                        " <number>"
                    )

                if (ConfigKeyTypes.HUBS.value in line
                        or ConfigKeyTypes.START.value in line
                        or ConfigKeyTypes.END.value in line
                        or "connection" in line):

                    type_hub = ""
                    is_match = None
                    if ConfigKeyTypes.START.value in line:
                        is_match = match(
                            r"^start_hub: (\w+) (-?\d+) (-?\d+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.START.value
                        finding[ConfigKeyTypes.START.value] += 1
                    elif ConfigKeyTypes.END.value in line:
                        is_match = match(
                            r"^end_hub: (\w+) (-?\d+) (-?\d+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.END.value
                        finding[ConfigKeyTypes.END.value] += 1
                    elif ConfigKeyTypes.CONN.value in line:
                        is_match = match(
                            r"^connection: (\w+)-(\w+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.CONN.value
                        finding[ConfigKeyTypes.CONN.value] += 1
                    else:
                        is_match = match(
                            r"^hub: (\w+) (-?\d+) (-?\d+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = ConfigKeyTypes.HUBS.value
                        finding[ConfigKeyTypes.HUBS.value] += 1

                    if finding.get(ConfigKeyTypes.START.value) > 1:
                        display_errors_msg(
                            f"Line {num}: Duplicate start hub!"
                        )
                    elif finding.get(ConfigKeyTypes.START.value) == 0:
                        display_errors_msg(
                            f"Line {num}: Start hub doesn't exist!"
                        )
                    elif finding.get(ConfigKeyTypes.END.value) > 1:
                        display_errors_msg(
                            f"Line {num}: Duplicate end hub!"
                        )
                    elif finding.get(ConfigKeyTypes.END.value) == 0:
                        display_errors_msg(
                            f"Line {num}: End hub doesn't exist!"
                        )

                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "it must be following this pattern\n"
                            f"-> {type_hub}: <name> <number> <number> [color=green]\n"
                            "Metadata is optional, Please check your "
                            "input file and try again."
                        )

                    if type_hub != ConfigKeyTypes.CONN.value:
                        name, x, y, metadata = is_match.groups()
                    elif type_hub == ConfigKeyTypes.CONN.value:
                        name_a, name_b, metadata = is_match.groups()

                    if metadata:
                        is_format_metadata = match(
                            r"\[(.*)\]", metadata
                        )

                        if not is_format_metadata:
                            display_errors_msg(
                                f"Line {num}: Invalid {metadata} metadata" +
                                " format!"
                            )

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

        return {
            ConfigKeyTypes.NB.value: self.nb_drones,
            ConfigKeyTypes.START.value: self.start_zone,
            ConfigKeyTypes.END.value: self.end_zone,
            ConfigKeyTypes.HUBS.value: self.hubs,
            ConfigKeyTypes.CONN.value: self.connections
        }

    def is_duplicate_zone(self, hub: Dict[str, Any]) -> bool | str:

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

    def is_exist_zone(self, name: str) -> bool:
        if self.start_zone.get("name") == name:
            return True
        elif self.end_zone.get("name") == name:
            return True

        for zone in self.hubs:
            if zone.get("name") == name:
                return True

        return False
