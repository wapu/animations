import contextlib
with contextlib.redirect_stdout(None):
    import pygame.draw
import numpy as np

from scipy.spatial import Delaunay
from shapely import geometry as geo

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



class Explosion():

    def __init__(self, width, height):
        self.center = np.array([width/2, height/2])

        self.rat = [
            np.array([[154.36952,80.547796], [147.00114,97.488823], [138.63272,91.364133]]),
            np.array([[145.91624,99.017996], [137.67399,92.881428], [129.8267,111.0769]]),
            np.array([[129.52062,69.895552], [137.90336,88.382847], [122.7762,123.51521], [116.08748,113.68673], [87.616424,108.0264]]),
            np.array([[115.93126,79.316193], [128.45212,67.944441], [113.94053,53.295623], [106.19609,57.766886], [103.58432,67.910156]]),
            np.array([[87.256701,109.88238], [115.2443,115.41252], [122.89102,126.57198], [118.71112,143.90717], [105.91583,141.84824], [85.501902,126.23895]]),
            np.array([[130.0917,144.78237], [122.61643,134.07485], [120.46141,143.7911]]),
            np.array([[125.04515,132.76764], [122.6714,133.50804], [123.40507,130.4461]]),
            np.array([[82.599997,127.24983], [84.907074,127.24983], [103.73998,142.2131], [83.56829,138.94232]]),
            np.array([[81.348414,129.60195], [82.225042,139.07432], [66.571785,137.92519], [46.457237,129.06917], [13.680662,122.12347], [45.292001,124.77719], [64.025824,130.96365]]),
            np.array([[135.03892,78.187038], [130.23109,66.538022], [123.65955,60.268029], [158.20582,61.821157], [158.04591,65.271482]]),
            np.array([[122.05796,58.851656], [115.23626,49.194838], [106.53024,53.072294], [105.72472,55.392639], [114.25902,51.432745]]),
        ]
        for poly in self.rat:
            poly[:] = 5*poly + np.array([400, 50])
        self.rat_offset = np.concatenate(self.rat, axis=0).mean(axis=0)
        self.rat = [poly - self.rat_offset for poly in self.rat]

        self.reset()


    def reset(self):
        self.intensity = 0
        self.stage = 0

        self.polys = self.rat
        self.areas = [geo.Polygon(p).area for p in self.polys]
        self.offsets = np.tile(self.rat_offset, (len(self.polys), 1))
        self.velocities = np.zeros((len(self.polys), 2))
        self.angles = np.zeros(len(self.polys))
        self.angular_vs = np.zeros(len(self.polys))


    def event(self):
        pass


    def clear_frame(self, screen):
        screen.fill((0,0,0))


    def beat(self, t):
        if len(self.polys) > 100:
            self.reset()
            self.stage = -1
        if self.stage < 0:
            self.stage += 1
            return

        # Explode each polygon and update the smithereens
        polys = []
        areas = []
        offsets = []
        velocities = []
        angles = []
        angular_vs = []

        for i, poly in enumerate(self.polys):
            shape = geo.Polygon(poly)
            centroid = np.asarray(shape.centroid.coords)

            smithereens = []
            if self.areas[i] < np.max(self.areas)/4:
                smithereens.append(poly)
            elif len(poly) == 3:
                a, b, c = np.sum(np.square(poly - np.roll(poly, -1, axis=0)), axis=1)
                if a > b + c:
                    mid = (poly[0] + poly[1])/2
                    smithereens.append(np.stack([poly[0], mid, poly[2]]))
                    smithereens.append(np.stack([poly[1], mid, poly[2]]))
                elif b > c + a:
                    mid = (poly[1] + poly[2])/2
                    smithereens.append(np.stack([poly[1], mid, poly[0]]))
                    smithereens.append(np.stack([poly[2], mid, poly[0]]))
                elif c > a + b:
                    mid = (poly[2] + poly[0])/2
                    smithereens.append(np.stack([poly[2], mid, poly[1]]))
                    smithereens.append(np.stack([poly[0], mid, poly[1]]))
                else:
                    poly_ = np.append(poly, poly.mean(axis=0)[None,:], axis=0)
                    smithereens.append(poly_[[0,1,3]])
                    smithereens.append(poly_[[1,2,3]])
                    smithereens.append(poly_[[2,0,3]])
            else:
                triangulation = Delaunay(poly)
                triangles = poly[triangulation.simplices]
                for t in triangles:
                    if shape.contains(geo.Point(t.mean(axis=0))):
                        smithereens.append(t)

            for s in smithereens:
                polys.append(s)
                areas.append(geo.Polygon(s).area)
                offsets.append(self.offsets[i:i+1])
                if len(smithereens) > 1:
                    v = s.mean(axis=0) - centroid
                    v = 30 * v/np.linalg.norm(v) + 5 * np.random.randn()
                else:
                    v = 15 * centroid/np.linalg.norm(centroid) + 3 * np.random.randn()
                velocities.append(self.velocities[i:i+1] + v)
                angles.append(self.angles[i])
                angular_vs.append(self.angular_vs[i] + 0.2 * np.random.randn())

        self.polys = polys
        self.areas = areas
        self.offsets = np.concatenate(offsets, axis=0)
        self.velocities = np.concatenate(velocities, axis=0)
        self.angles = np.array(angles)
        self.angular_vs = np.array(angular_vs)
        self.stage += 1


    def measure(self, t):
        pass


    def update(self, t, beat_progress, measure_progress, bpm):
        self.offsets += self.velocities
        self.angles += self.angular_vs
        self.velocities *= 0.9
        self.angular_vs *= 0.95


    def draw(self, screen, brightness, t, beat_progress, measure_progress):
        # for poly in self.rat:
        #     pygame.draw.polygon(screen, [10]*3, poly, width=1)

        for i in range(len(self.polys)):
            pygame.draw.polygon(screen, [0]*3, self.offsets[i] + rotate(self.polys[i], self.angles[i]))
            pygame.draw.polygon(screen, [255]*3, self.offsets[i] + rotate(self.polys[i], self.angles[i]), width=1)
