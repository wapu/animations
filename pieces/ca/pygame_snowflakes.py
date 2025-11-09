import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from shapely import geometry as geo
from shapely.ops import unary_union
from shapely.affinity import rotate

from colors import *



def rotate_around(points, angle, anchor=0):
    c = np.cos(angle)
    s = np.sin(angle)
    r = np.array([[c, -s], [s, c]])
    return anchor + np.matmul(points - anchor, r)

def scale_around(poly, factor, anchor=0):
    return anchor + factor * (poly - anchor)

def hermite(val):
    return 3*val*val - 2*val*val*val



class Branch():

    def __init__(self, origin, length, angle, thickness, level, seed):
        # Prepare parameters
        np.random.seed(seed)
        self.origin = origin
        self.length = length
        self.angle = angle
        self.thickness = thickness * (0.7 + 0.5 * np.random.rand())
        self.level = level

        # Create rump shape of branch
        self.start = np.array(origin)
        self.end = self.start + self.length * np.array([np.cos(self.angle), np.sin(self.angle)])
        spread = np.pi / np.random.randint(33, 50)
        vertices = [
            self.start,
            self.start + 0.9 * self.length * np.array([np.cos(self.angle - spread), np.sin(self.angle - spread)]),
            self.end,
            self.start + 0.9 * self.length * np.array([np.cos(self.angle + spread), np.sin(self.angle + spread)]),
            self.start
        ]
        self.poly = geo.Polygon(vertices).buffer(self.thickness, join_style='mitre', mitre_limit=0.01*self.length)

        # Add symmetrical and somewhat evenly spaced subbranches
        n_subbranches = np.random.randint(3 - level, 5 - level)
        if n_subbranches > 0:
            positions = np.linspace(0.1, 0.65, n_subbranches) + 0.15 * np.random.rand(n_subbranches)
        self.subbranches = []
        for i in range(n_subbranches):
            pos = positions[i]
            origin = (1 - pos) * self.start + pos * self.end
            length = 0.4 * self.length * np.exp(-(pos - 0.35)**2 * 10)
            if length > 10:
                thickness = self.thickness * (0.8 + 0.2 * np.random.randn())
                seed = np.random.randint(10**6)
                self.subbranches.append(Branch(origin, length, self.angle - np.pi/5, thickness, level + 1, seed))
                self.subbranches.append(Branch(origin, length, self.angle + np.pi/5, thickness, level + 1, seed))

    def get_polys(self):
        polys = [self.poly,]
        for b in self.subbranches:
            polys.extend(b.get_polys())
        return polys


class Flake():

    def __init__(self, center, radius, angle, hue, seed):
        # Prepare parameters
        self.thickness = 0.04 + 0.04 * np.random.rand() * radius
        self.angle = angle
        self.hue = hue
        length = radius * (0.9 + 0.2 * np.random.rand())

        # Create branch recursively
        self.branch = Branch(center, length, 0, self.thickness, 0, seed)

        # Combine branch into 6-symmetric snowflake shape
        self.poly = unary_union(self.branch.get_polys())
        center = geo.Point(center)
        self.poly = unary_union([rotate(self.poly, i * np.pi/3, origin=center, use_radians=True) for i in range(6)])

        # Prepare coordinate arrays for display
        self.main = np.asarray(self.poly.exterior.coords)
        self.outer = np.asarray(self.poly.buffer(15).exterior.coords)
        inner = self.poly.buffer(-10)
        if inner.geom_type == 'MultiPolygon':
            self.inner = [np.asarray(poly.exterior.coords) for poly in inner.geoms]
        else:
            self.inner = [np.asarray(inner.exterior.coords)]


