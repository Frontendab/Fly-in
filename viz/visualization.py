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
        self.surface_width = self.w_width * 0.9
        self.surface_height = self.w_height * 0.9
        self.margin_x = (self.w_width - self.surface_width) // 2
        self.margin_y = (self.w_height - self.surface_height) // 2
        self.radius = 80
        self.spacing = 250

    def run(self, graph: Graph):
        pygame.display.set_caption("Fly-in")

        screen = pygame.display.set_mode(
            (self.w_width, self.w_height)
        )
        image = pygame.image.load(self.image_path)
        bg_image = pygame.transform.scale(
            image, (self.w_width, self.w_height)
        )

        canvas = pygame.transform.scale(
            image,
            (self.surface_width, self.surface_height)
        )

        self.__draw_zones(canvas, graph)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(bg_image, (0, 0))
            screen.blit(canvas, (self.margin_x, self.margin_y))
            pygame.display.update()

        # * pygame quit
        pygame.quit()

    def __draw_zones(self, canvas: pygame.Surface, graph: Graph) -> None:
        spacing = self.spacing

        all_x = [zone.x for zone in graph.zones.values()]
        all_y = [zone.y for zone in graph.zones.values()]

        if not all_x:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        content_width = (max_x - min_x) * spacing
        content_height = (max_y - min_y) * spacing

        start_x = (self.surface_width - content_width) // 2
        start_y = (self.surface_height - content_height) // 2

        for zone in graph.zones.values():
            draw_x = (zone.x - min_x) * spacing + start_x
            draw_y = (zone.y - min_y) * spacing + start_y

            pygame.draw.circle(
                canvas,
                THECOLORS.get("yellow"),
                [int(draw_x), int(draw_y)],
                self.radius, 0
            )
