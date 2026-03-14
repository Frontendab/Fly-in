from viz import VisualizeSimulation
from models import Graph, PydanticError, FileParser
from pydantic import ValidationError
import sys
from utils import initialize_graph


# TODO: I have to hide pygame support
# TODO: I have to improve caching errors
# TODO: I have to add docstring for all methods, classes, functions


if __name__ == "__main__":
    argv = sys.argv

    if len(argv) != 2:
        print(
            "[ERROR]: Missing a filename!",
            file=sys.stderr
        )
        sys.exit(1)

    file_name = argv[1]

    file_parser = FileParser(file_name)

    data = file_parser.parse()

    graph = Graph()

    try:
        initialize_graph(data, graph)
    except ValidationError as e:
        error = PydanticError(e.errors())
        format_result = error.format_errors()
        error.display_errors(format_result)

    visualize = VisualizeSimulation()
    visualize.initialize_visualization(graph)
    visualize.run(graph)
