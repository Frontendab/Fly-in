from viz import start_visualization
from models import Graph, PydanticError
from pydantic import ValidationError


if __name__ == "__main__":
    print("Hello world, I am Fly-in :)")

    graph = Graph()

    graph.create_zone(
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

    print()
    # for zone in graph.zones.values():
    #     print(f"Name: {zone.name}")
    #     print(f"x: {zone.x}, y: {zone.y}")
    #     print(f"color: {zone.color}")
    #     print(f"zone_type: {zone.zone_type}")
    #     print(f"max_drones: {zone.max_drones}")
    #     print(f"current_drones: {zone.current_drones}")
    #     print()

    list_connection = [
        {
            "zones": {
                "zone_a": graph.zones.get("start"),
                "zone_b": graph.zones.get("waypoint1")
            },
            "max_link_capacity": 4,
        },
        {
            "zones": {
                "zone_a": graph.zones.get("waypoint1"),
                "zone_b": graph.zones.get("waypoint2")
            },
            "max_link_capacity": -2,
        },
        {
            "zones": {
                "zone_a": graph.zones.get("waypoint2"),
                "zone_b": graph.zones.get("goal")
            },
            "max_link_capacity": -3,
        },
    ]

    # TODO: I have to fix the data to store zone_a, zone_band max_link_capacity
    try:
        for item in list_connection:
            data = {}
            keys = item.keys()

            for key in keys:
                if key == "zones":
                    data.update({
                        "zone_a": item.get(key).get("zone_a"),
                        "zone_b": item.get(key).get("zone_b")
                    })
                if key == "max_link_capacity":
                    data.update({
                        "max_link_capacity": item.get(key)
                    })

                connection = graph.create_connection(**data)

                connection.initialize_connect()

        for key, value in graph.connections.items():
            print(
                f"Connection: {key}, target: {value.zone_a.target_zone.name}" +
                f", x: {value.zone_a.target_zone.x}, y: {value.zone_a.target_zone.y}"
            )
            print(f"max_link_capacity: {value.max_link_capacity}, current_flow: {value.current_flow}")

            print()

    except ValidationError as e:
        error = PydanticError(e.errors())
        format_errors = error.format_errors()
        error.display_errors(format_errors)

    start_visualization()
