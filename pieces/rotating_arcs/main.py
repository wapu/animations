import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *


name = 'rotating_arcs'
width, height = 768, 768
duration = 1.5


# Coordinates for polyline of one arc
def get_arc_poly(inner_r=300, outer_r=390):
    points = []
    for deg in range(90):
        rad = np.pi/180 * deg
        points.append((np.sin(rad) * outer_r - outer_r, np.cos(rad) * outer_r))
    for deg in range(90):
        rad = np.pi/180 * (90 - deg)
        points.append((np.sin(rad) * inner_r - inner_r, np.cos(rad) * inner_r))
    return points

points = get_arc_poly()


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    g = gz.Group(
          [gz.polyline(points=points, fill=(1,1,1,.5)).rotate(np.pi/180 * i - (2*np.pi / duration) * t * (10./360))
               for i in range(0,360,10)]
        + [gz.polyline(points=points, fill=(1,1,1,.5)).scale(rx=-1, ry=1).rotate(np.pi/180 * i + (2*np.pi / duration) * t * (10./360))
               for i in range(0,360,10)]
        + [gz.circle(r=.03 * width, fill=(0,0,0)),
           gz.circle(r=.65 * width, stroke_width=.5 * width),
           gz.circle(r=.40 * width, stroke_width=4, stroke=(1,1,1))]
        )

    g.translate([width/2, height/2]).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration)
    convert_to_mp4(name)