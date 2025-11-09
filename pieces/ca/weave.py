import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from colors import *
from shapely import geometry as geo
from shapely import GeometryCollection
from shapely.affinity import rotate, scale, translate
from scipy.linalg import norm



class Weave():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])
        self.WH = np.array([width, height])

        self.spacing = 20
        self.n_weaves = 5

        # Create all the lines
        length = norm(self.WH)
        self.weaves_base = []
        for offset in np.linspace(0, self.spacing, self.n_weaves, endpoint=False):
            lines = []
            for y in np.arange((height - length)/2 + offset, (height + length)/2, self.spacing):
                lines.append([[(width - length)/2, y], [(width + length)/2, y]])
            self.weaves_base.append(geo.MultiLineString(lines))

        self.hues = np.linspace(0, 0.5, self.n_weaves, endpoint=False)

        # Create shapes
        self.shapes_base = [
            geo.Point((0,0)).buffer(80).boundary.buffer(10)
            # geo.Polygon([(-50,-50), (-50,50), (50,50), (50,-50)]).buffer(10)
            for i in range(self.n_weaves)
        ]

        self.reset()


    def reset(self):
        # Init variables
        self.intensity = 0
        self.flash = 0
        self.spin = np.pi/4
        self.weaves = self.weaves_base
        self.coords = np.random.rand(self.n_weaves,2) * self.WH[None,:]
        self.vs = np.random.randn(self.n_weaves, 2) * 5
        self.angles = 2*np.pi * np.random.rand(self.n_weaves)
        self.angular_vs = 0.02 * np.random.randn(self.n_weaves)
        self.scales = 1.5 + 2 * np.random.rand(self.n_weaves)


    def event(self, num):
        match num:
            case 0:
                pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        # Jump update colors
        self.hues = (self.hues + 0.25) % 1.0

        # Jump rotate weaves a bit
        self.spin += np.pi/24


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        # Update colors
        self.hues = (self.hues + (bpm/60) * 0.001) % 1.0

        # Update shape variables
        for i in range(self.n_weaves):
            if self.coords[i,0] < 0.2 * self.WH[0]:
                self.vs[i,0] += 1
            if self.coords[i,0] > 0.8 * self.WH[0]:
                self.vs[i,0] -= 1
            if self.coords[i,1] < 0.2 * self.WH[1]:
                self.vs[i,1] += 1
            if self.coords[i,1] > 0.8 * self.WH[1]:
                self.vs[i,1] -= 1
            self.vs[i] += 0.5 * np.random.randn(2)
            v_ = norm(self.vs[i])
            if v_ > 10:
                self.vs[i] = self.vs[i] * 10/v_
            if v_ < 5:
                self.vs[i] = self.vs[i] * 5/v_
        self.coords += self.vs
        self.angles += self.angular_vs

        # Rotate weaves and intersect
        self.weaves = []
        bounce = -5 * self.spacing * beat_cos**0.3
        for i in range(self.n_weaves):
            shape = self.shapes_base[i]
            shape = rotate(shape, self.angles[i], use_radians=True)
            shape = scale(shape, self.scales[i] + (1-beat_cos)/3, self.scales[i] + (beat_cos)/3)
            shape = translate(shape, *self.coords[i])
            shape = translate(shape, 0, bounce)
            weave = rotate(self.weaves_base[i], self.spin, origin=self.center, use_radians=True)
            weave = translate(weave, 0, bounce)
            weave = weave.intersection(shape)
            self.weaves.append(weave)



    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress + np.pi)

        # Draw weaves
        for i in range(self.n_weaves):
            # Get all cropped geometries in this weave
            if isinstance(self.weaves[i], geo.MultiLineString):
                geoms = self.weaves[i].geoms
            elif isinstance(self.weaves[i], geo.LineString):
                geoms = [self.weaves[i]]

            # Create rainbow effect
            colors = hls_to_rgb_array(self.hues[i] + np.linspace(0, 0.15, len(geoms)))

            # Draw the lines
            screen.lock()
            for j in range(len(geoms)):
                lines = geoms[j].coords
                if len(lines) >= 2:
                    # color = colors[j] * (100 + 155*beat_cos**4)/colors[j].max()
                    color = colors[j] * 150/colors[j].max()
                    pygame.draw.lines(screen, color * brightness, False, lines)
            screen.unlock()
