import pygame
from pygame.colordict import THECOLORS
from models import Graph, Zone, ZoneTypes, Drone
from typing import Dict


class VisualizeSimulation:
    def __init__(self):
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
        self.drone_img = ""
        self.surface_width = self.w_width * 0.9
        self.surface_height = self.w_height * 0.9
        self.margin_x = (self.w_width - self.surface_width) // 2
        self.margin_y = (self.w_height - self.surface_height) // 2
        self.radius = 80
        self.spacing = 300
        self.hub_w_h = (68, 175)
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.start_x = 0
        self.start_y = 0
        self.list_zones: Dict[str, Zone] = {}
        self.line = {
            "color": THECOLORS.get("lightskyblue"),
            "border": 5
        }
        self.size_type_zones = (50, 50)
        self.cost_zones = {
            ZoneTypes.NORMAL.value: 1,
            ZoneTypes.RESTRICTED.value: 2,
            ZoneTypes.PRIORITY.value: 1,
            ZoneTypes.BLOCKED.value: 0,
        }
        self.angle = 0
        self.size_drone = (200, 100)
        self.clock = pygame.time.Clock()
        self.space_drones: Dict[Drone, pygame.Surface] = {}

    def run(self, graph: Graph):
        pygame.display.set_caption("Fly-in")
        screen = pygame.display.set_mode((self.w_width, self.w_height))

        self.drone_img = pygame.image.load(
            self.image_path_drone
        ).convert_alpha()

        load_original_bg = pygame.image.load(self.image_path).convert()

        canvas = pygame.transform.scale(
            load_original_bg, (self.w_width, self.w_height)
        )

        base_canvas = canvas.copy()
        self.__draw_edges(base_canvas, graph)
        self.__draw_zones(base_canvas, graph)
        self.__draw_type_zone(base_canvas, graph)

        running = True
        while running:
            pygame.time.delay(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(base_canvas, (0, 0))

            self.angle = (self.angle + 10) % 360

            self.__draw_drones(screen, graph)
            self.__move_drone(screen, graph)

            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()

    def __draw_edges(self, canvas: pygame.Surface, graph: Graph) -> None:
        spacing = self.spacing

        all_x = [zone.x for zone in graph.zones.values()]
        all_y = [zone.y for zone in graph.zones.values()]

        all_x += [graph.start_zone.x]
        all_y += [graph.start_zone.y]

        if not all_x:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        content_width = (max_x - min_x) * spacing
        content_height = (max_y - min_y) * spacing

        start_x = (self.surface_width - content_width) // 2
        start_y = (self.surface_height - content_height) // 2

        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y
        self.start_x = start_x
        self.start_y = start_y

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
                        self.line.get("color"),
                        self.get_render_coords(
                            zone.x, zone.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        self.get_render_coords(
                            target.x, target.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        self.line.get("border")
                    )

    def __draw_zones(self, canvas: pygame.Surface, graph: Graph) -> None:

        load_hub_image = pygame.image.load(self.image_path_hub)

        for zone in self.list_zones.values():

            color = zone.color if zone.color else THECOLORS.get("white")

            a, b, c, d = color
            new_a = int(a * 0.7 + 255 * 0.3)
            new_b = int(b * 0.7 + 255 * 0.3)
            new_c = int(c * 0.7 + 255 * 0.3)

            new_load = self.colorize(
                load_hub_image.convert_alpha(),
                self.hub_w_h, (new_a, new_b, new_c, d)
            )

            hub_image = pygame.transform.scale(
                new_load,
                self.hub_w_h
            )

            draw_x = (zone.x - self.min_x) * self.spacing + self.start_x
            draw_y = (zone.y - self.min_y) * self.spacing + self.start_y

            canvas.blit(hub_image, (draw_x, draw_y))

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

            draw_x = (zone.x - self.min_x) * self.spacing + self.start_x + 10
            draw_y = (zone.y - self.min_y) * self.spacing + self.start_y + 97

            if hub_image:
                canvas.blit(hub_image, (draw_x, draw_y))

    def __draw_drones(
        self, canvas: pygame.Surface, graph: Graph
    ) -> None:

        self.space_drones = {}

        for drone in graph.drones.values():
            draw_x = (drone.current_zone.x - self.min_x) * self.spacing + (
                self.start_x + 35)
            draw_y = (drone.current_zone.y - self.min_y) * self.spacing + (
                self.start_y + 85)

            rotate_drone = self.__rotate_image(canvas, draw_x, draw_y)
            self.space_drones.update({
                drone: rotate_drone
            })

    def get_drone(self, drone: Drone) -> pygame.Surface:
        return self.space_drones.get(drone, None)

    def get_render_coords(
        self, x: int, y: int, min_x: int, min_y: int,
        max_x: int, max_y: int
    ) -> tuple:
        render_x = (
            ((x - min_x) * self.spacing + self.start_x) + (
                self.hub_w_h[0] // 2
            )
        )
        render_y = (
            ((y - min_y) * self.spacing + self.start_y) + (
                self.hub_w_h[1] // 2
            )
        )
        return (render_x, render_y)

    def colorize(self, image: object, size: tuple, color: tuple) -> object:
        color_surface = pygame.Surface(image.get_size()).convert_alpha()
        color_surface.fill(color)

        new_image = image.copy()
        new_image.blit(
            color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
        return new_image

    def __rotate_image(
        self, canvas: pygame.Surface, draw_x: int, draw_y: int
    ) -> object:

        rotate_image = pygame.transform.rotate(
            self.drone_img,
            self.angle
        )

        rect = rotate_image.get_rect(center=(draw_x, draw_y))

        canvas.blit(rotate_image, rect.topleft)
        return rotate_image

    def __move_drone(self, canvas: pygame.Surface, graph: Graph) -> None:
        drone = graph.get_drone("D1")

        surface = self.get_drone(drone)

        draw_x = (drone.target_zone[0].x - self.min_x) * self.spacing + (
            self.start_x + 35)
        draw_y = (drone.target_zone[0].y - self.min_y) * self.spacing + (
            self.start_y + 85)

        rect = surface.get_rect(
            center=(draw_x, draw_y)
        )

        canvas.blit(surface, rect.topleft)
