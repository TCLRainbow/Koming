import pygame
from pygame.locals import *


class Game:
    SIZE = 800, 800

    def __init__(self, bg_file):
        self.screen = pygame.display.set_mode(Game.SIZE)
        self.load_image(bg_file)
        pygame.display.init()
        pygame.display.set_caption("Pygame Tiled Demo")
        self.running = True

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                elif event.type == KEYDOWN:
                    if event.key == K_l:
                        pass

        pygame.quit()

    def load_image(self, file):
        image = pygame.image.load(file)
        image = pygame.transform.scale(image, Game.SIZE)
        rect = image.get_rect()

        self.screen.blit(image, rect)
        pygame.display.update()