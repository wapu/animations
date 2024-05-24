import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

from colors import *



def spiral_in(points, center, factor, progress=1):
    angle = progress * np.pi/2
    factor = 1 + (factor - 1) * progress
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return center + np.matmul(points - center, r) / factor

def spiral_out(points, center, factor, progress=1):
    angle = progress * -np.pi/2
    factor = 1 + (factor - 1) * progress
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return center + factor * np.matmul(points - center, r)

def scale_around(poly, factor, center):
    return center + factor * (poly - center)

def rotate_around(poly, angle, center):
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return center + np.matmul(poly - center, r)

def hermite(val):
    return 3*val*val - 2*val*val*val



class Tower():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])

        self.n_stages = 6

        # Coordinates for tower and tip
        tower = np.array([[69,151.841], [85.5842,151.841], [86.8222,151.881], [88.119,151.608], [89.6448,150.853], [91.0994,149.528], [92.2566,147.843], [93.0606,146.023], [93.4556,144.295], [93.7261,135.258], [93.8247,127.829], [93.9669,126.841], [93.8019,125.908], [93.1749,124.95], [92.023,124.044], [90.6065,123.163], [88.0069,121.655], [87.172,120.945], [86.6339,120.059], [86.5358,119.576], [86.5837,119.08], [86.8016,118.583], [87.2132,118.095], [87.9632,117.603], [89.0583,117.114], [91.7969,116.062], [98.7783,113.431], [100.125,112.935], [101.159,112.309], [101.576,111.901], [101.855,111.428], [101.909,110.851], [101.72,110.137], [100.801,108.339], [99.479,106.124], [98.1337,103.576], [97.5164,101.845], [96.9524,99.4193], [96.5275,96.4251], [96.3279,92.9876], [96.4395,89.2321], [96.9483,85.284], [97.9405,81.2687], [98.6447,79.275], [99.502,77.3116], [101.111,74.3628], [102.933,71.6276], [104.868,69.1379], [106.815,66.9255], [110.344,63.4594], [112.718,61.4835], [115.79,59.2749]])
        second_half = tower[::-1]
        mirror = np.max(tower[:,0])
        second_half = mirror + (second_half - mirror) * np.array([-1,1])
        self.tower = np.concatenate([tower, second_half], axis=0)
        self.tower_with_tip = np.concatenate([tower, [[115.79, 14.5888]], second_half], axis=0)
        tip = np.vstack([np.zeros(len(self.tower_with_tip)) + 115.79, np.linspace(59.2749, 14.5888, len(self.tower_with_tip))]).T
        self.tip = tip + self.center - self.tower.mean(axis=0)
        self.tower_with_tip += self.center - self.tower.mean(axis=0)
        self.tower += self.center - self.tower.mean(axis=0)

        # Scaling factor for spiral
        tower_width = self.tower[-1,0] - self.tower[0,0]
        self.f = tower_width / (tip[0,1] - tip[-1,1])

        # Fit coordinates for exact recursive overlap
        a1, a2 = self.tip[-1] - self.center
        c1 = -tower_width/2
        c2 = self.tower[0,1] - height/2
        o2 = (-self.f*a1 - self.f*self.f*a2 + self.f*c1 - c2) / (1 + self.f*self.f)
        o1 = -(self.f*a2 - c1 + self.f*o2)
        offset = np.array([o1, o2])
        self.tower += offset
        self.tower_with_tip += offset
        self.tip += offset

        # Initial scale
        init_scale = 0.5
        self.tower = scale_around(self.tower, init_scale, self.center)
        self.tower_with_tip = scale_around(self.tower_with_tip, init_scale, self.center)
        self.tip = scale_around(self.tip, init_scale, self.center)

        self.blend_mode = 0

        self.reset()


    def reset(self):
        self.hues = [(0.5 + 0.075 * i) % 1 for i in range(self.n_stages + 1)]
        self.progress = 0
        self.rotation = 0

        self.last_update = time()


    def event(self):
        self.blend_mode = 1 - self.blend_mode


    def clear_frame(self, screen):
        if self.blend_mode == 0:
            screen.fill([150]*3, special_flags=pygame.BLEND_MULT)
        else:
            screen.fill([240]*3, special_flags=pygame.BLEND_MULT)


    def update(self, bpm, last_beat, delta_t):
        # Progress transformations
        self.progress = np.minimum(1, ((time() - last_beat) % (60/bpm)) * bpm / 60)
        self.rotation += 0.0008 * bpm
        for i in range(len(self.hues)):
            self.hues[i] += 0.0001 * bpm

        # Limit FPS to BPM for everything below
        if time() - last_beat < 60/bpm:
            self.last_update = last_beat
            return
        if time() - self.last_update < 60/bpm:
            return
        self.last_update += 60/bpm

        # Add new hue when new iteration spawns
        self.hues = [(self.hues[0] - 0.075) % 1,] + self.hues[:-1]


    def draw(self, screen, bpm, last_beat, brightness):
        tower = spiral_out(self.tower, self.center, self.f, self.progress)

        tip = (1 - hermite(self.progress)) * self.tip + hermite(self.progress) * spiral_in(self.tower_with_tip, self.center, self.f)
        tip = spiral_out(tip, self.center, self.f, self.progress)

        pygame.draw.aalines(screen, hls_to_rgb(self.hues[0], 0.3*brightness), False, rotate_around(tip, self.rotation, self.center))
        pygame.draw.aalines(screen, hls_to_rgb(self.hues[0], 0.3*brightness), False, rotate_around(tip, self.rotation + np.pi*2/3, self.center))
        pygame.draw.aalines(screen, hls_to_rgb(self.hues[0], 0.3*brightness), False, rotate_around(tip, self.rotation + np.pi*4/3, self.center))

        for i in range(self.n_stages):
            pygame.draw.lines(screen, hls_to_rgb(self.hues[i+1], 0.3*brightness), False, rotate_around(tower, self.rotation, self.center), width=i+1)
            pygame.draw.lines(screen, hls_to_rgb(self.hues[i+1], 0.3*brightness), False, rotate_around(tower, self.rotation + np.pi*2/3, self.center), width=i+1)
            pygame.draw.lines(screen, hls_to_rgb(self.hues[i+1], 0.3*brightness), False, rotate_around(tower, self.rotation + np.pi*4/3, self.center), width=i+1)

            tower = spiral_out(tower, self.center, self.f, progress=1)
            tip = spiral_out(tip, self.center, self.f, progress=1)
