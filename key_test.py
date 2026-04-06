import logging

logger = logging.getLogger(__name__)

import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
print("Press arrow keys to test. Press ESC to exit.")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            else:
                print(f"Key pressed: {pygame.key.name(event.key)}")
    pygame.time.wait(10)

pygame.quit()
