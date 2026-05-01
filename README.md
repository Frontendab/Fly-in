*This project has been created as part of the 42 curriculum by asadouri.*

# Fly-in: Multi-Drone Pathfinding & Simulation

## Description

**Fly-in** is a multi-agent pathfinding simulation designed to coordinate a fleet of drones through a complex network of zones and connections. The primary goal is to move all drones from a designated `start_hub` to an `end_hub` in the minimum number of turns possible while strictly adhering to physical constraints such as zone capacities, link capacities, and varying terrain types (Restricted, Priority, etc.).

This project tackles the **Cooperative Pathfinding** problem, ensuring that drones do not collide or exceed the structural limits of the graph, utilizing a time-expanded search space.

## Features

  - **Space-Time A* Algorithm*\*: Navigates drones through both physical space and discrete time intervals.
  - **Capacity Management**: Real-time tracking of `max_drones` per zone and `max_link_capacity` per connection.
  - **Diverse Terrain Support**:
      - `RESTRICTED`: Movements take 2 turns.
      - `PRIORITY`: Favored by the algorithm to optimize flow.
      - `BLOCKED`: Non-traversable nodes.
  - **Strategic Waiting**: Drones can choose to stay in their current zone to wait for a path to clear.
  - **High-Performance Visualizer**: A Pygame-based GUI that renders movement with smooth interpolation and real-time state feedback.

## Instructions

### Prerequisites

  - Python 3.10 or higher.
  - `pip` (Python package installer).

### Installation

The project includes a `Makefile` to automate the setup of the Virtual Environment (`venv`):

```bash
# Clone the repository
git clone <your-repo-link>
cd fly-in

# Install dependencies and set up venv
make install
```

### Execution

To run the simulation with a specific map:

```bash
make run FILE_NAME_MAP=<path>
```

## Algorithm & Implementation Strategy

The `PathFinder` class implements a turn-based cooperative pathfinding algorithm with explicit capacity reservation and restricted-zone transit handling.

### 1\. Pre-computation

The algorithm begins with Dijkstra search from the `end_hub`.

- **Distance map**: All zone distances are initialized to infinity, except `end_hub` which is set to 0.
- **Reverse expansion**: The search explores neighbors through the reverse adjacency list (`target_zone_from_end`). Blocked zones are skipped.
- **Terrain cost**: Movement cost is based on zone type: normal and priority zones cost `1`, restricted zones cost `2`. Priority zones receive a heuristic bias by subtracting `0.5` from their cost, encouraging route selection through them.
- **Result**: The computed distance map is stored in `self.shortest_dist` and used during move selection.

### 2\. Turn Order and Drone Evaluation

Drones are processed in a deterministic order each turn.

- **Sorting**: The implementation attempts to sort drones with the heuristic map. Since the pathfinder looks up distances using name's drone current_zone, the order remains stable and reproducible.
- **Effect**: Stable ordering avoids nondeterministic move conflicts when several drones compete for the same connection.

### 3\. Per-turn Move Selection

The algorithm runs a discrete turn loop until every drone reaches the goal.

- **Occupancy counters**: Each turn resets `z_next_count` for destination zone occupancy and `edge_usage` for connection usage.
- **Neighbor evaluation**: For every unfinished drone, the algorithm considers outgoing neighbors and applies the following checks:
  - Blocked zones are ignored.
  - Connections must exist and have remaining capacity.
  - Destination zone capacity is enforced (except for the end zone).
  - The neighbor with the lowest heuristic distance is chosen.

### 4\. Restricted Zone Transit

Restricted zones require two turns to traverse. The algorithm handles this explicitly.

- **Transit tracking**: When a drone enters a restricted neighbor, it is placed in `in_transit` with one remaining turn and the connection name.
- **Connection reservation**: The connection remains occupied for both turns of the restricted movement.
- **Arrival update**: On the following turn, the drone completes the move, enters the restricted zone, and the zone occupancy counter is updated.
- **Path recording**: While in transit, the drone path records the connection identifier. Upon arrival, the zone name is appended.

### 5\. Waiting and Move Application

If no valid move exists, the drone waits in place.

- **Wait handling**: Drones that cannot move due to blocked connections or capacity limits remain in their current zone.
- **Batch apply**: All moves are committed together, updating current zones and drone paths.
- **Finish condition**: Drones are marked finished when they arrive at the `end_hub`, and the loop continues until all drones finish.

### 6\. Output Generation

The output printer converts the recorded paths into turn-by-turn move lines.

### Algorithm Choices and Rationale

This section explains why specific algorithms and strategies were chosen for the Fly-in system.

#### Space-Time A* Algorithm
Space-Time A* was selected as the core algorithm because it handles multi-agent pathfinding by expanding the search space to include time, preventing collisions and respecting capacities. Unlike single-agent A*, it ensures conflict-free paths in dynamic environments where graph states change per turn.

#### Dijkstra's Algorithm for Pre-computation
Dijkstra pre-computes shortest distances from the end hub for an admissible heuristic. It's chosen for non-negative weights and single-source shortest paths, reducing search space compared to no heuristic.

