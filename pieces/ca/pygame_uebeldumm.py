import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

from colors import *



import imageio.v3 as iio
from shapely import geometry as geo



def de_boor_np(t, points, degree=4, i=None, n=None):
    if i is None: i = np.round(t).astype(int)
    if n is None: n = degree

    if degree == 0:
        return points[i % len(points)]
    alpha = ((t - i) / (n + 1 - degree))[:,None]
    return (1 - alpha) * de_boor_np(t, points, degree-1, i=i-1, n=n) + alpha * de_boor_np(t, points, degree-1, i=i, n=n)

def scale_around(poly, factor, anchor):
    return anchor + factor * (poly - anchor)

def hermite(val):
    return 3*val*val - 2*val*val*val



class UebelDumm():

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.center = np.array([width/2, height/2])

        self.points = np.load('data/uebeldumm_processed.npy')
        self.bg = np.load('data/uebeldumm_bg_processed.npy')

        self.n_waves = 20
        self.n_dots = 50
        self.trail = 10
        self.n_dashes = 4000

        self.reset()


    def reset(self):
        self.intensity = 0

        self.bg_lightup = 0
        self.locations = np.tile(np.random.randint(len(self.points), size=(self.n_dots, 1)), (1, self.trail)).astype(float)
        self.speeds = -(0.5 + 0.2*np.random.rand(self.n_dots))
        self.dash_offset = 0
        self.bg_res = 0


    def event(self, num):
        if num == 1:
            self.bg_lightup = 1


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        self.locations[:,0] -= 5
        self.bg_res = (self.bg_res - 1) % 4

        if self.intensity == 3:
            self.bg_lightup += 0.3


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        self.locations[:,1:] = self.locations[:,:-1]
        self.locations[:,0] += self.speeds
        self.dash_offset = (self.dash_offset - 0.2) % (len(self.points)/self.n_dashes)
        self.bg_lightup *= 0.75


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        progress_2 = (2 * measure_progress) % 1

        # Background tsp path
        bg = self.bg
        bg = scale_around(self.bg, 0.97 + 0.02 * beat_progress, self.center)

        # Bounce and jump
        points = self.points
        if self.intensity >= 1:
            points = points + 10*np.array([-np.cos(2*np.pi * progress_2), -np.abs(np.sin(2*np.pi * progress_2))])
            points = scale_around(points, 1 - 0.04 * beat_progress, self.center)
        else:
            points = scale_around(points, 1 - 0.02 * beat_progress, self.center)

        # Locations for jumpy dots and their trail
        dots = [de_boor_np(self.locations[:,i] % len(points), points) for i in range(self.trail)]

        # Coordinates of dashes for main tsp path
        d1 = de_boor_np(np.linspace(0, len(points), self.n_dashes, endpoint=False) + self.dash_offset, points)
        d2 = de_boor_np(np.linspace(0, len(points), self.n_dashes, endpoint=False) + self.dash_offset + 1, points)

        screen.lock()

        # Draw background
        if self.intensity <= 2:
            pygame.draw.lines(screen, hls_to_rgb(1, (0.03 + self.bg_lightup) * brightness, 0), True, bg, width=3)
        else:
            pygame.draw.lines(screen, hls_to_rgb(1, (0.03 + self.bg_lightup) * brightness, 0), True, bg[::self.bg_res + 1], width=3)

        # Draw dot trails
        if self.intensity >= 2:
            for d in range(self.n_dots):
                hue = (0.1*t + 0.2 * np.sin(2*np.pi*(self.n_waves*(self.locations[d,0]%len(points)) / len(points) + 0.5*t))) % 1
                for i in range(1, self.trail):
                    p1 = dots[i-1][d]
                    p2 = dots[i][d]
                    pygame.draw.line(screen, hls_to_rgb(hue, 0.5 * brightness * 0.75**i), p1, p2, width=4)

        # Draw dashed main tsp path
        for i in range(len(d1)):
            hue = (0.1*t + 0.2 * np.sin(2*np.pi*(self.n_waves*((i + self.dash_offset)/1000) + 0.5*t))) % 1
            if self.intensity == 3:
                l = 0.4 + 0.2 * np.sin(2*np.pi * beat_progress)
            else:
                l = 0.3
            pygame.draw.aaline(screen, hls_to_rgb(hue, l * brightness), d1[i], d2[i])

        # Draw dots
        if self.intensity >= 2:
            for d in range(self.n_dots):
                hue = (0.1*t + 0.2 * np.sin(2*np.pi*(self.n_waves*(self.locations[d,0]%len(points)) / len(points) + 0.5*t))) % 1
                pygame.draw.circle(screen, hls_to_rgb(hue, 0.5 * brightness), dots[0][d], radius=4)
                pygame.draw.circle(screen, (0,0,0), dots[0][d], radius=3)

        screen.unlock()


if __name__ == '__main__':
    pass

    import sys
    sys.path.insert(0, '../../tools')
    from stippling import *
    from tsp import *

    # points = stipple_image_points('data/uebeldumm.png', n_points=5000, max_iterations=100)
    # np.save('data/uebeldumm.npy', points)

    # points = np.load('data/uebeldumm.npy')
    # route = solve_tsp_fast(points, duration_seconds=300)
    # write_cyc(route, 'data/uebeldumm.cyc')

    # postprocess_cyc('data/uebeldumm.npy', 'data/uebeldumm.cyc', 'data/uebeldumm_processed.npy',
    #                 None, segment_length=5, degree=4, normalize_points=False)


    # points = stipple_image_points('data/uebeldumm_bg.png', n_points=5000, max_iterations=100)
    # np.save('data/uebeldumm_bg.npy', points)

    # points = np.load('data/uebeldumm_bg.npy')
    # route = solve_tsp_fast(points, duration_seconds=300)
    # write_cyc(route, 'data/uebeldumm_bg.cyc')

    # postprocess_cyc('data/uebeldumm_bg.npy', 'data/uebeldumm_bg.cyc', 'data/uebeldumm_bg_processed.npy',
    #                 None, segment_length=100, degree=4, normalize_points=False)
