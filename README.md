# Fly-in

### Format list of connection:
```json
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
            "max_link_capacity": 2,
        },
        {
            "zones": {
                "zone_a": graph.zones.get("waypoint2"),
                "zone_b": graph.zones.get("goal")
            },
            "max_link_capacity": 3,
        },
    ]
```