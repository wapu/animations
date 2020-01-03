import numpy as np
from shapely import geometry as geo
from copy import deepcopy as copy

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'fractal_triangles'
width, height = 768, 768
duration = 8


class Triangle():

    def __init__(self, size, offset=(0,0), angle=0, parent=None):
        self.coordinates = np.array([
            [-size/2, -np.sqrt(3)*size/6, 1],
            [ size/2, -np.sqrt(3)*size/6, 1],
            [      0,  np.sqrt(3)*size/3, 1]
        ])
        self.transform = np.array([
            [np.cos(angle), -np.sin(angle), offset[0]],
            [np.sin(angle),  np.cos(angle), offset[1]],
            [            0,              0,         1]
        ])
        self.size = size
        self.parent = parent

    def copy(self):
        t = Triangle(self.size)
        t.transform = np.array(self.transform)
        t.parent = self.parent
        return t

    def parent_transform(self):
        if self.parent:
            return np.matmul(self.parent.parent_transform(), self.transform)
        else:
            return self.transform

    def points(self, local=False, scale=1):
        assert scale > 0
        points = np.matmul(self.coordinates * [scale, scale, 1],
                           self.transform.T if local else self.parent_transform().T)
        return points[:,:2]

    def center(self, local=True):
        return np.mean(self.points(local=local), axis=0)

    def inner_radius(self): return np.sqrt(3)*self.size/6
    def outer_radius(self): return np.sqrt(3)*self.size/3
    def height(self): return np.sqrt(3)*self.size/2

    def scale(self, factor):
        assert factor > 0
        self.coordinates[:,:2] *= factor
        self.size *= factor
        return self

    def move(self, xy):
        self.transform[:2,2] += xy
        return self

    def rotate(self, angle):
        R = np.array([
            [np.cos(angle), -np.sin(angle), 0],
            [np.sin(angle),  np.cos(angle), 0],
            [            0,              0, 1]
        ])
        self.transform = np.matmul(R, self.transform)
        return self

    def rotate_around(self, angle, xy):
        self.move((-np.array(xy)))
        self.rotate(angle)
        self.move(xy)
        return self

    def rotate_inplace(self, angle):
        return self.rotate_around(angle, self.center())

    def draw(self, surface, s=.7, f=.3, w=3, helpers=False):
        gz.polyline(points=self.points(), close_path=True, stroke_width=w,
                    stroke=(s,s,s), fill=(f,f,f)).draw(surface)
        gz.polyline(points=self.points(scale=1/3), close_path=True, stroke_width=w,
                    stroke=(s,s,s), fill=(0,0,0)).draw(surface)
        if helpers:
            gz.circle(r=self.size/20, xy=(self.points(scale=0.8)[0]), fill=(1,0,0)).draw(surface)
            gz.circle(r=self.size/20, xy=(self.points(scale=0.8)[1]), fill=(0,1,0)).draw(surface)
            gz.circle(r=self.size/20, xy=(self.points(scale=0.8)[2]), fill=(0,0,1)).draw(surface)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t/duration

    angle_all = 2*progress * 2*np.pi / 3

    # Set up triangles
    t1 = Triangle(256.0)

    t2 = []
    for i in range(3):
        t2.append(Triangle(t1.size/2, parent=t1))
        t2[-1].rotate_inplace(np.pi)
        t2[-1].move((-t2[-1].size/2, - t1.inner_radius() - t2[-1].inner_radius()))
        t2[-1].rotate_around(i * 2*np.pi/3, (0,0))

    t3 = []
    for i in range(3):
        t3.append(Triangle(t2[i].size/2, parent=t2[i]))
        t3[-1].move((-t3[-1].size/2, - t2[i].inner_radius() - t3[-1].inner_radius()))
        t3[-1].rotate_inplace(np.pi).rotate_around(-2*np.pi/3, (0,0))
        t3.append(t3[-1].copy())
        t3[-1].rotate_around(-2*np.pi/3, (0,0))

    t4 = []
    for i in range(len(t3)):
        t4.append(Triangle(t3[i].size/2, parent=t3[i]))
        t4[-1].move((-t4[-1].size/2, - t3[i].inner_radius() - t4[-1].inner_radius()))
        t4[-1].rotate_inplace(np.pi).rotate_around(-2*np.pi/3, (0,0))
        t4.append(t4[-1].copy())
        t4[-1].rotate_around(-2*np.pi/3, (0,0))

    t5 = []
    for i in range(len(t4)):
        t5.append(Triangle(t4[i].size/2, parent=t4[i]))
        t5[-1].move((-t5[-1].size/2, - t4[i].inner_radius() - t5[-1].inner_radius()))
        t5[-1].rotate_inplace(np.pi).rotate_around(-2*np.pi/3, (0,0))
        t5.append(t5[-1].copy())
        t5[-1].rotate_around(-2*np.pi/3, (0,0))

    # Movement
    t1.rotate_inplace(angle_all).move((width/2, height/2))

    for t in t2:
        angle = progress * 2*np.pi
        t.rotate_around(-min(angle, 2*np.pi * 2/3), t.points(local=True)[1])
        if angle > 2*np.pi * 2/3:
            t.rotate_around(-min(angle - 2*np.pi * 2/3, 2*np.pi * 1/3), t.points(local=True)[2])

    for t in t3:
        i = 0
        angle = progress * 2*np.pi * 2
        while angle > 0:
            t.rotate_around(min(angle, 2*np.pi * 1/3), t.points(local=True)[i%3])
            angle -= 2*np.pi * 1/3; i -= 1

            if angle > 0:
                t.rotate_around(min(angle, 2*np.pi * 2/3), t.points(local=True)[i%3])
                angle -= 2*np.pi * 2/3; i -= 1

    for t in t4:
        i = 1
        angle = progress * 2*np.pi * 4
        while angle > 0:
            t.rotate_around(-min(angle, 2*np.pi * 2/3), t.points(local=True)[i%3])
            angle -= 2*np.pi * 2/3; i += 1

            if angle > 0:
                t.rotate_around(-min(angle, 2*np.pi * 1/3), t.points(local=True)[i%3])
                angle -= 2*np.pi * 1/3; i += 1

    for t in t5:
        i = 0
        angle = progress * 2*np.pi * 8
        while angle > 0:
            t.rotate_around(min(angle, 2*np.pi * 1/3), t.points(local=True)[i%3])
            angle -= 2*np.pi * 1/3; i -= 1

            if angle > 0:
                t.rotate_around(min(angle, 2*np.pi * 2/3), t.points(local=True)[i%3])
                angle -= 2*np.pi * 2/3; i -= 1

    # Render
    t1.draw(            surface, s=.2, f=.1, w=2.5)
    for t in t2: t.draw(surface, s=.4, f=.2, w=2.0)
    for t in t3: t.draw(surface, s=.6, f=.3, w=1.5)
    for t in t4: t.draw(surface, s=.8, f=.4, w=1.0)
    for t in t5: t.draw(surface, s=1., f=.5, w=0.5)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)

