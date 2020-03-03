import numpy as np
from queue import PriorityQueue


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

    return (A_x*r1+b_x, A_y*r1+b_y, r1), (A_x*r2+b_x, A_y*r2+b_y, r2)

def apollonian_circles(c1, c2, c3):
    return apollonian_circles_(c1.x, c1.y, c1.r, c2.x, c2.y, c2.r, c3.x, c3.y, c3.r)


def apollonian_gasket(C1, C2, C3, surface, rec_limit):
    if rec_limit == 0:
        return
    new1, new2 = apollonian_circles(*C1, *C2, *C3)
    if new1[2] > 0.01 and new1[2] < np.abs(C1[2]) and new1[2] < np.abs(C2[2]) and new1[2] < np.abs(C3[2]):
        gz.circle(xy=(400+80*new1[0], 400+80*new1[1]), r=80*new1[2], stroke_width=1, stroke=(.5,.5,.5)).draw(surface)
        apollonian_gasket(C1, C2, new1, surface, rec_limit - 1)
        apollonian_gasket(C1, C3, new1, surface, rec_limit - 1)
        apollonian_gasket(C2, C3, new1, surface, rec_limit - 1)
    if new2[2] > 0.01 and new2[2] < np.abs(C1[2]) and new2[2] < np.abs(C2[2]) and new2[2] < np.abs(C3[2]):
        gz.circle(xy=(400+80*new2[0], 400+80*new2[1]), r=80*new2[2], stroke_width=1, stroke=(.5,.5,.5)).draw(surface)
        apollonian_gasket(C1, C2, new2, surface, rec_limit - 1)
        apollonian_gasket(C1, C3, new2, surface, rec_limit - 1)
        apollonian_gasket(C2, C3, new2, surface, rec_limit - 1)



class ApollonianCircle():

    def __init__(self, x, y, r, parents=[]):
        self.x = x
        self.y = y
        self.r = r
        self.parents = parents
        self.neighbors = [p for p in parents]

    def intersects(self, other, tol=1e-2):
        return (self.r + other.r)**2 - tol > (self.x - other.x)**2 + (self.y - other.y)**2

    def touches(self, other, tol=1e-3):
        return (self.r + other.r)**2 - (self.x - other.x)**2 + (self.y - other.y)**2 < tol**2

    def __lt__(self, other):
        return self.r > other.r

    def __eq__(self, other):
        return self.r == other.r and self.x == other.x and self.y == other.y


class ApollonianGasket():

    def __init__(self, outer, inner1, inner2, inner3):
        self.circles = [outer, inner1, inner2, inner3]
        self.queue = PriorityQueue()
        self.add_candidates(outer, inner1, inner2, inner3)

    def make_candidates(self, c1, c2, c3):
        n1, n2 = apollonian_circles(c1, c2, c3)
        n1 = ApollonianCircle(*n1, parents=[c1, c2, c3])
        n2 = ApollonianCircle(*n2, parents=[c1, c2, c3])
        return n1, n2

    def add_candidates(self, c1, c2, c3, c4):
        n1, n2 = self.make_candidates(c1, c2, c3)
        self.queue.put(n1)
        self.queue.put(n2)
        n1, n2 = self.make_candidates(c2, c3, c4)
        self.queue.put(n1)
        self.queue.put(n2)
        n1, n2 = self.make_candidates(c3, c4, c1)
        self.queue.put(n1)
        self.queue.put(n2)
        n1, n2 = self.make_candidates(c4, c1, c2)
        self.queue.put(n1)
        self.queue.put(n2)

    def get_biggest_candidate(self):
        # Take largest candidate from queue
        c = self.queue.get()
        # Check that it doesn't intersect any existing circles
        for other in self.circles[1:]:
            if c.intersects(other):
                return None
        # Register with its neighbors
        for neighbor in c.neighbors:
            neighbor.neighbors.append(c)
        # Add to circle list
        self.circles.append(c)
        return c

    def fill_gasket(self, min_radius=0.05):
        while self.queue.qsize() > 0:
            c = self.get_biggest_candidate()
            if c is not None:
                if c.r > min_radius:
                    self.add_candidates(c, *c.neighbors)


if __name__ == '__main__':

    np.random.seed(12)
    x1, y1, x2, y2, x3, y3 = 0.5*np.random.randn(6) + np.array([-1.5, 1.5, 1, 1, -1, -1])
    r1, r2, r3 = tangential_radii_from_centers(x1, y1, x2, y2, x3, y3)
    r1 = 0.75*r1
    r2 = 0.75*r2
    r3 = 0.75*r3

    import gizeh as gz
    surface = gz.Surface(800,800)
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
    for c in G.circles:
        gz.circle(xy=(400+80*c.x, 400+80*c.y), r=80*c.r, fill=(.9,.9,.9)).draw(surface)
    G.fill_gasket()
    print(G.queue.qsize())
    print(len(G.circles))
    print(len([c for c in G.circles if c.r > 0]))
    for c in G.circles:
        gz.circle(xy=(400+80*c.x, 400+80*c.y), r=80*np.abs(c.r), stroke_width=1, stroke=(0,0,0)).draw(surface)

    # apollonian_gasket((x1,y1,r1), (x2,y2,r2), (x3,y3,r3), surface, rec_limit=15)
    # apollonian_gasket((xr,yr,rr), (x2,y2,r2), (x3,y3,r3), surface, rec_limit=15)
    # apollonian_gasket((x1,y1,r1), (xr,yr,rr), (x3,y3,r3), surface, rec_limit=15)
    # apollonian_gasket((x1,y1,r1), (x2,y2,r2), (xr,yr,rr), surface, rec_limit=15)

    # gz.circle(xy=(400+80*x1, 400+80*y1), r=80*r1, stroke_width=1, stroke=(0,0,0)).draw(surface)
    # gz.circle(xy=(400+80*x2, 400+80*y2), r=80*r2, stroke_width=1, stroke=(0,0,0)).draw(surface)
    # gz.circle(xy=(400+80*x3, 400+80*y3), r=80*r3, stroke_width=1, stroke=(0,0,0)).draw(surface)

    # gz.circle(xy=(400+80*xr, 400+80*yr), r=80*np.abs(rr), stroke_width=1, stroke=(0,0,0)).draw(surface)

    surface.write_to_png('apollonius.png')
