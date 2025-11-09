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



class ZweiZwei():

    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.center = np.array([width/2, height/2])

        self.two = np.array([[120.533, 69.9777], [107.848, 69.9777], [108.915, 68.4887], [110.165, 67.2368], [112.891, 64.9704], [115.591, 62.6901], [118.038, 60.3012], [119.036, 58.9908], [119.814, 57.5631], [120.318, 55.9879], [120.498, 54.2352], [120.34, 52.6792], [119.884, 51.2879], [119.158, 50.0745], [118.19, 49.0522], [117.009, 48.2341], [115.643, 47.6334], [114.12, 47.2634], [112.469, 47.1371], [110.712, 47.2805], [109.109, 47.6977], [107.684, 48.3694], [106.462, 49.2762], [105.469, 50.3988], [104.728, 51.7178], [104.265, 53.2139], [104.106, 54.8678], [107.268, 54.8678], [107.374, 53.766], [107.657, 52.8072], [108.105, 51.9924], [108.707, 51.3231], [109.449, 50.8003], [110.32, 50.4254], [111.307, 50.1995], [112.399, 50.1239], [114.319, 50.3946], [115.157, 50.7262], [115.888, 51.1825], [116.492, 51.7591], [116.947, 52.4514], [117.235, 53.2548], [117.336, 54.165], [117.182, 55.517], [116.743, 56.7584], [116.055, 57.9171], [115.153, 59.0208], [112.844, 61.1745], [110.097, 63.4418], [107.496, 65.8118], [105.406, 68.2229], [104.611, 69.428], [104.014, 70.6242], [103.639, 71.8052], [103.508, 72.9646], [120.533, 72.9646]]
        )
        self.dot = np.array([[95.6898, 72.9646], [99.2916, 72.9646], [99.2916, 69.3628], [95.6898, 69.3628]])

        self.right = 25 * (self.two - self.dot.mean(axis=0) + np.array([-8.2, 12]))
        self.left = self.right * np.array([-1,1])
        self.middle = 21 * (rotate(self.dot, np.pi/4) - self.dot.mean(axis=0) + np.array([0, 14.5]))

        self.left += self.center
        self.right += self.center
        self.middle += self.center

        self.bg_scale = 30
        self.font = pygame.font.SysFont('Loma', self.bg_scale)
        self.bg = self.font.render('2', True, (5,5,5))
        self.bg_dot = self.font.render('.', True, (5,5,5))

        self.reset()


    def reset(self):
        self.intensity = 0
        self.hue = 0
        self.hue_target = 0

        self.offset_two = np.array([190, 0])
        self.offset_dot = np.array([0, 50])
        self.bounce = np.array([0, -60])

        self.slide_factor = 0
        self.slide_factor_target = 0
        self.bounce_factor = 0.5
        self.bounce_factor_target = 0.5
        self.bg_bounce_factor = 0
        self.bg_bounce_factor_target = 0


    def event(self, num):
        match num:
            case 0:
                pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        self.hue_target = self.hue_target + 1/3

        if self.intensity == 0:
            self.slide_factor_target = 0
            self.bounce_factor_target = 0.5
            self.bg_bounce_factor_target = 0
        elif self.intensity == 1:
            self.slide_factor_target = 0.25
            self.bounce_factor_target = 0.75
            self.bg_bounce_factor_target = 0
        elif self.intensity == 2:
            self.slide_factor_target = 1
            self.bounce_factor_target = 1.125
            self.bg_bounce_factor_target = 0.75
        elif self.intensity == 3:
            self.slide_factor_target = 1
            self.bounce_factor_target = 1.5
            self.bg_bounce_factor_target = 1.5

    def measure(self, t):
        pass



    def update(self, t, beat_progress, measure_progress, bpm):
        beat_sin = 0.5 - 0.5*np.sin(2*np.pi * beat_progress - np.pi/2)

        self.slide_factor = 0.7 * self.slide_factor + 0.3 * self.slide_factor_target
        self.bounce_factor = 0.7 * self.bounce_factor + 0.3 * self.bounce_factor_target
        self.bg_bounce_factor = 0.7 * self.bg_bounce_factor + 0.3 * self.bg_bounce_factor_target
        self.hue = 0.5 * self.hue + 0.5 * self.hue_target

        self.bg = self.font.render('2', True, hls_to_rgb((self.hue - 0.1) % 1, 0.1, 0.5))
        self.bg_dot = self.font.render('.', True, hls_to_rgb((self.hue - 0.1) % 1, 0.1 + 0.1 * self.intensity * beat_sin**2, 0.5))


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)
        beat_cos_ = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi)
        measure_cos = 0.5 - 0.5*np.cos(2*np.pi * ((2 * measure_progress)%1))

        s = 1 + 0.15 * beat_cos_**2 * self.bounce_factor
        bounce = beat_cos**2 * self.bounce * self.bounce_factor
        slide = 1 - measure_cos * self.slide_factor
        left = scale_around(self.left - slide * self.offset_two, s, self.center) + bounce
        left = rotate(left, 0.02 * np.pi * (1 - measure_cos))
        right = scale_around(self.right + slide * self.offset_two, s, self.center) + bounce
        right = rotate(right, -0.02 * np.pi * (1 - measure_cos))
        middle = scale_around(self.middle + slide * self.offset_dot, s, self.center) + bounce

        for x in range(-2*self.bg_scale, self.W + 2*self.bg_scale, self.bg_scale):
            for y in range(-2*self.bg_scale, self.H + 2*self.bg_scale, self.bg_scale):
                flip_x = (((x + y)//self.bg_scale) % 2 == 1) != (measure_progress > 0.5)
                x_ = 2 * self.bg_scale * measure_progress
                x_ = x + x_ * (1 if (y//self.bg_scale)%2 == 0 else -1)
                y_ = y - self.bg_scale * beat_cos * self.bg_bounce_factor
                screen.blit(pygame.transform.flip(self.bg, flip_x, False), (x_, y_))
                screen.blit(self.bg_dot, (x_ + 0.65 * self.bg_scale, y_))

        screen.lock()

        h = self.hue % 1
        l = (0.4 - 0.2 * slide + 0.2 * beat_cos)
        s = 0.5
        for shape in [left, right, middle]:
            pygame.draw.polygon(screen, hls_to_rgb(h, l * brightness, s), shape, width=5)

        for shape in [left, right, middle]:
            pygame.draw.polygon(screen, (0,0,0), shape, width=0)

        screen.unlock()
