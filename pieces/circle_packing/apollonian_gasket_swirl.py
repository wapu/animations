import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from apollonius import *
from geometry import *


name = 'apollonian_gasket_swirl'
width, height = 768, 768
duration = 15
min_radius = 1.5 # 3


def make_frame(t):
    surface = gz.Surface(width, height)
    p = 2*np.pi * ((t+0.8) / duration)

    c = get_circle_coordinates(3, radius=width/4, center=(0,0))
    c *= [[1.5 + np.sin(p)], [1.5 + np.sin(p + 2*np.pi/3)], [1.5 + np.sin(p + 4*np.pi/3)]]
    c += [width/2, height/2]
    x1, y1, x2, y2, x3, y3 = c.reshape(-1)
    r1, r2, r3 = tangential_radii_from_centers(x1, y1, x2, y2, x3, y3)

    (xl,yl,rl), (xr,yr,rr) = apollonian_circles_(x1,y1,r1,x2,y2,r2,x3,y3,r3)
    if np.abs(rl) < np.abs(rr):
        outer = ApollonianCircle(xr, yr, rr, [])
    else:
        outer = ApollonianCircle(xl, yl, rl, [])
    inner1 = ApollonianCircle(x1, y1, r1, [])
    inner2 = ApollonianCircle(x2, y2, r2, [])
    inner3 = ApollonianCircle(x3, y3, r3, [])
    outer.neighbors = [inner1, inner2, inner3]
    inner1.neighbors = [outer, inner2, inner3]
    inner1.neighbors = [inner1, outer, inner3]
    inner1.neighbors = [inner1, inner2, outer]

    # Normalize outer circle to screen
    dx = -outer.x
    dy = -outer.y
    s = 330/np.abs(outer.r)
    for c in [inner1, inner2, inner3, outer]:
        c.x = (c.x+dx)*s
        c.y = (c.y+dy)*s
        c.r *= s

    G = ApollonianGasket(outer, inner1, inner2, inner3)
    G.fill_gasket(min_radius=min_radius)

    max_r = np.abs(outer.r)
    for c in G.circles[1:]:
        gz.circle(xy=(width/2+c.x, height/2+c.y), r=np.abs(c.r)*0.96 - 0.5,
                  fill=[1-.85*(c.r/max_r)**0.5]*3).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    pass
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
