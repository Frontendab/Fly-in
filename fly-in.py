from viz import start_visualization
from models import Graph, PydanticError, FileParser
from pydantic import ValidationError
import sys


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
    if data:
        print(data)

    start_visualization()
