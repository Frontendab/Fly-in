from typing import List, Dict, Any
from sys import stderr, exit
from re import match
from utils import display_errors_msg


class FileParser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_zone: Dict[str, Any] = None
        self.end_zone: Dict[str, Any] = None
        self.hubs: List[Dict[str, Any]] = None
        self.connections: List[Dict[str, Any]] = None

    def parse(self) -> Dict[str, Any]:
        finding = {
            "nb_drones": False,
        }
        response = {}
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
                    response["nb_drones"] = int(nb_drones)
                elif not finding.get("nb_drones", False):
                    display_errors_msg(
                        f"Line {num}: Drones number must be defined in " +
                        "the first line\n-> nb_drones: <number>"
                    )

                if "start_hub" in line:
                    is_match = match(
                        r"^start_hub: [A-Za-z]+ [0-9]+ [0-9]+(?:\s+\[(.*)\])?",
                        line
                    )

                    # TODO: I have to complete parsing start_ hub

                    print(is_match)

                    if not is_match:
                        display_errors_msg(
                            f"Line {num}: Invalid File Format\n"
                            "it must be following this pattern\n"
                            "-> start_hub: start 0 0 [color=green]\n"
                            "Metadata is optional, Please check your "
                            "input file and try again."
                        )

        return response
