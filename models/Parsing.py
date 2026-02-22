from typing import List, Dict, Any
from re import match
from utils import display_errors_msg


class FileParser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_zone: Dict[str, Any] = {}
        self.end_zone: Dict[str, Any] = {}
        self.hubs: List[Dict[str, Any]] = []
        self.connections: List[Dict[str, Any]] = []
        self.__metadata_zones = ("color", "zone", "max_drones")

    def parse(self) -> Dict[str, Any]:
        finding = {
            "nb_drones": False,
        }
        with open(self.file_name, "r") as file:
            lines = file.readlines()

            if not lines:
                display_errors_msg(
                    "File is empty!"
                )

            for num, line in enumerate(lines, start=1):
                line = line[:-1]

                if line.startswith("#"):
                    continue

                if not line.strip():
                    continue

                if "nb_drones" in line:
                    is_match = match(r"^nb_drones: [0-9]+$", line)
                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "The first file must start with the following"
                            " pattern:\n-> nb_drones: <number>\n"
                            "Please check your input file and try again."
                        )
                    finding["nb_drones"] = True
                    nb_drones = line.split(" ", 1)[1]
                    self.nb_drones = int(nb_drones)
                elif not finding.get("nb_drones", False):
                    display_errors_msg(
                        f"Line {num}: Drones number must be defined in " +
                        "the first line\n-> nb_drones: <number>"
                    )

                if ("hub" in line or "start_hub" in line or "end_hub" in line
                        or "connection" in line):

                    type_hub = "hub"
                    is_match = match(
                        r"^hub: (\w+) (\d+) (\d+)(?:\s+(.*))?",
                        line
                    )
                    if "start_hub" in line:
                        is_match = match(
                            r"^start_hub: (\w+) (\d+) (\d+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = "start_hub"
                    elif "end_hub" in line:
                        is_match = match(
                            r"^end_hub: (\w+) (\d+) (\d+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = "end_hub"

                    elif "connection" in line:
                        is_match = match(
                            r"^connection: (\w+)-(\w+)(?:\s+(.*))?",
                            line
                        )
                        type_hub = "connection"

                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "it must be following this pattern\n"
                            f"-> {type_hub}: start 0 0 [color=green]\n"
                            "Metadata is optional, Please check your "
                            "input file and try again."
                        )

                    if type_hub != "connection":
                        _, _, _, metadata = is_match.groups()
                    elif type_hub == "connection":
                        name_a, name_b, metadata = is_match.groups()

                    # TODO: I have to append the hubs and connections to self

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
                                if key not in self.__metadata_zones:
                                    display_errors_msg(
                                        f"Line {num}: Invalid zones's" +
                                        " metadata, " +
                                        f"expected: {self.__metadata_zones}!"
                                    )

                        if "start_hub" in line:
                            self.start_zone.update({
                                "metadata": metadata_items
                            })
                        elif "end_hub" in line:
                            self.end_zone.update({
                                "metadata": metadata_items
                            })

                    if "start_hub" in line:
                        name, x, y, _ = is_match.groups()
                        self.start_zone.update({
                            "name": name,
                            "x": int(x),
                            "y": int(y),
                        })
                    elif "end_hub" in line:
                        name, x, y, _ = is_match.groups()
                        self.end_zone.update({
                            "name": name,
                            "x": int(x),
                            "y": int(y),
                        })
                    elif "connection" in line:
                        print(name_a, name_b, metadata)

                elif "nb_drones" not in line:
                    display_errors_msg(
                        f"Line {num}: Unsupported line: {line}"
                    )

        return {
            "nb_drones": self.nb_drones,
            "start_zone": self.start_zone,
            "end_zone": self.end_zone,
            "hubs": self.hubs,
            "connections": self.connections
        }
