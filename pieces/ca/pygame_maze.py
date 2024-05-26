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

        # Create diagonal grid
        d = 10
        mesh = np.mgrid[25:width-15:d, 25:height-5:d]
        self.mesh = np.transpose(mesh, (1,2,0))
        self.n_egdes = self.mesh.shape[0] * self.mesh.shape[1]
        starts_l = self.mesh + np.array([-d/2, -d/2])
        finish_l = self.mesh + np.array([d/2, d/2])
        starts_r = self.mesh + np.array([d/2, -d/2])
        finish_r = self.mesh + np.array([-d/2, d/2])

        self.coords = np.zeros((self.n_egdes, 4))
        for x in range(self.mesh.shape[0]):
            for y in range(self.mesh.shape[1]):
                i = ravel(x, y, self.mesh.shape)
                if (x+y)%2 == 0: # slanted right
                    self.coords[i, :2] = starts_r[x,y]
                    self.coords[i, 2:] = finish_r[x,y]
                else: # slanted left
                    self.coords[i, :2] = starts_l[x,y]
                    self.coords[i, 2:] = finish_l[x,y]

        # Mark forbidden areas
        ca = iio.imread('data/CA_188x104.png')
        self.forbidden = (ca[:,:,0] > 0).flatten()

        # Set up neighborhood graph
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

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0
        self.mode = 0
        self.max_value = 200
        self.values = np.zeros(self.n_egdes)
        self.hues = np.zeros(self.n_egdes)
        self.frontier = []

        dists = np.linalg.norm(np.array([1, 1.6]) * (self.center - (self.coords[:,:2] + self.coords[:,2:])/2), axis=-1)
        for i in range(self.n_egdes):
            if 0.75 * self.center[0] < dists[i] + 40*np.random.randn() < 0.752 * self.center[0]:
                self.frontier.extend(self.neighbors[i])


    def event(self, num):
        self.mode = 1 - self.mode


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
        new_frontier = []
        for i in self.frontier:
            for n in self.neighbors[i]:
                if self.values[n] < self.max_value/3 and not self.forbidden[n]:
                    self.values[n] = self.max_value
                    if np.random.rand() < self.density:
                        new_frontier.append(n)
                        self.hues[n] = hue
                    else:
                        self.hues[n] = np.nan
        self.frontier = new_frontier


    def update(self, t, beat_progress, measure_progress, bpm):
        self.values -= bpm/250
        self.hues = (self.hues + (bpm/60) * 0.001) % 1.0


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)
        vals = np.arange(self.max_value + 1)
        l = 0.6 * (vals/self.max_value)**1.2 + 0.4 * beat_cos * np.exp(-(self.max_value - vals)**2 / 20)

        screen.lock()
        for i in range(self.n_egdes):
            if self.values[i] > 0 and not np.isnan(self.hues[i]):
                color = hls_to_rgb(self.hues[i], l[int(self.values[i])] * brightness)
                if self.mode == 0:
                    pygame.draw.line(screen, color, self.coords[i,:2], self.coords[i,2:])
                else:
                    pygame.draw.circle(screen, color, (self.coords[i,:2] + self.coords[i,2:])/2, radius=2)
        screen.unlock()
