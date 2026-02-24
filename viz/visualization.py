import pygame
from pygame.colordict import THECOLORS
from models import Graph


class VisualizeSimulation:
    def __init__(self):
        pygame.init()

        self.pygame_info = pygame.display.Info()
        self.w_width = self.pygame_info.current_w * 0.8
        self.w_height = self.pygame_info.current_h * 0.8
        self.image_path = "assets/bg.png"
        self.image_path_hub = "assets/hub.png"
        self.surface_width = self.w_width * 0.9
        self.surface_height = self.w_height * 0.9
        self.margin_x = (self.w_width - self.surface_width) // 2
        self.margin_y = (self.w_height - self.surface_height) // 2
        self.radius = 80
        self.spacing = 100
        self.hub_w_h = (40, 100)
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        self.start_x = 0
        self.start_y = 0

    def run(self, graph: Graph):
        pygame.display.set_caption("Fly-in")

        screen = pygame.display.set_mode(
            (self.w_width, self.w_height)
        )
        image = pygame.image.load(self.image_path)
        canvas = pygame.transform.scale(
            image, (self.w_width, self.w_height)
        )

        self.__draw_zones(canvas, graph)
        self.__draw_edges(canvas, graph)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(canvas, (0, 0))
            pygame.display.update()

        # * pygame quit
        pygame.quit()

    def __draw_zones(self, canvas: pygame.Surface, graph: Graph) -> None:
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

        load_hub_image = pygame.image.load(self.image_path_hub)

        list_zones = {key: value for key, value in graph.zones.items()}
        list_zones.update({
            graph.start_zone.name: graph.start_zone,
            graph.end_zone.name: graph.end_zone
        })

        for zone in list_zones.values():

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

            draw_x = (zone.x - min_x) * spacing + start_x
            draw_y = (zone.y - min_y) * spacing + start_y

            canvas.blit(hub_image, (draw_x, draw_y))

    def colorize(self, image: object, size: tuple, color: tuple) -> object:
        color_surface = pygame.Surface(image.get_size()).convert_alpha()
        color_surface.fill(color)

        new_image = image.copy()
        new_image.blit(
            color_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT
        )
        return new_image

    def __draw_edges(self, canvas: pygame.Surface, graph: Graph) -> None:
        print("draw edges")

        list_zones = {key: value for key, value in graph.zones.items()}
        list_zones.update({
            graph.start_zone.name: graph.start_zone,
            graph.end_zone.name: graph.end_zone
        })

        for zone in list_zones.values():

            if zone.target_zone:
                for target in zone.target_zone:

                    pygame.draw.line(
                        canvas,
                        THECOLORS.get("white"),
                        self.get_render_coords(
                            zone.x, zone.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        self.get_render_coords(
                            target.x, target.y, self.min_x, self.min_y,
                            self.start_x, self.start_y
                        ),
                        2
                    )

    def get_render_coords(
        self, x: int, y: int, min_x: int, min_y: int,
        max_x: int, max_y: int
    ) -> tuple:
        render_x = (
            ((x - min_x) * self.spacing + self.start_x) + (self.hub_w_h[0] // 2)
        )
        render_y = (
            ((y - min_y) * self.spacing + self.start_y) + (self.hub_w_h[1] // 2)
        )
        return (render_x, render_y)
