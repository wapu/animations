import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

from colors import *



import imageio.v3 as iio
from scipy.ndimage import distance_transform_edt
from shapely import geometry as geo



class Test():

    def __init__(self, width, height):
        self.w = width
        self.h = height

        # self.bg = iio.imread('data/uebeldumm.png').T
        # self.points = np.load('data/uebeldumm_processed.npy')

        self.n_waves = 20


    def reset(self):
        self.last_update = time()


    def event(self):
        pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def update(self, bpm, last_beat, delta_t):

        # Limit FPS to BPM for everything below
        if time() - last_beat < 60/bpm:
            self.last_update = last_beat
            return
        if time() - self.last_update < 60/bpm:
            return
        self.last_update += 60/bpm



    def draw(self, screen, bpm, last_beat, brightness):
        # for i in range(len(self.points)):
        #     pygame.draw.circle(screen, (255,255,255), self.points[i], radius=2)

        t = time()
        progress = ((t/4) % (60/bpm)) / (60/bpm)

        # for i in range(len(self.points)):
        #     p1, p2 = self.points[i], self.points[(i+1) % len(self.points)]
        #     hue = (0.1*t + 0.2 * np.sin(2*np.pi*(self.n_waves*i / len(self.points) + progress))) % 1
        #     l = 0.5
        #     pygame.draw.aaline(screen, hls_to_rgb(hue, l * brightness), p1, p2)
        pygame.draw.aalines(screen, hls_to_rgb(.5), False, self.points)


        # pygame.surfarray.blit_array(screen, self.density)
        # screen.blit(pygame.surfarray.make_surface(self.density), (0,0))

        print(time() - t)




if __name__ == '__main__':
    pass

