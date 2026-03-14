from models import Graph, ConfigKeyTypes, ZoneTypes
from typing import Dict, Any


def initialize_graph(data: Dict[str, Any], graph: Graph) -> None:

    # TODO: I have to improve this function

    start = data.get(ConfigKeyTypes.START.value)
    if start:
        metadata = start.get("metadata")
        zone_type = metadata.get("zone", ZoneTypes.NORMAL.value)
        max_drones = metadata.get("max_drones", 1)
        color = metadata.get("color", None)

        graph.start_zone = graph.create_zone(
            start.get("name"), start.get("x"), start.get("y"), zone_type,
            max_drones, color
        )

    end = data.get(ConfigKeyTypes.END.value)

    if end:
        metadata = end.get("metadata", None)
        zone_type = metadata.get("zone", ZoneTypes.NORMAL.value)
        max_drones = metadata.get("max_drones", 1)
        color = metadata.get("color", None)

        graph.end_zone = graph.create_zone(
            end.get("name"), end.get("x"), end.get("y"), zone_type,
            max_drones, color
        )

    hubs_list = data.get(ConfigKeyTypes.HUBS.value, None)
    if hubs_list:
        for zone in hubs_list:
            metadata = zone.get("metadata")
            zone_type = metadata.get("zone", ZoneTypes.NORMAL.value)
            max_drones = metadata.get("max_drones", 1)
            color = metadata.get("color", None)

            new_zone = graph.create_zone(
                zone.get("name"), zone.get("x"), zone.get("y"), zone_type,
                max_drones, color
            )
            graph.zones.update({
                new_zone.name: new_zone
            })

    conn_list = data.get(ConfigKeyTypes.CONN.value, None)
    if conn_list:
        for conn in conn_list:

            metadata = data.get("metadata", None)
            max_link_capacity = 1
            if metadata:
                max_link_capacity = metadata.get("max_link_capacity", 1)

            name_a = graph.get_zone(conn.get("name_a"))
            name_b = graph.get_zone(conn.get("name_b"))
            if name_a and name_b:
                new_conn = graph.create_connection(
                    name_a, name_b, max_link_capacity
                )
                new_conn.initialize_connect()
                key_format = f"{new_conn.zone_a.name}-{new_conn.zone_b.name}"
                graph.connections.update({
                    key_format: new_conn
                })

    nb_drones = data.get(ConfigKeyTypes.NB.value, 0)

    for idx in range(1, nb_drones + 1):
        drone = graph.create_drone(
            (idx),
            graph.start_zone,
            graph.start_zone.target_zone
        )
        graph.drones.update({
            drone.id: drone
        })
