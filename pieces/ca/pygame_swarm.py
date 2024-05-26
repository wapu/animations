import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np
import imageio.v3 as iio

from scipy.spatial import distance_matrix
from scipy.ndimage import distance_transform_edt
from glob import glob
from os.path import isfile
from time import time

from colors import *



def prepare_guide(image_filename, overwrite=False):
    np_name = f'swarm_{image_filename.split(".")[0]}.npy'
    if isfile('data/' + np_name) and not overwrite:
        return

    try:
        light_map = iio.imread('data/' + image_filename)[:,:,0].T
    except:
        return

    edt, inds = distance_transform_edt(light_map < 1, return_indices=True)
    inds = inds.transpose(1,2,0)
    guide = inds - np.mgrid[0:1920,0:1080].transpose(1,2,0)

    norm = np.linalg.norm(guide, axis=-1)
    with np.errstate(invalid='ignore'):
        guide = guide / norm[:,:,None]
    guide[norm == 0] = 0

    np.save('data/' + np_name, guide.astype(np.float16))



class Swarm():

    def __init__(self, width, height):
        self.WH = np.array([width, height])

        # Set up guides
        prepare_guide('smiley.png')
        prepare_guide('heart.png')
        prepare_guide('weed.png')
        prepare_guide('peace.png')
        prepare_guide('infinity.png')
        prepare_guide('yinyang.png')
        prepare_guide('eyes.png')
        prepare_guide('triskele.png')

        self.guides = []
        for file in glob('data/swarm_*.npy'):
            self.guides.append(np.load(file))
        if len(self.guides) == 0:
            self.guides.append(np.zeros((width, height, 2)))

        # Constants
        self.n = 200
        self.dist = 30#150
        self.tradeoff = 0.95#0.8
        self.surface_pull = 0.3#0.05
        self.momentum = 0.2#0.7
        self.momentum_tmp = 0
        self.v_max = 5
        self.v_max_tmp = 0

        self.coords = np.random.rand(self.n, 2) * self.WH
        self.vs = np.random.randn(self.n, 2) * 2

        self.reset()


    def reset(self):
        self.intensity = 0
        self.guide = self.guides[np.random.randint(len(self.guides))]


    def event(self, num):
        to_center = self.WH/2 - self.coords
        to_center = to_center / np.linalg.norm(to_center)
        self.vs = -50 * to_center
        self.momentum_tmp = 1 - self.momentum
        self.v_max_tmp = 20


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        # Move
        self.coords = np.mod(self.coords + self.vs, self.WH)

        # Swarm contribution
        vs_new = np.zeros_like(self.vs)
        self.D = distance_matrix(self.coords, self.coords) + 1e-08
        directions = self.coords[None,:,:] - self.coords[:,None,:]
        normalized = directions / self.D[:,:,None]
        for i in range(self.n):
            normalized[i,i] = 0
        contributions = np.where(self.D < self.dist,
                                 -np.cos(self.D*np.pi/self.dist) - self.tradeoff,
                                 (1 - self.tradeoff) * np.exp(-(self.D-self.dist)**2 / (10*self.dist)))
        vs_new += 1 * np.sum(contributions[:,:,None] * normalized, axis=1)

        # Surface contribution
        vs_new += self.surface_pull * self.guide[tuple(self.coords.astype(int).T)]

        # Update velocities
        self.vs = self.vs + (1 - (self.momentum + self.momentum_tmp)) * vs_new
        v_norm = np.linalg.norm(self.vs, axis=-1)
        self.vs = np.where((v_norm < self.v_max + self.v_max_tmp)[:,None], self.vs, self.vs / v_norm[:,None])

        self.momentum_tmp *= 0.98
        self.v_max_tmp *= 0.98


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        hue_shift = measure_progress
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        # Lines
        # D_rbf = np.exp(-(self.D / (self.dist/4))**2)
        D_rbf = np.exp(-(self.D / (0.8 * self.dist))**2)
        for i in range(self.n):
            for j in range(i+1, self.n):
                # if self.D[i,j] < self.dist/2:
                if self.D[i,j] < 2*self.dist:
                    h = (D_rbf[i,j] + hue_shift) % 1
                    l = 0.6 * D_rbf[i,j] + 0.01 * beat_cos
                    pygame.draw.aaline(screen, hls_to_rgb(h,l*brightness,1.0), self.coords[i], self.coords[j])

        # Points
        color = [255*beat_cos*brightness]*3
        for c in self.coords:
            # pygame.draw.circle(screen, color, c, radius=2)
            pygame.draw.circle(screen, color, c, radius=1)
