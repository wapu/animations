import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from colors import *


def scale(poly, factor):
    center = np.mean(poly, axis=0)
    return center + factor * (poly - center)

def rotate(poly, angle):
    center = np.mean(poly, axis=0)
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return center + np.matmul(poly - center, r)

def scale_around(poly, factor, anchor):
    return anchor + factor * (poly - anchor)

def rotate_around(poly, angle, anchor):
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return anchor + np.matmul(poly - anchor, r)



class Welde():

    def __init__(self, width, height):
        self.bottle = np.array([[135.77, 261.486], [124.093, 266.119], [105.338, 267.733], [85.1963, 266.298], [72.7904, 261.498], [69.2709, 257.636], [67.5232, 252.541], [67.5012, 166.062], [71.423, 148.625], [73.4239, 144.056], [76.7453, 136.182], [77.6332, 130.025], [76.375, 120.884], [75.1333, 111.324], [75.9431, 105.438], [79.7017, 95.656], [84.0295, 83.5961], [83.2053, 72.2689], [82.0968, 64.749], [83.0562, 57.3132], [85.7886, 47.8692], [89.5015, 28.5997], [88.5961, 24.7289], [88.2693, 21.6277], [89.1371, 18.2381], [90.9724, 16.3368], [103.524, 14.7899], [115.465, 15.9071], [117.318, 17.0324], [118.409, 18.7572], [119.146, 22.9363], [118.706, 24.7456], [117.896, 28.6117], [119.562, 40.4679], [124.728, 59.7414], [129.306, 75.6615], [130.385, 86.0921], [128.588, 97.0151], [126.803, 109.381], [128.485, 119.122], [132.655, 128.727], [138.533, 142.916], [141.202, 155.937], [141.209, 252.391], [139.395, 257.556], [135.77, 261.486], [135.77, 261.486]]
        )
        self.bottle -= self.bottle.mean(axis=0)
        self.bottle *= 0.5

        self.center = np.array([width/2, height/2])
        self.bottle += self.center

        self.n_rings = 6

        self.reset()


    def reset(self):
        self.intensity = 0
        self.angular_offset = 0
        self.amp = 0.15 * np.pi
        self.bounce_amps = np.ones(self.n_rings) * 5


    def event(self, num):
        match num:
            case 0:
                self.angular_offset = (self.angular_offset + np.pi) % (2*np.pi)


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        pass


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)
        if self.intensity == 0:
            target_amp = 0.1 * np.pi
        else:
            target_amp = 0.25 * np.pi
        self.amp = 0.8 * self.amp + 0.2 * target_amp

        self.rings = []
        for r in range(self.n_rings, 0, -1):
            ring = []
            dir =  1 if (r%2 == 0) else -1
            speed = 0.05*t * (0.5 + 3*(self.n_rings - r)/self.n_rings)
            size = 1 + (r-1) * 0.5
            radius = 130 * r - 30
            if self.intensity == 0:
                target_bounce = 5
            elif self.intensity == 1:
                target_bounce = 20
            elif self.intensity >= 2:
                target_bounce = 40 * size
            self.bounce_amps[r-1] = 0.8 * self.bounce_amps[r-1] + 0.2 * target_bounce

            n_bottles = r + 7
            for b in range(n_bottles):
                bottle = self.bottle + np.array([0, -(radius + self.bounce_amps[r-1] * beat_cos)])
                bottle = rotate_around(bottle, 2*np.pi * (b/n_bottles + (r%2)/(2*n_bottles) + speed * dir), self.center)
                bottle = rotate(bottle, self.amp * np.sin(2*np.pi * measure_progress) * dir + self.angular_offset)
                bottle = scale(bottle, size)
                ring.append(bottle)
            self.rings.append(ring)


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        screen.lock()

        for i, ring in enumerate(self.rings):
            h = i/6 + 0.3 * t
            l = 0.1 + 0.4 * (i+1) / (self.n_rings)
            s = 0.25 + 0.5 * (i+1) / (self.n_rings)
            for bottle in ring:
                if self.intensity >= 3:
                    pygame.draw.aalines(screen, hls_to_rgb(h, l * beat_cos * brightness, s), True, scale(bottle, 3))
                    pygame.draw.aalines(screen, hls_to_rgb(h, l * beat_cos * brightness, s), True, scale(bottle, 2))
                    pygame.draw.aalines(screen, hls_to_rgb(h, l * beat_cos * brightness, s), True, scale(bottle, 1.5))
                pygame.draw.polygon(screen, hls_to_rgb(h, l * brightness, s), bottle, width=4 + i//3)

        for i, ring in enumerate(self.rings):
            for bottle in ring:
                pygame.draw.polygon(screen, (0,0,0), bottle, width=0)

        screen.unlock()
