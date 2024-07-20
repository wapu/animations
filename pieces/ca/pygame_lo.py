import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

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



class LO():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])

        self.O = self.center + 120 * np.array([[1, -1], [-1, -1], [-1, 1], [1, 1]])
        self.L = self.center + 120 * np.array([[-2.3, -1], [-1.5, -1], [-1.5, 1.5], [1, 1.5], [1, 2.3], [-2.3, 2.3]])

        self.last_update = time()
        self.reset()


    def reset(self):
        self.intensity = 0
        self.i_corner = 0
        self.corner = self.O[self.i_corner]
        self.color = 0
        self.rotation = 0
        self.angular_v = 0.05
        self.rotation_dir = 1

        self.Ls = []
        self.latest_L = rotate_around(self.L, self.i_corner * np.pi/2, self.center)


    def event(self, num):
        match num:
            case 0:
                self.rotation_dir *= -1


    def clear_frame(self, screen):
        if self.intensity == 3:
            screen.fill([180]*3, special_flags=pygame.BLEND_MULT)
        else:
            screen.fill((0,0,0))


    def beat(self, t):
        if self.intensity >= 1:
            # Add latest L to the ones flying away
            # Flying Ls have coords, outward velocity, color, base rotation and angular velocity
            v = 0.055 * (np.mean(self.latest_L, axis=0) - self.center)
            self.Ls.append([self.latest_L, v, hls_to_rgb(self.color, 0.05), self.rotation, self.angular_v])

            # Switch corner
            self.i_corner = (self.i_corner + 1) % 4
            self.corner = self.O[self.i_corner]

            # Spawn new l
            self.latest_L = rotate_around(self.L, self.i_corner * np.pi/2, self.center)

        # Drop old Ls
        self.Ls = [[L, v, c, r, av] for [L, v, c, r, av] in self.Ls if c.sum() > 1]


    def update(self, t, beat_progress, measure_progress, bpm):
        self.color = measure_progress
        self.rotation += self.rotation_dir * self.angular_v

        for i in range(len(self.Ls)):
            # L, v, color, r, av
            self.Ls[i][0] += self.Ls[i][1]
            self.Ls[i][3] += self.Ls[i][4]
            self.Ls[i][0][:] = scale_around(self.Ls[i][0], 1.02, self.center)
            self.Ls[i][2] *= 0.9
            self.Ls[i][4] *= 0.9


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_wave = 0.5 - 0.5*np.sin(2*np.pi * beat_progress + np.pi/4)
        color = hls_to_rgb(self.color, 0.05)
        effective_color = color * brightness
        if self.intensity == 3:
            effective_color *= 2*beat_wave
        if self.intensity >= 2:
            border_color = [255 * beat_wave * brightness] * 3
        else:
            border_color = [127 * brightness] * 3

        if self.intensity >= 1:
            for L, _, c, rotation, _ in self.Ls:
                L = rotate_around(L, rotation, self.center)
                pygame.draw.polygon(screen, c * (1 if self.intensity < 3 else 2*beat_wave), L)
                if self.intensity >= 2:
                    pygame.draw.polygon(screen, border_color, L, width=2)
                else:
                    pygame.draw.aalines(screen, border_color, True, L)

            latest_L = scale_around(self.latest_L, 0.3 + 0.7 * beat_progress, self.corner)
            latest_L = rotate_around(latest_L, self.rotation, self.center)
            pygame.draw.polygon(screen, effective_color, latest_L)
            if self.intensity >= 2:
                pygame.draw.polygon(screen, border_color, latest_L, width=2)
            else:
                pygame.draw.aalines(screen, border_color, True, latest_L)

        O = scale_around(self.O, 0.8 + 0.4 * beat_wave, self.corner)
        O = rotate_around(O, self.rotation, self.center)
        pygame.draw.polygon(screen, effective_color, O)
        if self.intensity >= 2:
            pygame.draw.polygon(screen, border_color, O, width=2)
        else:
            pygame.draw.aalines(screen, border_color, True, O)

        if self.intensity == 0:
            L = rotate_around(self.L, self.i_corner * np.pi/2, self.center)
            L = scale_around(L, 0.8 + 0.4 * beat_wave, self.corner)
            L = rotate_around(L, self.rotation, self.center)
            pygame.draw.polygon(screen, effective_color, L)
            pygame.draw.aalines(screen, border_color, True, L)
