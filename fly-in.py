from viz import start_visualization
from models import Graph


if __name__ == "__main__":
    print("Hello world, I am Fly-in :)")

    graph = Graph()

    graph.create_zone(
        name="start", x=0, y=0, color="green",
    )

    print(graph.zones)

    start_visualization()
