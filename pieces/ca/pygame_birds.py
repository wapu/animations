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



class Bird_1():

    def __init__(self, width, height):
        self.bird = [
            np.array([[5.8354688, -0.00046875], [25.638203, 7.7241406], [50.921406, 1.5405469], [5.8354688, -0.00046875]]),
            np.array([[51.206562, 2.6323437], [26.671406, 8.7436719], [32.388203, 14.403828], [37.239766, 13.790547], [44.745625, 17.222188], [51.206562, 2.6323437]]),
            np.array([[52.339375, 2.8667187], [45.919453, 17.897969], [55.190937, 21.606953], [61.630391, 16.995625], [52.339375, 2.8667187]]),
            np.array([[71.987813, 11.710469], [71.353047, 19.300313], [88.802266, 18.351094], [71.987813, 11.710469]]),
            np.array([[70.872578, 11.794453], [56.454609, 22.255391], [69.296406, 27.716328], [70.235859, 18.937031], [70.872578, 11.794453]]),
            np.array([[37.169453, 15.149922], [-0.00046875, 20.993672], [24.306172, 24.163594], [37.169453, 15.149922]]),
            np.array([[37.837422, 16.108906], [25.751484, 25.179219], [40.067891, 37.046406], [37.837422, 16.108906]]),
            np.array([[39.177266, 16.384297], [41.382344, 36.954609], [66.913594, 28.003438], [39.177266, 16.384297]]),
            np.array([[69.212422, 28.394063], [47.513203, 36.325703], [47.532734, 53.706562], [68.341328, 35.356953], [69.212422, 28.394063]]),
            np.array([[46.179219, 36.776875], [12.853047, 62.806172], [46.233906, 54.087422], [46.179219, 36.776875]]),
            np.array([[22.13625, 61.812031], [12.274922, 64.302266], [7.5307813, 78.690938], [22.13625, 61.812031]])
        ]
        self.bird = [8*poly + np.array([600, 200]) for poly in self.bird]

        self.center = np.mean([c for poly in self.bird for c in poly], axis=0)

        self.n_shadows = 30
        self.shadows = []
        for s in np.linspace(6, 1, self.n_shadows):
            self.shadows.append([scale(poly, s) for poly in self.bird])

        self.reset()


    def reset(self):
        self.intensity = 0
        self.burst = 0
        self.angle_phases = 2*np.pi * np.random.rand(len(self.bird))
        self.scale_phases = 2*np.pi * np.random.rand(len(self.bird))


    def event(self, num):
        match num:
            case 1:
                self.burst = 0.8


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        pass


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        self.burst *= 0.95

        self.angles = 2*np.pi * (2/360) * np.sin(2*np.pi * beat_progress + self.angle_phases)
        self.scales = 1 + (0.03 + 0.04 * self.intensity) * np.sin(2*np.pi * beat_progress + self.scale_phases)
        if self.intensity == 3:
            self.burst = 0.2 * (1 + np.cos(2*np.pi * beat_progress))


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        screen.lock()

        n_shadows = int(np.round(self.n_shadows * (self.intensity + np.sin(2*np.pi * measure_progress)/2)/3))
        if self.intensity > 0:
            for i, layer in enumerate(self.shadows[-n_shadows:]):
                for j, shadow in enumerate(layer):
                    time = 2*np.pi * (beat_progress - 0.05*i)
                    a = 2*np.pi * (2/360) * np.sin(time + self.angle_phases[j])
                    s = 1 + 0.05 * np.sin(time + self.scale_phases[j])
                    shadow = shadow + self.burst*(np.mean(shadow, axis=0) - self.center)
                    if self.intensity == 1:
                        p = scale(shadow, s)
                    elif self.intensity >= 2:
                        p = scale(rotate(shadow, a), s)
                    hue = ((t + 0.05*i) % 3) / 3
                    lightness = 0.8 * (i/n_shadows)**1.3
                    pygame.draw.polygon(screen, (0,0,0), p)
                    pygame.draw.aalines(screen, hls_to_rgb(hue, lightness * brightness, 1), True, p)

        for i, poly in enumerate(self.bird):
            poly = poly + self.burst*(np.mean(poly, axis=0) - self.center)
            if self.intensity == None:
                p = poly
            elif self.intensity <= 1:
                p = scale(poly, self.scales[i])
            elif self.intensity >= 2:
                p = scale(rotate(poly, self.angles[i]), self.scales[i])
            pygame.draw.polygon(screen, (0,0,0), p)
            hue = ((t + 0.05*n_shadows) % 3) / 3
            lightness = 0.4 + 0.33 * np.sin(2*np.pi * beat_progress)
            pygame.draw.polygon(screen, hls_to_rgb(hue, lightness * brightness, 1), p, width=2)

        screen.unlock()