## Design decision


### Precomputing Distances (Dijkstra)
Before any drones move, the `__precompute_distances` method runs a Dijkstra search starting from the **end zone** and working backward.

* **The Heuristic**: It calculates the exact minimum cost to reach the goal from every zone.

* **Priority Influence**: It subtracts $0.5$ from the movement cost for PRIORITY zones. This "tricks" the drones into thinking priority zones are physically closer, encouraging them to prefer those routes.

### Real-Time Simulation (A*)

The `a_star_search` doesn't just calculate one path; it simulates the world turn-by-turn.

* **Greedy Selection**: In each turn, drones look at their neighbors and pick the one with the lowest precomputed distance.

* **Wait Logic**: If all neighbors are blocked or at capacity, the drone stays in its current zone (a "wait" action), which is a common strategy in multi-agent pathfinding to resolve deadlocks.


## Visualization

The visual representation is built using **Pygame** to enhance the debugging and user experience:

### Visual Representation Features

#### Smooth Interpolation
Drones move smoothly between zones using interpolation over the `turn_delay` period, rather than instantaneous jumps. This feature enhances user experience by providing a realistic and fluid animation that allows users to visually track drone movements, making it easier to understand traffic flow and identify potential bottlenecks or delays in the simulation.

#### Visual Feedback for Zones and Drones
- **Zone Differentiation**: Zones are represented with distinct icons and colors (e.g., green for start, red for end, yellow for junctions, blue for paths). Restricted zones may have warning indicators, priority zones highlighted for preference, and blocked zones visually obstructed.
- **Drone States**: Drones display dynamic rotor rotation speeds—fast when actively moving to indicate progress, slow when waiting to highlight idle time. This visual cue helps users quickly assess simulation efficiency and spot drones stuck in conflicts.

#### Collision and Capacity Visualization
An offset system positions multiple drones in the same zone slightly apart, preventing visual overlap. This allows users to see capacity utilization at a glance, enhancing understanding of how drones share space and respect limits, which is crucial for debugging capacity-related issues and optimizing pathfinding strategies.

These features collectively improve user experience by transforming abstract data into an intuitive, interactive display that facilitates debugging, learning, and enjoyment of the multi-drone simulation.

## Usage Example

### Input Map

Consider the following simple map file (`maps/easy/01_linear_path.txt`):

```
# Easy Level 2: Simple fork with two paths
nb_drones: 3

start_hub: start 0 0 [color=green]
hub: junction 1 0 [color=yellow max_drones=2]
hub: path_a 2 1 [color=blue]
hub: path_b 2 -1 [color=blue]
end_hub: goal 3 0 [color=red max_drones=3]

connection: start-junction [max_link_capacity=2]
connection: junction-path_a
connection: junction-path_b
connection: path_a-goal
connection: path_b-goal
```

### Expected Output

The program will output the sequence of moves for each turn:

```
D1-junction D2-junction
D1-path_a D2-path_b D3-junction
D1-goal D2-goal D3-path_a
D3-goal
```

### Explanation

This output is generated by the algorithm as follows:

- **Pre-computation**: Distances are calculated from the end zone ("goal") using reverse Dijkstra. The distances are: "goal"=0, "path_a"=1, "path_b"=1, "junction"=2, "start"=3.

- **Turn 1**: All drones start at "start". Drones are sorted by their current zone's distance (all have distance 3, so by ID: D1, D2, D3). The "junction" zone has a capacity of 2 drones. D1 and D2 move to "junction" (using the connection with capacity 2). D3 cannot move due to capacity limits and waits at "start".

- **Turn 2**: D1 (at "junction") moves to "path_a", D2 moves to "path_b". D3 moves to "junction" (now available).

- **Turn 3**: D1 moves to "goal", D2 moves to "goal". D3 moves to "path_a".

- **Turn 4**: D3 moves to "goal".

The algorithm ensures no capacity violations and prioritizes moves based on heuristic distances to the goal.

## Resources

  - [**A * Search Algorithm**](https://www.geeksforgeeks.org/dsa/a-search-algorithm/)
  - [**A * Visualization**](https://algorithms.discrete.ma.tum.de/graph-algorithms/spp-a-star/index_en.html)
  - [**Pygame Tuturial**](https://www.geeksforgeeks.org/python/pygame-tutorial/)
  - [**Python RegEx**](https://www.w3schools.com/python/python_regex.asp)

### AI Usage Disclosure

Artificial Intelligence (specifically Large Language Models) was used **solely for understanding, explanation, and writing the `README.md`** during this project. Its contributions included:
  - **Optimization**: Helping to understand how to improve the turn count in the "Challenger" map.
  - **Refactoring**: Assisting in the creation of clean, Pythonic docstrings and type hinting for the `PathFinder` class, primarily for explanatory purposes.
  - **Visualizer Logic**: Aiding in understanding and implementing the linear interpolation math used in the Pygame `__move_drones` logic.
  - **Documentation**: Generating initial drafts for the README and technical explanations.