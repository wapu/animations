import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np
import imageio.v3 as iio

from scipy.spatial import distance_matrix
from scipy.ndimage import gaussian_filter
from glob import glob
from os.path import isfile
from time import time

from colors import *



def de_boor_np(t, points, degree=4, i=None, n=None):
    if i is None: i = np.round(t).astype(int)
    if n is None: n = degree

    if degree == 0:
        return points[i % len(points)]
    alpha = ((t - i) / (n + 1 - degree))[:,None]
    return (1 - alpha) * de_boor_np(t, points, degree-1, i=i-1, n=n) + alpha * de_boor_np(t, points, degree-1, i=i, n=n)

def rotate_around(points, angle, anchor):
    c = np.cos(angle)
    s = np.sin(angle)
    r = np.array([[c, -s], [s, c]])
    return anchor + np.matmul(points - anchor, r)

def vortex_around(points, angles, anchor):
    c = np.cos(angles)
    s = np.sin(angles)
    r = np.array([[c, -s], [s, c]]).transpose(2,3,0,1)
    offsets = (points - anchor)[:,:,None,:]
    return anchor + np.matmul(offsets, r)[:,:,0,:]



class Lines():

    def __init__(self, width, height):
        self.WH = np.array([width, height])
        self.center = self.WH / 2

        # Load BG image
        try:
            # self.bg = iio.imread('data/trashy_trance_soft.png')[:,:,0].T / 255
            self.bg = iio.imread('data/kürbis.png')[:,:,0].T / 255
            self.bg = self.bg**4
        except:
            self.bg = np.zeros(width, height)

        self.baselines = np.mgrid[120:width-120:7, 110:height-90:20]
        self.baselines = np.transpose(self.baselines, (2,1,0)).astype(float)

        self.reset()


    def reset(self):
        self.intensity = 0

        self.lines = np.array(self.baselines)
        self.x_offset_size = 0
        self.x_offset_size_target = 10
        self.rotate_lines = 0
        self.rotate_lines_target = 0
        self.rotate_bg = 0
        self.rotate_bg_target = 0
        self.x_offsets = np.zeros((self.baselines.shape[0], 1))
        self.noise = np.zeros_like(self.baselines)
        self.highlights = np.zeros(self.baselines.shape[0])
        self.i_highlight = -1
        self.beat_counter = 0

        # self.vortex_center = np.array(self.center)
        # self.vortex_size = 300

    def event(self, num):
        match num:
            case 1:
                pass
            case 2:
                pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        self.beat_counter += 1

        self.x_offsets = self.x_offset_size * np.random.randn(self.baselines.shape[0], 1)

        self.noise = 3 * np.random.randn(*self.baselines.shape)**3
        self.noise[:,:,0] = 0
        self.noise = gaussian_filter(self.noise, (1,4,0), mode='constant')

        if self.intensity == 3:
            self.i_highlight = np.random.randint(len(self.highlights))
            if 0 <= self.i_highlight < len(self.highlights):
                self.highlights[self.i_highlight] = 1.0


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = (0.5 + 0.5*np.cos(2*np.pi * beat_progress))
        measure_cos = (0.5 + 0.5*np.cos(2*np.pi * measure_progress))
        cos = np.cos(2*np.pi * measure_progress)
        sin = np.sin(2*np.pi * beat_progress)

        # Smooth transition for intensity based parameters
        self.x_offset_size_target = 10 + self.intensity * 12
        self.x_offset_size = 0.8 * self.x_offset_size + 0.2 * self.x_offset_size_target

        if self.intensity >= 1:
            self.rotate_lines_target = 0.01 * np.pi
        else:
            self.rotate_lines_target = 0
        self.rotate_lines = 0.75 * self.rotate_lines + 0.25 * self.rotate_lines_target

        if self.intensity >= 2:
            self.rotate_bg_target = 0.02 * np.pi
        else:
            self.rotate_bg_target = 0
        self.rotate_bg = 0.75 * self.rotate_bg + 0.25 * self.rotate_bg_target

        # Decay beatwise changes
        self.x_offsets *= 0.95
        self.highlights *= 0.8

        # Lines independently jump horizontally
        self.lines = np.array(self.baselines) + self.noise
        self.lines[:,:,0] += self.x_offsets

        # Lines spread with the beat
        self.lines[:,:,1] = self.lines[:,:,1] + (self.lines[:,:,1] - self.WH[1]/2) * (0.02 + self.intensity/20) * beat_cos

        # Rotate line grid around center
        self.lines = rotate_around(self.lines, self.rotate_lines * cos, self.center)

        # All points bounce vertically
        self.lines[:,:,1] += 5*sin * (self.intensity + 1)

        # # Update vortex
        # # self.vortex_center = (0.5 + 0.3 * cos) * self.WH
        # self.vortex_angle = 0.75 * np.pi * (0.25 + 0.75 * measure_cos)
        # self.vortex_size = 400 * (0.25 + 0.75 * measure_cos)

        # # Apply vortex
        # if self.intensity >= 3:
        #     dists = np.linalg.norm(self.vortex_center - self.lines, axis=-1)
        #     influence = np.exp(-(dists/self.vortex_size)**2)
        #     self.lines = vortex_around(self.lines, self.vortex_angle * influence, self.vortex_center)

        # Bump vertices depending on background image and beat
        coords = self.lines
        coords = rotate_around(self.lines, self.rotate_bg * cos, self.center)
        coords = np.minimum(self.WH - 1, np.maximum(0, coords)).round(0).astype(int)
        values = self.bg[coords[:,:,0], coords[:,:,1]]
        offset = np.array([0.4,-1]) * values[:,:,None]
        self.lines += (10 + 12 * (self.intensity + 1)) * offset * beat_cos

        # Smooth out the lines
        self.lines = [de_boor_np(np.arange(len(line)), line, 5)[5:] for line in self.lines]


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 + 0.5*np.cos(2*np.pi * beat_progress)

        # Lines
        screen.lock()
        for i in range(len(self.lines)):
            h = (1.5 * (i/len(self.lines)) - 0.5*t) % 1.0
            if self.intensity == 2:
                l_ = 0.25 if ((self.beat_counter + i) % 5 != 0) else 0.25 + 0.2 * beat_cos
            else:
                l_ = 0.3
            l = l_ + (1 - l_) * self.highlights[i]
            s = 0.75 + 0.25 * self.highlights[i]
            color = hls_to_rgb(h, l * brightness,s)
            if i == self.i_highlight and self.intensity == 3:
                pygame.draw.lines(screen, color, False, self.lines[i], width=3)
            else:
                pygame.draw.aalines(screen, color, False, self.lines[i])
        screen.unlock()
