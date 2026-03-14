import pygame
from pygame.colordict import THECOLORS
from models import (
    Graph, Zone, ZoneTypes,
    Drone, PathFinder
)
from typing import Dict, Tuple, cast
from enum import Enum
from math import hypot


class SizeImages(Enum):
    BIG = "big"
    SMALL = "small"


class NameImages(Enum):
    HUB = "hub"
    DRONE = "drone"
    SPACING = "spacing"
    ZONE_TYPES = "zone_types"


class VisualizeSimulation:
    def __init__(self) -> None:
        pygame.init()

        self.pygame_info = pygame.display.Info()
        self.w_width = self.pygame_info.current_w * 0.8
        self.w_height = self.pygame_info.current_h * 0.8
        self.image_path = "assets/bg.png"
        self.image_path_hub = "assets/hub.png"
        self.image_path_priority = "assets/priority.png"
        self.image_path_restricted = "assets/restricted.png"
        self.image_path_blocked = "assets/blocked.png"
        self.image_path_drone = "assets/drone.png"
        self.drone_img: pygame.Surface = pygame.Surface((32, 32))
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
        self.line_color: Tuple[int, int, int, int] = (
            THECOLORS.get("lightskyblue", (
                135, 206, 250, 255
            ))
        )
        self.line_border: int = 5
        self.size_type_zones = (25, 25)
        self.angle = 0
        self.clock = pygame.time.Clock()
        self.plus_zone_types = (10, 105)
        self.plus_drone_types = (15, 40)
        self.speed_drones = 4
        self.current_sim_turns = 0

    def run(self, graph: Graph) -> None:
        pygame.display.set_caption("Fly-in")
        screen = pygame.display.set_mode(
            (self.w_width, self.w_height)
        )

        self.drone_img = pygame.image.load(
            self.image_path_drone
        ).convert_alpha()

        load_original_bg = pygame.image.load(self.image_path).convert()

        canvas = pygame.transform.smoothscale(
            load_original_bg, (self.w_width, self.w_height)
        )

        base_canvas = canvas.copy()
        self.__draw_edges(base_canvas, graph)
        self.__draw_zones(base_canvas, graph)
        self.__draw_type_zone(base_canvas, graph)

        self.__initialize_drone_start(graph)

        # TODO: TESTING ALGORITHM OF A*(A-STAR)
        pathfinder = PathFinder(graph)
        pathfinder.a_star_search()
        # pathfinder.generate_output_trace()

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

            self.__animation_drones(screen, graph)

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def __draw_edges(self, canvas: pygame.Surface, graph: Graph) -> None:
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
                        self.line_color,
                        self.get_render_coords(
                            zone.x, zone.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        self.get_render_coords(
                            target.x, target.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        self.line_border
                    )

    def __draw_zones(self, canvas: pygame.Surface, graph: Graph) -> None:

        load_hub_image = pygame.image.load(self.image_path_hub)

        for zone in self.list_zones.values():

            color_val = zone.color
            color: Tuple[int, int, int, int] | str | None = color_val

            if isinstance(color_val, str):
                color = cast(
                    Tuple[int, int, int, int],
                    THECOLORS.get(color_val.lower())
                )

            if isinstance(color, tuple) and color:
                a, b, c, d = color
                new_a = int(a * 0.6 + 255 * 0.3)
                new_b = int(b * 0.6 + 255 * 0.3)
                new_c = int(c * 0.6 + 255 * 0.3)

                new_load = self.colorize(
                    load_hub_image.convert_alpha(),
                    self.hub_w_h, (new_a, new_b, new_c, d)
                )

                hub_image = pygame.transform.scale(
                    new_load,
                    self.hub_w_h
                )

                current_pos = self.__get_pos(
                    zone.x, zone.y
                )

                canvas.blit(hub_image, current_pos)

    def __draw_type_zone(self, canvas: pygame.Surface, graph: Graph) -> None:

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

    def get_render_coords(
        self, x: int, y: int, min_x: int, min_y: int,
        max_x: float, max_y: float
    ) -> tuple:
        pos = self.__get_pos(x, y)
        return (
            pos[0] + self.hub_w_h[0] // 2,
            pos[1] + self.hub_w_h[1] // 2
        )

    def colorize(
        self, image: pygame.Surface, size: tuple, color: tuple
    ) -> pygame.Surface:
        color_surface = pygame.Surface(image.get_size()).convert_alpha()
        color_surface.fill(color)

        new_image = image.copy()
        new_image.blit(
            color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
        return new_image

    def __rotate_image(
        self, canvas: pygame.Surface, draw_x: int, draw_y: int
    ) -> pygame.Surface:

        rotate_image = pygame.transform.rotate(
            self.drone_img,
            self.angle
        )

        return rotate_image

    def __animation_drones(
        self, canvas: pygame.Surface,
        graph: Graph
    ) -> None:
        all_drones_targets = True
        for i, drone in enumerate(graph.drones.values()):

            if not hasattr(drone, "departure_turn"):
                drone.departure_turn = i * 45

            if self.current_sim_turns < drone.departure_turn:
                self.__draw_single_drone(canvas, drone)
                continue

            if drone.target_index < len(drone.path):
                target = drone.path[drone.target_index]
                target_pos = self.__get_pos(
                    target.x,
                    target.y
                )
                target_x, target_y = target_pos

                dx = target_x - drone.current_x
                dy = target_y - drone.current_y
                distance = hypot(dx, dy)

                speed = self.speed_drones * self.dynamic_scale
                if target.zone_type == ZoneTypes.RESTRICTED:
                    speed /= 3
                if target.zone_type == ZoneTypes.PRIORITY:
                    speed += 5
                if distance <= speed:
                    drone.current_x = target_x
                    drone.current_y = target_y
                    drone.target_index += 1
                else:
                    drone.current_x += (dx / distance) * speed
                    drone.current_y += (dy / distance) * speed

            self.__draw_single_drone(canvas, drone)

        if all_drones_targets:
            self.current_sim_turns += 1

    def __draw_single_drone(
        self, canvas: pygame.Surface, drone: Drone
    ) -> None:
        current_pos = self.__get_pos(
            drone.current_zone.x, drone.current_zone.y
        )

        surface = self.__rotate_image(
            canvas, current_pos[0] + self.plus_drone_types[0],
            current_pos[1] + self.plus_drone_types[1]
        )

        if surface:
            rect = surface.get_rect(
                center=(
                    drone.current_x + self.plus_drone_types[0],
                    drone.current_y + self.plus_drone_types[1]
                )
            )
            canvas.blit(surface, rect.topleft)

    def __get_pos(self, x: int, y: int) -> tuple:
        x_ = (x - self.min_x) * (self.spacing * self.dynamic_scale) + (
            self.start_x)
        y_ = (y - self.min_y) * (self.spacing * self.dynamic_scale) + (
            self.start_y)
        return (x_, y_)

    def initialize_visualization(self, graph: Graph) -> None:

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
        self, name_image: NameImages, size: SizeImages
    ) -> None:
        if name_image == NameImages.HUB:
            if size == SizeImages.BIG:
                self.hub_w_h = (68, 175)
            elif size == SizeImages.SMALL:
                self.hub_w_h = (30, 80)
        elif name_image == NameImages.DRONE:
            if size == SizeImages.BIG:
                self.image_path_drone = "assets/drone_big.png"
                self.plus_drone_types = (30, 82)
            elif size == SizeImages.SMALL:
                self.image_path_drone = "assets/drone.png"
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
        for drone in graph.drones.values():
            current_pos = self.__get_pos(
                drone.current_zone.x, drone.current_zone.y
            )
            drone.current_x = current_pos[0]
            drone.current_y = current_pos[1]
