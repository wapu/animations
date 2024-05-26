import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

from colors import *


def get_rotation_matrix(angle):
    return np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])

def rotate_around(poly, r, center):
    return center + np.matmul(poly - center, r)

def hermite(val):
    return 3*val*val - 2*val*val*val



class Faltr():

    def __init__(self, width, height):
        self.width = width
        self.center = np.array([width/2, height/2])

        # Coordinates
        self.scaling = 0.8
        self.xs = np.array([100, 280, 275, 295, 290, 310, 305, 325, 320, 340, 440]) * self.scaling
        self.ys = np.array([100, 100,  90, 100,  90, 100,  90, 100,  90, 100, 100]) * self.scaling
        self.xl = np.array([100, 280, 300, 330, 350, 380, 400, 430, 450, 480, 580]) * self.scaling
        self.yl = np.array([100, 100,  95, 100,  95, 100,  95, 100,  95, 100, 100]) * self.scaling
        self.h = 90 * self.scaling

        # Number of crawlers per row (x) and rows (y)
        self.n_x = 8
        self.n_y = 10

        self.reset()


    def reset(self):
        self.intensity = 0
        self.progress = 0
        self.highlights = []
        self.mode = 0

        # Set up initial positions and alternating group membership for crawlers
        offsets = []
        for y in range(self.n_y):
            random = np.random.rand()*415
            for x in range(self.n_x):
                offsets.append([x*450 - 70*((x+y)%2) + 207*(y%2) - 1020 + random, y*120 - 100])
        self.offsets = np.array(offsets)
        self.groups = np.array([(x+y)%2 for y in range(self.n_y) for x in range(self.n_x)])

        self.tilt = get_rotation_matrix(0.05 * np.cos(2*np.pi * time()/8 - np.pi/2))
        self.sway = np.array([200 * np.cos(2*np.pi * time()/8), 50 * np.sin(2*np.pi * time()/4)])
        self.switch_time = time()
        self.sway_lag = 0

        # Initial colors
        self.hues = np.array([(0.25*(0.5 + 0.5*np.sin(2*np.pi * x/self.n_x)) + 0.05*y)%1 for y in range(self.n_y) for x in range(self.n_x)])


    def event(self, num):
        if self.mode == 0:
            self.switch_time = time()
            self.mode = 1
        elif self.mode == 1:
            self.sway_lag += time() - self.switch_time
            self.mode = 0


    def clear_frame(self, screen):
        if self.mode == 0:
            screen.fill([200]*3, special_flags=pygame.BLEND_MULT)
        if self.mode == 1:
            screen.fill([0]*3)


    def beat(self, t):
        # Pick new highlights
        self.highlights = np.random.randint(len(self.offsets), size=10)

        # Move offset for crawlers that switch to contracting
        self.offsets[self.groups == 1] += np.array([140,0]) * self.scaling
        # Switch group memberships
        self.groups = 1 - self.groups


    def update(self, t, beat_progress, measure_progress, bpm):
        self.hues += 0.005

        # Tilt and sway for "drunk" effect
        if self.mode == 0:
            time = t - self.sway_lag
            self.tilt = get_rotation_matrix(0.05 * np.cos(2*np.pi * time/8 - np.pi/2))
            self.sway = np.array([200 * np.cos(2*np.pi * time/8), 50 * np.sin(2*np.pi * time/4)])

        # Crawlers that went out on the right get reset to the left
        for i in range(len(self.offsets)):
            if self.offsets[i,0] > self.width:
                self.offsets[i,0] -= self.n_x * 450


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        p = hermite(beat_progress)

        # Polygons for group 0
        x0 = (1-p) * self.xs + p * self.xl
        y0 = (1-p) * self.ys + p * self.yl
        polys0 = np.array([[[x0[-i], y0[-i]], [x0[-i], y0[-i] + self.h], [x0[-i-1], y0[-i-1] + self.h], [x0[-i-1], y0[-i-1]]] for i in range(1, len(self.xs))])

        # Polygons for group 1
        x1 = p * self.xs + (1-p) * self.xl + p * 140 * self.scaling
        y1 = p * self.ys + (1-p) * self.yl
        polys1 = np.array([[[x1[-i], y1[-i]], [x1[-i], y1[-i] + self.h], [x1[-i-1], y1[-i-1] + self.h], [x1[-i-1], y1[-i-1]]] for i in range(1, len(self.xs))])

        # Draw all polygons at respective offsets
        screen.lock()
        for i in range(len(self.offsets)):
            polys = polys0 if self.groups[i] == 0 else polys1
            hue_shift = ((1-p) * 0.1) if self.groups[i] == 0 else (p * 0.1)
            for poly in polys:
                poly = poly + self.offsets[i]
                # Mirror x coordinates for odd rows
                if (i//self.n_x)%2 == 1:
                    poly[:,0] = self.width - poly[:,0]
                if i in self.highlights:
                    fill = hls_to_rgb(self.hues[i] + hue_shift, 0.01, 1)
                    border = hls_to_rgb(self.hues[i] + hue_shift, 0.8, 1)
                else:
                    fill = np.zeros(3)
                    border = hls_to_rgb(self.hues[i] + hue_shift, 0.3, 0.8)
                poly = rotate_around(poly, self.tilt, self.center) + self.sway
                pygame.draw.polygon(screen, fill*brightness, poly)
                pygame.draw.aalines(screen, border*brightness, True, poly)
        screen.unlock()
