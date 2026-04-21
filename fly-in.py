from pathFinder import PathFinder
from visualization import VisualizeSimulation
from classes import Graph, PydanticError
from parsing import FileParser, display_errors_msg
from pydantic import ValidationError
from sys import argv, stderr, exit
from initialize import initialize_graph
from typing import Dict, Any


def main() -> None:

    if len(argv) != 2:
        print(
            "[WARNING]: Usage (make run MAP=path)",
            file=stderr
        )
        exit(1)

    file_name: str = argv[1]

    data: Dict[str, Any] | None = None
    try:
        file_parser: FileParser = FileParser(file_name)

        data = file_parser.parse()
    except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
        display_errors_msg(str(e))

    if not data:
        return

    graph: Graph = Graph()

    try:
        initialize_graph(data, graph)
    except ValidationError as e:
        error = PydanticError(e.errors())
        format_result = error.format_errors()
        error.display_errors(format_result)

    try:
        pathfinder = PathFinder(graph)
        pathfinder.a_star_search()
        pathfinder.generate_output()
    except ValueError as e:
        display_errors_msg(str(e))

    try:
        visualize: VisualizeSimulation = VisualizeSimulation()
        visualize.initialize_visualization(graph)
        visualize.run(graph)
    except KeyboardInterrupt:
        display_errors_msg("Exit the program")


if __name__ == "__main__":
    main()
