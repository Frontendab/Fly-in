import pygame


def start_display():
    pygame.init()

    pygame.display.set_mode((1000, 1000))
    pygame.display.set_caption("Fly-in")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # * Pygame quit
    pygame.quit()
