from classes import Zone, ZoneTypes, Graph, Drone
from typing import Dict, Tuple, Match, Any
from enum import Enum
from re import search

from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame # noqa
from pygame.colordict import THECOLORS # noqa


class SizeImages(Enum):
    """
    Enumeration for image size options.

    Defines available sizes for visual elements.
    """
    BIG = "big"
    SMALL = "small"


class NameImages(Enum):
    """
    Enumeration for image type names.

    Defines the types of images used in visualization.
    """
    HUB = "hub"
    DRONE = "drone"
    SPACING = "spacing"
    ZONE_TYPES = "zone_types"


class VisualizeSimulation:
    """
    Main class for visualizing the Fly-in drone simulation.

    Handles Pygame initialization, rendering of zones and connections,
    and animated movement of drones through the graph.
    """

    def __init__(self) -> None:
        """
        Initialize the visualization simulation.

        Sets up Pygame, screen dimensions, image paths, and default parameters
        for rendering the simulation.
        """
        pygame.init()
        self.pygame_info = pygame.display.Info()
        self.w_width = self.pygame_info.current_w * 0.8
        self.w_height = self.pygame_info.current_h * 0.8
        self.image_path = "bg.png"
        self.image_path_hub = "hub.png"
        self.image_path_priority = "priority.png"
        self.image_path_restricted = "restricted.png"
        self.image_path_blocked = "blocked.png"
        self.image_path_drone = "drone.png"
        self.drone_img: pygame.Surface = pygame.Surface((0, 0))
        self.load_rainbow_image: pygame.Surface = pygame.Surface((0, 0))
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.dynamic_scale: float = 0.0
        self.start_x: float = 0.0
        self.start_y: float = 0.0
        self.surface_width = self.w_width * 0.9
        self.surface_height = self.w_height * 0.9
        self.radius = 80
        self.spacing = 100
        self.hub_w_h = (30, 80)
        self.list_zones: Dict[str, Zone] = {}
        self.line: Dict[str, Any] = {
            "color": THECOLORS.get("lightskyblue"),
            "border": 5
        }
        self.size_type_zones = (25, 25)
        self.angle = 0
        self.clock = pygame.time.Clock()
        self.space_drones: Dict[str, pygame.Surface] = {}
        self.plus_zone_types = (10, 105)
        self.plus_drone_types = (15, 40)
        self.current_sim_turns = 0
        self.frames_per_turn = 60
        self.frame_counter = 0

        self.turn_delay_ms = 1500
        self.last_turn_update_time = pygame.time.get_ticks()

    def run(self, graph: Graph) -> None:
        """
        Run the main visualization loop.

        Initializes the display, draws static elements, computes paths,
        and runs the animation loop for drone movements.

        Args:
            graph (Graph): The graph containing zones, connections, and drones.
        """
        pygame.display.set_caption("Fly-in")
        screen = pygame.display.set_mode(
            (self.w_width, self.w_height)
        )

        self.load_rainbow_image = pygame.image.load(
            "rainbow.png"
        ).convert_alpha()

        self.drone_img = pygame.image.load(
            self.image_path_drone
        ).convert_alpha()

        load_original_bg = pygame.image.load(self.image_path).convert()

        canvas = pygame.transform.smoothscale(
            load_original_bg, (self.w_width, self.w_height)
        )

        # Load the font with size
        font = pygame.font.SysFont("Arial", 24)

        base_canvas = canvas.copy()
        self.__draw_edges(base_canvas, graph)
        self.__draw_zones(base_canvas)
        self.__draw_type_zone(base_canvas)

        self.__initialize_drone_start(graph)

        running = True
        while running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            screen.blit(base_canvas, (0, 0))

            self.angle = (self.angle + 10) % 360

            self.__draw_drones(graph)

            self.__move_drones(screen, graph)

            turn_text = font.render(
                f"Simulation Turn: {self.current_sim_turns}", True,
                (255, 255, 255)
            )
            screen.blit(turn_text, (20, 20))

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def __draw_edges(self, canvas: pygame.Surface, graph: Graph) -> None:
        """
        Draw connection edges between zones on the canvas.

        Args:
            canvas (pygame.Surface): The surface to draw on.
            graph (Graph): The graph containing zones and connections.
        """
        list_zones = {key: value for key, value in graph.zones.items()}
        list_zones.update({
            graph.start_zone.name: graph.start_zone,
            graph.end_zone.name: graph.end_zone
        })
        self.list_zones = list_zones

        for zone in list_zones.values():

            if zone.target_zone:
                for target in zone.target_zone:

                    pygame.draw.line(
                        canvas,
                        self.line.get("color", (225, 225, 225, 225)),
                        self.get_render_coords(
                            zone.x, zone.y
                        ),
                        self.get_render_coords(
                            target.x, target.y
                        ),
                        self.line.get("border", 3)
                    )

    def __draw_zones(self, canvas: pygame.Surface) -> None:
        """
        Draw zone hubs on the canvas with colorization.

        Args:
            canvas (pygame.Surface): The surface to draw on.
            graph (Graph): The graph containing zones.
        """

        load_hub_image = pygame.image.load(self.image_path_hub)

        for zone in self.list_zones.values():

            color = (
                zone.color if zone.color else THECOLORS.get("white")
            )

            if zone.color_name != "rainbow" and color:
                if isinstance(color, tuple):
                    a, b, c, d = color
                    new_a = int(a * 0.6 + 255 * 0.3)
                    new_b = int(b * 0.6 + 255 * 0.3)
                    new_c = int(c * 0.6 + 255 * 0.3)

                    new_load = self.colorize(
                        load_hub_image.convert_alpha(),
                        (new_a, new_b, new_c, d)
                    )

                hub_image = pygame.transform.scale(
                    new_load,
                    self.hub_w_h
                )
                current_pos = self.__get_pos(
                    zone.x, zone.y
                )
            else:
                hub_image = pygame.transform.scale(
                    self.load_rainbow_image,
                    (170, 100)
                )
                current_pos = self.__get_pos(
                    zone.x, zone.y
                )
                current_pos = (
                    current_pos[0] - 45,
                    current_pos[1]
                )

            canvas.blit(hub_image, current_pos)

    def __draw_type_zone(self, canvas: pygame.Surface) -> None:
        """
        Draw zone type indicators (priority, restricted, blocked)
        on the canvas.

        Args:
            canvas (pygame.Surface): The surface to draw on.
            graph (Graph): The graph containing zones.
        """

        load_restricted = pygame.image.load(self.image_path_restricted)
        load_priority = pygame.image.load(self.image_path_priority)
        load_blocked = pygame.image.load(self.image_path_blocked)

        for zone in self.list_zones.values():

            hub_image = None
            if zone.zone_type == ZoneTypes.PRIORITY:
                hub_image = pygame.transform.scale(
                    load_priority,
                    self.size_type_zones
                )
            elif zone.zone_type == ZoneTypes.RESTRICTED:
                hub_image = pygame.transform.scale(
                    load_restricted,
                    self.size_type_zones
                )
            elif zone.zone_type == ZoneTypes.BLOCKED:
                hub_image = pygame.transform.scale(
                    load_blocked,
                    self.size_type_zones
                )

            current_pos = self.__get_pos(
                zone.x, zone.y
            )

            if hub_image:
                current_pos = (
                    current_pos[0] + self.plus_zone_types[0],
                    current_pos[1] + self.plus_zone_types[1]
                )
                canvas.blit(hub_image, current_pos)

    def __draw_drones(
        self, graph: Graph
    ) -> None:
        """
        Prepare drone surfaces for rendering.

        Args:
            canvas (pygame.Surface): The surface (not used in this method).
            graph (Graph): The graph containing drones.
        """

        self.space_drones = {}

        for drone in graph.drones.values():

            rotate_drone = self.__rotate_image()

            self.space_drones.update({
                drone.id: rotate_drone
            })

    def get_drone(self, id: str) -> pygame.Surface | None:
        """
        Get the surface for a specific drone.

        Args:
            id (str): The drone ID.

        Returns:
            pygame.Surface: The drone's surface, or None if not found.
        """
        return self.space_drones.get(id, None)

    def get_render_coords(
        self, x: int, y: int
    ) -> tuple:
        """
        Get rendering coordinates for a position.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.

        Returns:
            tuple: Rendered (x, y) coordinates.
        """
        pos = self.__get_pos(x, y)
        return (
            pos[0] + self.hub_w_h[0] // 2,
            pos[1] + self.hub_w_h[1] // 2
        )

    def colorize(self, image: pygame.Surface, color: tuple) -> pygame.Surface:
        """
        Apply color tint to an image.

        Args:
            image (object): The image to colorize.
            size (tuple): Size of the image.
            color (tuple): RGBA color tuple.

        Returns:
            object: The colorized image.
        """
        color_surface = pygame.Surface(image.get_size()).convert_alpha()
        color_surface.fill(color)

        new_image = image.copy()
        new_image.blit(
            color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
        return new_image

    def __rotate_image(
        self
    ) -> pygame.Surface:
        """
        Rotate the drone image based on the current angle.

        Returns:
            pygame.Surface: The rotated image.
        """

        rotate_image = pygame.transform.rotate(
            self.drone_img,
            self.angle
        )

        return rotate_image

    def __move_drones(self, canvas: pygame.Surface, graph: Graph) -> None:
        """
        Update and animate drone positions based on their paths.

        Handles interpolation between zones and turn-based movement.

        Args:
            canvas (pygame.Surface): The surface to draw on.
            graph (Graph): The graph containing drones and their paths.
        """

        current_time = pygame.time.get_ticks()

        elapsed_since_turn = current_time - self.last_turn_update_time

        move_duration = self.turn_delay_ms * 0.9
        progress = min(1, elapsed_since_turn / move_duration)

        for drone in graph.drones.values():

            if not drone.path:
                continue

            path_step = next(
                (
                    s for s in drone.path
                    if s[0] == self.current_sim_turns
                ), None
            )
            next_step = next(
                (
                    s for s in drone.path
                    if s[0] == self.current_sim_turns + 1
                ), None
            )

            if path_step:
                curr_pos: Tuple[float, float] = self.__get_location_pos(
                    path_step[1]
                )

                if next_step:
                    # ? If the prev and next steps are quales the drone is wait
                    if next_step[1] == path_step[1]:
                        # ? Stop the drone in the current (x, y)
                        drone.current_x, drone.current_y = curr_pos
                    else:
                        next_pos = self.__get_location_pos(next_step[1])
                        drone.current_x = curr_pos[0] + (
                            next_pos[0] - curr_pos[0]
                        ) * progress
                        drone.current_y = curr_pos[1] + (
                            next_pos[1] - curr_pos[1]
                        ) * progress
                else:
                    drone.current_x, drone.current_y = curr_pos

            self.__draw_single_drone(canvas, drone)

        if (
            elapsed_since_turn >= self.turn_delay_ms
            and not self.__all_drones_reached(graph)
        ):
            self.current_sim_turns += 1
            self.last_turn_update_time = current_time

    def __get_location_pos(self, name: str) -> Tuple[float, float]:
        """
        Get the position coordinates for a location name.

        Handles both zone names and connection names (e.g., "A-B").

        Args:
            name (str): The location name.

        Returns:
            Tuple[float, float]: The (x, y) coordinates.
        """
        if "-" in name:
            u_name, v_name = name.split("-")
            u = self.list_zones[u_name]
            v = self.list_zones[v_name]
            p1 = self.__get_pos(u.x, u.y)
            p2 = self.__get_pos(v.x, v.y)
            return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

        zone = self.list_zones[name]
        return self.__get_pos(zone.x, zone.y)

    def __draw_single_drone(
        self, canvas: pygame.Surface, drone: Drone
    ) -> None:
        """
        Draw a single drone on the canvas with offset to avoid overlap.

        Args:
            canvas (pygame.Surface): The surface to draw on.
            drone (Drone): The drone to draw.
        """
        surface = self.get_drone(drone.id)
        if not surface:
            return

        is_match: Match | None = search(r'\d+', drone.id)
        if is_match:
            drone_num = int(is_match.group())
            offset_x = (drone_num % 3 - 1) * 10
            offset_y = (drone_num // 3 % 3 - 1) * 10

            rect = surface.get_rect(
                center=(
                    drone.current_x + self.plus_drone_types[0] + offset_x,
                    drone.current_y + self.plus_drone_types[1] + offset_y
                )
            )
            canvas.blit(surface, rect.topleft)

    def __get_pos(self, x: int, y: int) -> tuple:
        """
        Calculate the rendering position for coordinates.

        Args:
            x (int): X-coordinate.
            y (int): Y-coordinate.

        Returns:
            tuple: Rendered (x, y) position.
        """
        x_ = (x - self.min_x) * (self.spacing * self.dynamic_scale) + (
            self.start_x)
        y_ = (y - self.min_y) * (self.spacing * self.dynamic_scale) + (
            self.start_y)
        return (x_, y_)

    def initialize_visualization(self, graph: Graph) -> None:
        """
        Initialize visualization parameters based on screen size and graph.

        Sets image sizes, spacing, and scaling factors.

        Args:
            graph (Graph): The graph to visualize.
        """

        screen_with = self.pygame_info.current_w

        if screen_with < 3000:

            self.change_size_image(
                NameImages.DRONE,
                SizeImages.SMALL
            )
            self.change_size_image(
                NameImages.HUB,
                SizeImages.SMALL
            )
            self.change_size_image(
                NameImages.SPACING,
                SizeImages.SMALL
            )
            self.change_size_image(
                NameImages.ZONE_TYPES,
                SizeImages.SMALL
            )
        else:
            self.change_size_image(
                NameImages.DRONE,
                SizeImages.BIG
            )
            self.change_size_image(
                NameImages.HUB,
                SizeImages.BIG
            )
            self.change_size_image(
                NameImages.SPACING,
                SizeImages.BIG
            )
            self.change_size_image(
                NameImages.ZONE_TYPES,
                SizeImages.BIG
            )

        spacing = self.spacing

        all_x = [zone.x for zone in graph.zones.values()]
        all_y = [zone.y for zone in graph.zones.values()]

        all_x += [graph.start_zone.x] + [graph.end_zone.x]
        all_y += [graph.start_zone.y] + [graph.end_zone.y]

        if not all_x:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        raw_content_width = (max_x - min_x) * spacing + self.hub_w_h[0]
        raw_content_height = (max_y - min_y) * spacing + self.hub_w_h[1]

        padding = 100
        width_radio = self.surface_width / (raw_content_width + padding)
        height_radio = self.surface_height / (raw_content_height + padding)

        self.dynamic_scale = min(width_radio, height_radio, 1.0)

        scale_width = raw_content_width * self.dynamic_scale
        scale_height = raw_content_height * self.dynamic_scale

        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.start_x = (self.w_width - scale_width) // 2
        self.start_y = (self.w_height - scale_height) // 2

    def change_size_image(
        self, name_image: NameImages, size: SizeImages | None
    ) -> None:
        """
        Change the size of visual elements based on screen resolution.

        Args:
            name_image (str): The type of image to resize.
            size (str): The size option ("big" or "small").
        """
        if name_image == NameImages.HUB:
            if size == SizeImages.BIG:
                self.hub_w_h = (68, 175)
            elif size == SizeImages.SMALL:
                self.hub_w_h = (30, 80)
        elif name_image == NameImages.DRONE:
            if size == SizeImages.BIG:
                self.image_path_drone = "drone_big.png"
                self.plus_drone_types = (30, 82)
            elif size == SizeImages.SMALL:
                self.image_path_drone = "drone.png"
                self.plus_drone_types = (15, 40)
        elif name_image == NameImages.SPACING:
            if size == SizeImages.BIG:
                self.spacing = 250
            elif size == SizeImages.SMALL:
                self.spacing = 300
        elif name_image == NameImages.ZONE_TYPES:
            if size == SizeImages.BIG:
                self.size_type_zones = (50, 50)
                self.plus_zone_types = (10, 105)
            elif size == SizeImages.SMALL:
                self.size_type_zones = (25, 25)
                self.plus_zone_types = (3, 48)

    def __initialize_drone_start(self, graph: Graph) -> None:
        """
        Initialize drone starting positions.

        Args:
            graph (Graph): The graph containing drones.
        """
        for drone in graph.drones.values():
            current_pos = self.__get_pos(
                drone.current_zone.x, drone.current_zone.y
            )
            drone.current_x = current_pos[0]
            drone.current_y = current_pos[1]

    def __all_drones_reached(self, graph: Graph) -> bool:
        """
        Check if all drones have reached their final destinations.

        Args:
            graph (Graph): The graph containing drones.

        Returns:
            bool: True if all drones have finished their paths.
        """
        for drone in graph.drones.values():
            if not drone.path:
                continue
            last_turn_for_drone = drone.path[-1][0]
            if self.current_sim_turns < last_turn_for_drone:
                return False
        return True
