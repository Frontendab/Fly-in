import pygame
from enum import Enum


class AttributeWindow(Enum):
    X = 3500
    Y = 1700
    image_path = "assets/bg.png"


def start_visualization():
    pygame.init()

    pygame.display.set_caption("Fly-in")

    screen = pygame.display.set_mode(
        (AttributeWindow.X.value, AttributeWindow.Y.value)
    )
    bg_image = pygame.image.load(AttributeWindow.image_path.value)
    bg_image = pygame.transform.scale(
        bg_image, (AttributeWindow.X.value, AttributeWindow.Y.value)
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(bg_image, (0, 0))
        pygame.display.update()

    # * pygame quit
    pygame.quit()
