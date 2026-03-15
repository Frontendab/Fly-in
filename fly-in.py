from viz import VisualizeSimulation
from models import Graph, PydanticError, FileParser
from pydantic import ValidationError
from sys import exit, stderr, argv
from utils import initialize_graph, display_errors_msg


# TODO: I have to add docstring for all methods, classes, functions
# TODO: I have to test all maps with config.txt file
# TODO: I have to verify max_link_capacity
# TODO: I have to write README.MD file


def main() -> None:
    if len(argv) != 2:
        print(
            "[ERROR]: Missing a filename!",
            file=stderr
        )
        exit(1)

    file_name = argv[1]

    data = None

    try:
        file_parser = FileParser(file_name)

        data = file_parser.parse()
    except (
        PermissionError, FileNotFoundError,
        TypeError, ValueError
    ) as e:
        display_errors_msg(e)

    graph = Graph()

    try:
        initialize_graph(data, graph)
    except ValidationError as e:
        error = PydanticError(e.errors())
        format_result = error.structure_errors()
        error.display_errors(format_result)

    visualize = VisualizeSimulation()
    visualize.initialize_visualization(graph)
    visualize.run(graph)


if __name__ == "__main__":
    main()
