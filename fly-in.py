from viz import start_visualization
from models import Graph, PydanticError, FileParser
from pydantic import ValidationError
import sys
from utils import initialize_graph


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

    initialize_graph(data, graph)

    # TODO: I have to start draw the zones with edges in the pygame hh

    start_visualization()
