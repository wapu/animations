import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np
import pickle

from shapely import geometry as geo
from shapely.validation import make_valid
from time import time

from colors import *



def get_ellipse(a, b, n_points=50):
    t = np.linspace(0, 2*np.pi, n_points)[:,None]
    return np.hstack([a * np.cos(t), b * np.sin(t)])

def rotate(poly, angle):
    center = np.mean(poly, axis=0)
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return center + np.matmul(poly - center, r)

def rotate_around(poly, angle, anchor):
    r = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    return anchor + np.matmul(poly - anchor, r)



class Spotlights():

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.size = np.array([width, height])
        self.center = self.size/2

        with open('data/CLLGM CDMCM.pkl', 'rb') as f:
            self.cllgm = pickle.load(f)

        self.n_lights = 3
        self.surfaces = [pygame.Surface((width, height)) for i in range(self.n_lights)]
        self.shadow_length = 100
        self.z_light = 500
        self.z_lines = 100
        self.half_angle = 15 * 2*np.pi/360

        self.reset()


    def reset(self):
        self.last_update = time()
        self.new_lights()


    def new_lights(self):
        self.angles_l = 2*np.pi * np.random.rand(self.n_lights)
        self.radii_l = (0.35 + 0.1*np.random.rand()) * self.h
        self.pos_l = self.center +  np.stack([self.radii_l * (self.w/self.h) * np.cos(self.angles_l), self.radii_l * np.sin(self.angles_l)]).T
        self.v_l = 2*np.pi * 0.001 * 1#np.random.randn(self.n_lights)

        self.angles_t = 2*np.pi * np.random.rand(self.n_lights)
        self.radii_t = (0.01 + 0.3*np.random.rand()) * self.h
        self.pos_t = self.center +  np.stack([self.radii_t * (self.w/self.h) * np.cos(self.angles_t), self.radii_t * np.sin(self.angles_t)]).T
        self.v_t = 2*np.pi * 0.001 * 1#np.random.randn(self.n_lights)
        self.hues = (np.random.rand() + np.arange(self.n_lights)/self.n_lights) % 1


    def event(self):
        self.new_lights()
        pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def update(self, bpm, last_beat, delta_t):
        self.angles_l += self.v_l
        self.pos_l = self.center + np.stack([self.radii_l * (self.w/self.h) * np.cos(self.angles_l), self.radii_l * np.sin(self.angles_l)]).T
        self.angles_t += self.v_t
        self.pos_t = self.center +  np.stack([self.radii_t * (self.w/self.h) * np.cos(self.angles_t), self.radii_t * np.sin(self.angles_t)]).T

        # Limit FPS to BPM for everything below
        if time() - last_beat < 60/bpm:
            self.last_update = last_beat
            return
        if time() - self.last_update < 60/bpm:
            return
        self.last_update += 60/bpm

        # self.new_lights()


    def draw(self, screen, bpm, last_beat, brightness):
        # t = (time() - last_beat) / (60/bpm)
        # beat_cos = 0.5 - 0.5*np.cos(2*np.pi * t)
        # beat_spike = np.exp(-((t - np.round(t))*20)**2)

        for i in range(self.n_lights):
            surf = self.surfaces[i]
            surf.lock()
            surf.fill([0]*3)

            # Calculate ellipses for light cones
            # See https://math.stackexchange.com/a/2177933
            dx = np.sqrt(np.sum((self.pos_l[i] - self.pos_t[i])**2))
            alpha = np.arctan2(self.z_light, dx)
            R = np.sqrt(dx**2 + self.z_light**2)
            p1 = R * np.tan(self.half_angle) * np.cos(self.half_angle) / np.cos(alpha + self.half_angle)
            p2 = R * np.tan(self.half_angle) * np.cos(self.half_angle) / np.cos(alpha - self.half_angle)
            if p1 <= 0 or p2 <= 0:
                surf.unlock()
                break
            a = (p1 + p2)/2
            b = a * R * np.tan(self.half_angle) / np.sqrt(p1*p2)
            ellipse = get_ellipse(a, b)

            target_angle = np.arctan2(self.pos_l[i][1] - self.pos_t[i][1], self.pos_t[i][0] - self.pos_l[i][0])
            ellipse = self.pos_t[i] + rotate(ellipse, target_angle)
            if dx > a:
                xt = -(a*a)/dx
                yt = np.sqrt(b*b * (1 - (xt**2/a**2)))
                cone = np.array([(-dx, 0), (xt, yt), (xt, -yt)])
                cone = self.pos_t[i] + rotate_around(cone, target_angle, np.zeros(2))
                pygame.draw.aalines(surf, hls_to_rgb(self.hues[i], 0.01 * brightness), True, cone)
            pygame.draw.polygon(surf, hls_to_rgb(self.hues[i], 0.02 * brightness), ellipse)

            # Draw colored outline of letters
            intersections = []
            for letter in self.cllgm:
                poly = geo.Polygon(ellipse)
                lines = geo.LineString(letter)
                if lines.intersects(poly):
                    intersection = lines.intersection(poly)
                    if isinstance(intersection, geo.LineString):
                        intersections.append(np.asarray(intersection.coords))
                    elif isinstance(intersection, geo.MultiLineString):
                        intersections.extend([np.asarray(line.coords) for line in intersection.geoms])
            for intersection in intersections:
                pygame.draw.lines(surf, hls_to_rgb(self.hues[i], 0.5 * brightness), False, intersection, width=3)

            # Draw shadows
            for letter in self.cllgm:
                outer = letter - self.pos_l[i]
                dists = np.linalg.norm(outer, axis=-1, keepdims=True)
                lengths = dists * self.z_lines / (self.z_light - self.z_lines)
                outer /= dists
                outer = letter + lengths * outer

                for j in range(len(letter)-1):
                    pygame.draw.polygon(surf, [0]*3, [letter[j], letter[j+1], outer[j+1], outer[j]])

            # Fill letters in
            for letter in self.cllgm:
                pygame.draw.polygon(surf, [0]*3, letter)

                e = geo.Polygon(ellipse)
                l = geo.Polygon(letter)
                try:
                    intersection = e.intersection(l)
                    if isinstance(intersection, geo.Polygon):
                        intersection = np.asarray(intersection.exterior.coords)
                        pygame.draw.polygon(surf, hls_to_rgb(self.hues[i], 0.025 * brightness), intersection)
                    elif isinstance(intersection, geo.MultiPolygon):
                        for poly in intersection.geoms:
                            pygame.draw.polygon(surf, hls_to_rgb(self.hues[i], 0.025 * brightness), poly.exterior.coords)
                except:
                    pass

            surf.unlock()

            # Add light contribution to canvas
            screen.blit(surf, (0,0), special_flags=pygame.BLEND_ADD)

        # Display light sources
        for i in range(self.n_lights):
            pygame.draw.circle(screen, hls_to_rgb(self.hues[i], 0.5 * brightness), self.pos_l[i], radius=5)
            pygame.draw.circle(screen, hls_to_rgb(self.hues[i], 1 * brightness), self.pos_t[i], radius=2)
