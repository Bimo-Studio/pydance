import logging

logger = logging.getLogger(__name__)

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Test")
screen.fill((255, 255, 255))
pygame.display.flip()

print("Pygame window created. Close it to exit.")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

pygame.quit()
print("Test complete")
