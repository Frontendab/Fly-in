import pygame


def start_visualization():
    pygame.init()

    pygame.display.set_mode((500, 500))
    pygame.display.set_caption("Fly-in")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # * Pygame quit
    pygame.quit()
