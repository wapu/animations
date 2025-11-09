import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from colors import *
from scipy.spatial import distance_matrix
from scipy.linalg import norm



def hermite(x):
    return 3*x**2 - 2*x**3



class Metaballs():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])
        self.WH = np.array([width, height])
        self.aspect = width/height
        self.aspect_array = np.array([self.aspect, 1.0])

        self.n_balls = 12
        self.mode = 0

        # Create grid
        self.grid_size = 12
        mesh = np.mgrid[25:width-15:self.grid_size, 25:height-5:self.grid_size]
        self.mesh = np.transpose(mesh, (1,2,0))
        self.mesh_w, self.mesh_h, _ = self.mesh.shape
        self.canvas = np.zeros((self.mesh_w, self.mesh_h, 3))
        mesh_aspect = self.center + (self.mesh - self.center) / self.aspect_array
        self.radial_dist = distance_matrix(mesh_aspect.reshape(-1,2), self.center[None,:]).reshape(self.mesh_w, self.mesh_h)

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0
        self.hues = np.linspace(0, 1, self.n_balls, endpoint=False)
        self.radii = 7 + 8 * np.random.rand(self.n_balls)
        self.coords = self.WH * np.random.rand(self.n_balls, 2)
        self.vs = np.random.randn(self.n_balls, 2) * 10


    def event(self, num):
        match num:
            case 0:
                self.mode = (self.mode + 1) % 2


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        pass


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        # Update colors
        self.hues = (self.hues + (bpm/60) * 0.001) % 1.0

        # Update directions
        for i in range(self.n_balls):
            if self.coords[i,0] < 0.1 * self.WH[0]:
                self.vs[i,0] += 1
            if self.coords[i,0] > 0.9 * self.WH[0]:
                self.vs[i,0] -= 1
            if self.coords[i,1] < 0.1 * self.WH[1]:
                self.vs[i,1] += 1
            if self.coords[i,1] > 0.9 * self.WH[1]:
                self.vs[i,1] -= 1
            self.vs[i] += 0.5 * np.random.randn(2)
            v_ = norm(self.vs[i])
            if v_ > 35:
                self.vs[i] = self.vs[i] * 35/v_
            if v_ < 15:
                self.vs[i] = self.vs[i] * 15/v_

        # Move
        self.coords = self.coords + (0.2 + 0.8 * hermite(beat_progress)) * self.vs

        # Calculate metaballs and their color contributions
        dist = distance_matrix(self.mesh.reshape(-1,2), self.coords).reshape(*self.mesh.shape[:-1], self.n_balls)
        dist /= self.grid_size - self.intensity/6 + 2*(1 - beat_cos) * self.intensity/3

        contributions = (self.radii/dist)[:,:,:,None]**2 * hls_to_rgb_array(self.hues)[None,None,:,:]
        self.canvas = contributions.sum(axis=2)

        max_channel = self.canvas.max(axis=-1, keepdims=True)
        mask = max_channel[:,:,0] > 255
        if self.mode == 0:
            self.canvas[mask] = 0
        elif self.mode == 1:
            self.canvas[mask] *= 255 / max_channel[mask]
            self.canvas[mask] *= 0.05
        self.canvas[~mask] = (200 - 50*beat_cos) * (self.canvas[~mask]/255)**(3 + beat_cos)


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos_all = (0.5 - 0.5*np.cos(2*np.pi * beat_progress))

        canvas_sum = self.canvas.sum(axis=-1)
        if self.mode == 0:
            beat_cos = (0.5 - 0.5*np.cos(2*np.pi * beat_progress - np.pi * self.radial_dist/100))**6
            r = 0.15 * self.grid_size + 0.3 * self.grid_size * beat_cos
        elif self.mode == 1:
            beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi * (canvas_sum**0.5 / 2 + 0.2*t))
            r = 0.05 * self.grid_size + 0.3 * self.grid_size * beat_cos

        screen.lock()

        mesh = self.center + (1 - 0.03 * beat_cos_all * self.intensity) * (self.mesh - self.center)
        for x in range(mesh.shape[0]):
            for y in range(mesh.shape[1]):
                if canvas_sum[x,y] > 5:
                    color = self.canvas[x,y]
                    pygame.draw.circle(screen, color * brightness, mesh[x,y], radius=r[x,y], width=1)

        screen.unlock()