class Snowflakes():

    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.WH = np.array([width, height])
        self.center = np.array([width/2, height/2])

        self.n_bg = 100

        # BG star shape
        points = np.linspace(0, 2*np.pi, 8, endpoint=False)
        x, y = np.cos(points), np.sin(points)
        self.bg_flake = np.stack([x,y], axis=-1)
        self.bg_flake[::2,:] *= 0.3
        self.bg_flake *= 7

        self.radius = 0.4 * min(self.W, self.H)
        self.gravity = np.array([0, 4])

        self.reset()


    def reset(self):
        self.intensity = 0

        self.angle = 0
        self.flakes = [
            Flake(self.center, self.radius, self.angle, np.random.rand(), seed=np.random.randint(10**6)),
            Flake(self.center, self.radius, self.angle + np.pi/6, np.random.rand(), seed=np.random.randint(10**6))
        ]

        self.bg_coords = np.random.rand(self.n_bg, 2) * self.WH
        self.bg_angles = 2*np.pi * np.random.rand(self.n_bg)
        self.bg_vs = np.random.randn(self.n_bg, 2)


    def event(self, num):
        match num:
            case 0:
                pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        self.flakes.append(Flake(self.center, self.radius, self.angle, np.random.rand(), seed=int(10**6 * t)))
        self.flakes = self.flakes[1:]
        self.angle = (self.angle + np.pi/6) % (2*np.pi)


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        self.bg_vs += 0.2 * np.random.randn(*self.bg_vs.shape)
        self.bg_vs *= np.array([0.95, 0.7])
        self.bg_coords += self.bg_vs + self.gravity
        self.bg_coords = self.bg_coords % self.WH


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        beat_cos = 0.5 - 0.5*np.cos(2*np.pi * beat_progress)

        # Draw background flakes
        color = hls_to_rgb((0.1 * t) % 1, 0.1 + 0.25 * (1-beat_cos)**5, 0.2)
        bg_coords = scale_around(self.bg_coords, 1.1 - 0.1*beat_cos, self.center)
        for i in range(self.n_bg):
            flake = rotate_around(self.bg_flake, self.bg_angles[i] - 0.5*t)
            flake *= np.exp(-self.bg_vs[i]**2 * 2)
            pygame.draw.aalines(screen, color, True, flake + bg_coords[i])

        # Draw old flake
        scale = 0.7 + 0.3 * hermite(1 - beat_progress)
        rotation = 0.2 * t + self.flakes[0].angle
        flake = rotate_around(scale_around(self.flakes[0].main, scale, self.center), rotation, self.center)
        outer_flake = rotate_around(scale_around(self.flakes[0].outer, scale + 0.05*beat_cos, self.center), rotation, self.center)
        inner_flakes = [rotate_around(scale_around(poly, scale - 0.05*beat_cos, self.center), rotation, self.center) for poly in self.flakes[0].inner]

        hue = self.flakes[0].hue
        main_color = hls_to_rgb(hue, 0.5 * hermite(1 - beat_progress), 0.2)
        side_color = hls_to_rgb(hue, 0.25 * hermite(1 - beat_progress), 0.2)

        pygame.draw.polygon(screen, (0,0,0), outer_flake)
        pygame.draw.aalines(screen, main_color, False, flake)
        pygame.draw.aalines(screen, side_color, False, outer_flake)
        for poly in inner_flakes:
            pygame.draw.aalines(screen, side_color, False, poly)

        # Draw new flake
        scale = hermite(beat_progress)
        rotation = 0.2 * t + self.flakes[1].angle
        flake = rotate_around(scale_around(self.flakes[1].main, scale, self.center), rotation, self.center)
        outer_flake = rotate_around(scale_around(self.flakes[1].outer, scale + 0.2*beat_cos, self.center), rotation, self.center)
        inner_flakes = [rotate_around(scale_around(poly, scale - 0.3*beat_cos, self.center), rotation, self.center) for poly in self.flakes[1].inner]

        hue = self.flakes[1].hue
        main_color = hls_to_rgb(hue, 0.5 + 0.3 * beat_cos, 0.2)
        side_color = hls_to_rgb(hue, 0.25, 0.2)

        pygame.draw.polygon(screen, (0,0,0), outer_flake)
        pygame.draw.aalines(screen, main_color, False, flake)
        pygame.draw.aalines(screen, side_color, False, outer_flake)
        for poly in inner_flakes:
            pygame.draw.aalines(screen, side_color, False, poly)

