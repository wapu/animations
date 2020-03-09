import numpy as np
from queue import PriorityQueue
from itertools import combinations


def tangential_radii_from_centers(x1, y1, x2, y2, x3, y3):
    d12 = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    d13 = np.sqrt((x1 - x3)**2 + (y1 - y3)**2)
    d23 = np.sqrt((x2 - x3)**2 + (y2 - y3)**2)
    r1 = (d12 + d13 - d23) / 2
    r2 = (d12 + d23 - d13) / 2
    r3 = (d13 + d23 - d12) / 2
    return r1, r2, r3


def apollonian_circles_(x1, y1, r1, x2, y2, r2, x3, y3, r3):
    C_2 = (r1*r1 - r2*r2 - x1*x1 + x2*x2 - y1*y1 + y2*y2) / 2
    C_3 = (r1*r1 - r3*r3 - x1*x1 + x3*x3 - y1*y1 + y3*y3) / 2

    # Switch x and y if equations would become unstable otherwise
    if (y1 - y2 < 1e-8):
        flip = True
        x1, y1, x2, y2, x3, y3 = y1, x1, y2, x2, y3, x3
    else:
        flip = False

    # x = A_x * r + b_x
    h = (y3-y1)/(y2-y1)
    A_x = ((r1-r3) - ((r1-r2)*h)) / ((x3-x1) - ((x2-x1)*h))
    b_x = (C_3 - C_2*h) / ((x3-x1) - (x2-x1)*h)
    # y = A_y * r + b_y
    A_y = (r1-r2 - A_x*(x2-x1)) / (y2-y1)
    b_y = (C_2 - b_x*(x2-x1)) / (y2-y1)

    # Radii of the two solution circles
    p_half = (r1 - A_x*b_x + A_x*x1 - A_y*b_y + A_y*y1) / (1 - A_x*A_x - A_y*A_y)
    q = (r1*r1 - b_x*b_x + 2*b_x*x1 - x1*x1 - b_y*b_y + 2*b_y*y1 - y1*y1) / (1 - A_x*A_x - A_y*A_y)
    r1 = -p_half + np.sqrt(p_half*p_half - q)
    r2 = -p_half - np.sqrt(p_half*p_half - q)

    # Switch x and y back if necessary
    if flip is False:
        return (A_x*r1+b_x, A_y*r1+b_y, r1), (A_x*r2+b_x, A_y*r2+b_y, r2)
    else:
        return (A_y*r1+b_y, A_x*r1+b_x, r1), (A_y*r2+b_y, A_x*r2+b_x, r2)


def apollonian_circles(c1, c2, c3):
    return apollonian_circles_(c1.x, c1.y, c1.r, c2.x, c2.y, c2.r, c3.x, c3.y, c3.r)



class ApollonianCircle():

    def __init__(self, x, y, r, parents=[]):
        self.x = x
        self.y = y
        self.r = r
        self.parents = parents
        self.neighbors = [p for p in parents]
        self.children = []
        self.id = -1

    def intersects(self, other):
        tol = min(self.r, other.r) * 0.01
        return (self.r + other.r)**2 - tol > (self.x - other.x)**2 + (self.y - other.y)**2

    def touches(self, other, tol=1e-3):
        return (self.r + other.r)**2 - (self.x - other.x)**2 + (self.y - other.y)**2 < tol**2

    def __lt__(self, other):
        return self.r > other.r

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id


class ApollonianGasket():

    def __init__(self, outer, inner1, inner2, inner3):
        self.circles = []
        for c in [outer, inner1, inner2, inner3]:
            self.add_circle(c)
        self.queue = PriorityQueue()
        self.done = set([])
        self.add_candidates([outer, inner1, inner2, inner3])

    def make_candidates(self, c1, c2, c3):
        n1, n2 = apollonian_circles(c1, c2, c3)
        n1 = ApollonianCircle(*n1, parents=[c1, c2, c3])
        n2 = ApollonianCircle(*n2, parents=[c1, c2, c3])
        return n1, n2

    def add_candidates(self, circles):
        combis = set(combinations(circles, 3))
        for combi in combis - self.done:
            n1, n2 = self.make_candidates(*combi)
            self.queue.put(n1)
            self.queue.put(n2)
            self.done.add(combi)

    def add_candidates_all(self, min_radius = 0.1):
        combis = set(combinations([c for c in self.circles if c.r > min_radius], 3))
        for combi in combis - self.done:
            n1, n2 = self.make_candidates(*combi)
            self.queue.put(n1)
            self.queue.put(n2)
            self.done.add(combi)

    def add_circle(self, c):
        self.circles.append(c)
        c.id = len(self.circles)

    def fill_gasket(self, min_radius=0.05):
        while self.queue.qsize() > 0:
            # Take largest candidate from queue
            c = self.queue.get()
            # Check that it doesn't intersect any existing circles
            if not any([c.intersects(other) for other in self.circles[1:]]):
                # Add to circle list
                self.add_circle(c)
                # Register with neighbors
                for neighbor in c.neighbors:
                    neighbor.neighbors.append(c)
                # Generate new candidates
                if c.r > min_radius:
                    self.add_candidates([c, *c.neighbors])
                # Register with parents
                for parent in c.parents:
                    parent.children.append(c)


if __name__ == '__main__':

    np.random.seed(12)
    x1, y1, x2, y2, x3, y3 = 0.5*np.random.randn(6) + np.array([-1.5, 1.5, 1, 1, -1, -1])
    r1, r2, r3 = tangential_radii_from_centers(x1, y1, x2, y2, x3, y3)
    # r1 = 0.75*r1
    # r2 = 0.75*r2
    # r3 = 0.75*r3

    import gizeh as gz
    surface = gz.Surface(800,800)
    gz.square(xy=(400,400), l=800, fill=(0,0,0)).draw(surface)
    (xl,yl,rl), (xr,yr,rr) = apollonian_circles_(x1,y1,r1,x2,y2,r2,x3,y3,r3)

    outer = ApollonianCircle(xr, yr, rr, [])
    inner1 = ApollonianCircle(x1, y1, r1, [])
    inner2 = ApollonianCircle(x2, y2, r2, [])
    inner3 = ApollonianCircle(x3, y3, r3, [])
    outer.neighbors = [inner1, inner2, inner3]
    inner1.neighbors = [outer, inner2, inner3]
    inner1.neighbors = [inner1, outer, inner3]
    inner1.neighbors = [inner1, inner2, outer]

    G = ApollonianGasket(outer, inner1, inner2, inner3)
    G.fill_gasket(min_radius=0.015)
    # for i in range(2):
    #     G.add_candidates_all()
    #     G.fill_gasket()

    max_r = max([c.r for c in G.circles])
    dx = -G.circles[0].x
    dy = -G.circles[0].y
    s = 350/(80*np.abs(G.circles[0].r))
    for c in G.circles[1:]:
        gz.circle(xy=(400+80*(c.x+dx)*s, 400+80*(c.y+dy)*s), r=80*np.abs(c.r)*s - .5,
                  fill=[1-.5*(c.r/max_r)**0.3]*3).draw(surface)
        # if c.r > 0.2:
        #     gz.text(str(c.id), fontfamily='Arial', fontsize=16, fill=(0,0,0), xy=(400+80*c.x, 400+80*c.y)).draw(surface)

    surface.write_to_png('apollonius.png')
