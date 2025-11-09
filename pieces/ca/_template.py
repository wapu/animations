import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from colors import *



class Name():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])
        self.WH = np.array([width, height])

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0


    def event(self, num):
        match num:
            case 0:
                pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        pass


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        pass


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        pass
