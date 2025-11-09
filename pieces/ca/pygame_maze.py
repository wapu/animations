import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np
import imageio.v3 as iio

from time import time

from colors import *



def ravel(x, y, shape):
    return x + y*shape[0]

def unravel(i, shape):
    x = i % shape[0]
    y = (i-x) // shape[0]
    return x, y

def hue_from_time(interval=20.0):
    return (time() % interval) / interval



class Maze():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])

        # Constants
        self.density = 0.6

        # Create grid
        d = 10
        mesh = np.mgrid[25:width-15:d, 25:height-5:d]
        self.mesh = np.transpose(mesh, (1,2,0))
        self.n_egdes = self.mesh.shape[0] * self.mesh.shape[1]

        # Set up diagonals
        self.line_l = np.array([[-d/2, -d/2], [d/2, d/2]])
        self.line_r = np.array([[d/2, -d/2], [-d/2, d/2]])
        self.slant_right = (np.mgrid[0:self.mesh.shape[0], 0:self.mesh.shape[1]].sum(axis=0) % 2) == 0
        self.slant_right = self.slant_right.reshape(-1, order='F')

        # Mark forbidden areas
        ca = iio.imread('data/CA_188x104.png')
        self.forbidden = (ca[:,:,0] > 0).flatten()
        # lo = iio.imread('data/LO_188x104.png')
        # self.forbidden = (lo[:,:,0] > 0).flatten()

        # Set up diagonal neighborhood graph
        self.neighbors = [[] for i in range(self.n_egdes)]
        for x in range(self.mesh.shape[0]):
            for y in range(self.mesh.shape[1]):
                i_neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
                if (x+y)%2 == 0: # slanted right
                    i_neighbors.extend([(x-1, y+1), (x+1, y-1)])
                else: # slanted left
                    i_neighbors.extend([(x-1, y-1), (x+1, y+1)])

                for j,k in i_neighbors:
                    if 0 <= j < self.mesh.shape[0] and 0 <= k < self.mesh.shape[1]:
                        self.neighbors[ravel(x, y, self.mesh.shape)].append(ravel(j, k, self.mesh.shape))

        self.mesh = self.mesh.reshape((-1,2), order='F')

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0
        self.mode = 0
        self.max_value = 200
        self.values = np.zeros(self.n_egdes)
        self.hues = np.zeros(self.n_egdes)
        self.frontier = []
        self.new_frontier = []

        dists = np.linalg.norm(np.array([1, 1.6]) * (self.center - self.mesh), axis=-1)
        for i in range(self.n_egdes):
            if 0.75 * self.center[0] < dists[i] + 40*np.random.randn() < 0.752 * self.center[0]:
                self.frontier.extend(self.neighbors[i])


    def event(self, num):
        match num:
            case 0:
                self.mode = 1 - self.mode
            case 1:
                self.values -= 0.1 * self.max_value
            case 2:
                self.seed()


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def seed(self):
        # Place random new edge
        i = np.random.randint(self.n_egdes)
        while self.forbidden[i]:
            i = np.random.randint(self.n_egdes)
        if self.values[i] < self.max_value/3:
            self.values[i] = self.max_value
            self.hues[i] = hue_from_time()
            self.frontier.extend(self.neighbors[i])


    def beat(self, t):
        # Spawn new seeds if frontier almost empty and at random
        if len(self.frontier) < 5 or np.random.rand() < 0.05:
            self.seed()

        # Expand frontier
        hue = hue_from_time()
        self.new_frontier = []
        for i in self.frontier:
            for n in self.neighbors[i]:
                if self.values[n] < self.max_value/3 and not self.forbidden[n]:
                    self.values[n] = self.max_value
                    if np.random.rand() < self.density:
                        self.new_frontier.append(n)
                        self.hues[n] = hue
                    else:
                        self.hues[n] = np.nan
        self.frontier = self.new_frontier


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        self.values -= bpm/250
        self.hues = (self.hues + (bpm/60) * 0.001) % 1.0


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi/2)

        vals = np.arange(self.max_value + 1)
        l = 0.5 * (vals/self.max_value)**1.2
        l += 0.2 * beat_cos * np.exp(-(self.max_value - vals)**2 / 50**2)
        if self.intensity >= 2:
            for i in range(4):
                wave_age = measure_progress - (int(measure_progress*4) - i) / 4
                l += (0.7 - 0.6 * wave_age) * np.exp(-((self.max_value * (1 - wave_age)) - vals)**2 / 20)
        l = np.maximum(0, np.minimum(1, l))

        if self.intensity >= 3:
            scale = 0.4 + 0.6 * beat_cos
        else:
            scale = 0.9
        mesh_r = self.mesh[:,None,:] + scale * self.line_r
        mesh_l = self.mesh[:,None,:] + scale * self.line_l

        screen.lock()
        if self.intensity == 1:
            for i in self.new_frontier:
                pygame.draw.circle(screen, hls_to_rgb(self.hues[i], 0.1 * (1 - beat_progress)), self.mesh[i], radius=15 * (1 - beat_progress))
                pygame.draw.circle(screen, [0,0,0], self.mesh[i], radius=13 * (1 - beat_progress))
        for i in range(self.n_egdes):
            if self.values[i] > 0 and not np.isnan(self.hues[i]):
                color = hls_to_rgb(self.hues[i], l[int(self.values[i])] * brightness)
                if self.mode == 0:
                    if self.slant_right[i]:
                        pygame.draw.line(screen, color, *mesh_r[i])
                    else:
                        pygame.draw.line(screen, color, *mesh_l[i])
                else:
                    if self.intensity >= 3:
                        pygame.draw.circle(screen, color, self.mesh[i], radius=1 + 1.5 * beat_cos)
                    else:
                        pygame.draw.circle(screen, color, self.mesh[i], radius=2)
        screen.unlock()
