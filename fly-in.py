from viz import start_visualization
from models import Graph, PydanticError
from pydantic import ValidationError


if __name__ == "__main__":
    print("Hello world, I am Fly-in :)")

    graph = Graph()

    try:
        zone = graph.create_zone(
            name="start", x=0, y=0, color="green",
        )

        graph.create_zone(
            name="waypoint1", x=1, y=0, color="blue",
        )

        graph.create_zone(
            name="waypoint2", x=2, y=0, color="blue",
        )

        graph.create_zone(
            name="goal", x=3, y=0, color="red",
        )

    except ValidationError as e:
        error = PydanticError(e.errors())
        format_errors = error.format_errors()
        error.display_errors(format_errors)

    start_visualization()