class Bird_2():

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.center = np.array([width/2, height/2])

        bird = [
            np.array([[0, 78.074], [3.902, 66.544], [14.604, 64.388]]),
            np.array([[41.12, 33.287], [107.46482, 42.729905], [66.54, 14.503], [47.334, 16.344]]),
            np.array([[86.067, 9.059], [70.132, 6.717], [72.645, 0.39]]),
            np.array([[66.113, 12.828], [71.513, -0.001], [46.065, 14.836], [66.112, 12.828]]),
            np.array([[40.358, 34.951], [22.01, 52.183], [49.245, 35.854]]),
            np.array([[50.858, 36.214], [44.372, 40.373], [88.107, 51.749], [80.389, 40.263]]),
            np.array([[38.897, 34.271], [45.93, 14.965], [33.994, 28.681], [14.925, 57.207]]),
            np.array([[35.386, 45.849], [27.042, 60.627], [4.543, 64.977]])
        ]
        bird = [4*poly + np.array([955, 200]) for poly in bird]
        self.birds = [[rotate_around(poly, i*2*np.pi/9, self.center) for poly in bird] for i in range(9)]
        self.directions = np.array([np.mean(np.concatenate(b), axis=0) - self.center for b in self.birds])
        self.directions = self.directions / np.linalg.norm(self.directions, axis=1, keepdims=True)

        self.reset()


    def reset(self):
        self.intensity = 0
        self.stage = 0
        self.mirror = False


    def event(self, num):
        if num == 1:
            self.mirror = not self.mirror


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        self.stage = (self.stage + 1) % 8


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        pass


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        screen.lock()
        for i, bird in enumerate(self.birds):
            beat_cos_i = 0.5 - 0.5 * np.cos(2*np.pi * beat_progress + 4*np.pi*i/9)
            for j, poly in enumerate(bird):
                dist = np.linalg.norm(poly.mean(axis=0) - self.center)
                hue = (dist/1000 + i/9 + (t%2)/2) % 1
                poly_ = rotate_around(poly, -0.75 * t, self.center)
                if self.intensity == 1:
                    poly_ = scale_around(poly_, 1 + 0.05 * beat_cos_i, self.center)
                elif self.intensity == 2:
                    poly_ = scale_around(poly_, 1 + 0.1 * beat_cos_i, self.center)
                elif self.intensity == 3:
                    beat_cos = 0.5 - 0.5 * np.sin(2*np.pi * (beat_progress - dist/1500))
                    poly_ += (10 + dist/5) * beat_cos * rotate_around(self.directions[i][None,:], -0.75 * t, np.zeros(2))
                if self.mirror:
                    poly_[:,0] = self.w - poly_[:,0]
                n_lines = np.linspace(1, 0, self.intensity + 1, endpoint=False)
                for k in n_lines:
                    if self.intensity <= 1:
                        lightness = 0.9 if self.stage == j else 0.4
                        pygame.draw.polygon(screen, hls_to_rgb(hue, lightness*brightness * k, 1), scale(poly_, k), width=1)
                    elif self.intensity == 2:
                        if self.stage == j:
                            lightness = 0.7
                            width = 2
                        else:
                            lightness = 0.3 - 0.1 * np.cos(2*np.pi * (beat_progress + k))
                            width = 1
                        pygame.draw.polygon(screen, hls_to_rgb(hue, lightness*brightness * k, 1), scale(poly_, k), width=width)
                    elif self.intensity == 3:
                        if self.stage == j:
                            lightness = 0.7
                        else:
                            lightness = (0.05 + k/5) - 0.05 * np.cos(2*np.pi * (beat_progress + k))
                        pygame.draw.polygon(screen, hls_to_rgb(hue, lightness*brightness * k, 1), scale(poly_, k), width=2)
        screen.unlock()
