import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from time import time

from colors import *



def spike_pattern(n_y, size, i=None):
    if i is None:
        i = np.random.randint(5)
    match i:
        case 0:
            spike = np.sin(np.arange(n_y)) * size
        case 1:
            spike = np.cos(np.arange(n_y)/2) * size
        case 2:
            spike = (np.arange(n_y)**3)/(n_y**2) * size/4
        case 3:
            spike = (np.random.rand(n_y) - 1) * size
        case 4:
            spike = np.ones(n_y) * size/2
    sign = 2*np.random.randint(2) - 1
    return spike * sign



class Matrix():

    def __init__(self, width, height):
        self.w = width
        self.h = height

        self.font_size = 20
        self.fonts = ['Sakurata', 'Chilanka']
        self.drops_per_beat = 4

        self.sequence = 'RAMBACAMBA '
        self.sequence = 'BLOCK PARTY '
        self.n_x = (self.w + 2*self.font_size) // (self.font_size+5)
        self.n_y = (self.h + self.font_size) // (self.font_size+5) + 1

        self.reset()


    def reset(self):
        self.intensity = 0
        self.i_font = 0
        self.font = pygame.font.SysFont(self.fonts[self.i_font], self.font_size)

        self.letters = np.arange(self.n_x * self.n_y).reshape(self.n_x, self.n_y) % len(self.sequence)
        for x in range(self.n_x):
            self.letters[x,:] = (self.letters[x,:] + np.random.randint(len(self.sequence))) % len(self.sequence)
        self.flipped = np.random.randint(2, size=(self.n_x, self.n_y))
        self.rotation = np.random.randint(3, size=(self.n_x, self.n_y)) - 1
        self.hue = np.zeros((self.n_x, self.n_y))
        self.hue_offset = 0.05 * np.random.rand(self.n_x, self.n_y)
        self.age = np.zeros((self.n_x, self.n_y)) - 60

        self.drops = []
        self.glitches = [(np.random.randint(self.n_x), np.random.randint(self.n_y)) for i in range(100)]
        self.spike = np.zeros(self.n_y)
        self.spike_event = np.zeros(self.n_y)


    def event(self, num):
        if num == 0:
            self.i_font = 1 - self.i_font
            self.font = pygame.font.SysFont(self.fonts[self.i_font], self.font_size)
        if 1 <= num <= 5:
            self.spike_event = spike_pattern(self.n_y, self.font_size * 3, num-1)


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        # Add new drops
        for i in range(np.random.randint(1, self.drops_per_beat+1)):
            column = np.random.randint(self.n_x)
            speed = 0.1 + 0.6*np.random.rand()
            flipped = np.random.randint(2)
            rotation = np.random.randint(3) - 1
            letter = np.random.randint(len(self.sequence))
            hue = (t % 10) / 10
            self.drops.append([column, 0.0, speed, flipped, rotation, letter, hue])

        # Apply glitches
        for x,y in self.glitches:
            self.letters[x,y] = np.random.randint(len(self.sequence))
            self.flipped[x,y] = np.random.randint(2)
            self.rotation[x,y] = np.random.randint(3) - 1

        # Change glitch locations
        for i in range(10):
            self.glitches[np.random.randint(len(self.glitches))] = (np.random.randint(self.n_x), np.random.randint(self.n_y))

        # Change spike type
        self.spike = spike_pattern(self.n_y, self.font_size)


    def update(self, t, beat_progress, measure_progress, bpm):
        # Move and apply all drops
        for drop in self.drops:
            x, y, speed, flipped, rotation, letter, hue = drop
            x, y = int(x), int(y)
            self.letters[x,y] = (letter + y) % len(self.sequence)
            self.age[x,y] = t
            self.flipped[x,y] = flipped
            self.rotation[x,y] = rotation
            self.hue[x,y] = hue + self.hue_offset[x,y]
            drop[1] += speed

        # Remove drops that leave the screen
        self.drops = [drop for drop in self.drops if int(drop[1]) < self.n_y]

        # Fade away user event
        self.spike_event *= 0.9


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)
        beat_spike = np.exp(-((beat_progress/2 - np.round(beat_progress/2))*20)**2)

        for x in range(self.n_x):
            for y in range(self.n_y):
                letter = self.sequence[self.letters[x,y]]
                if t - self.age[x,y] < 0.05:
                    lightness = 0.25 + 0.75 * beat_cos
                else:
                    if self.intensity < 3:
                        lightness = 0.5 * np.exp(-(t - self.age[x,y])**2 / 3) * (0.8 + 0.2 * beat_cos)
                    else:
                        lightness = 0.7 * np.exp(-(t - self.age[x,y])**2 / (3 + 5*beat_cos)) * (0.4 + 0.6 * beat_cos)
                color = hls_to_rgb(self.hue[x,y], lightness * brightness, .7)
                l = self.font.render(letter, True, color)
                l = pygame.transform.flip(l, self.flipped[x,y] == 1, False)
                l = pygame.transform.rotate(l, 90 * self.rotation[x,y])
                w, h = l.get_size()
                x_ = (self.font_size+5)*x - w/2
                if self.intensity >= 1:
                    x_ += beat_spike * self.spike[y]
                x_ += self.spike_event[y]
                y_ = (self.font_size+5)*y - h/2
                if self.intensity >= 2:
                    y_ -= self.font_size * beat_cos
                    y_ -= 20 * beat_spike
                screen.blit(l, (x_, y_))
