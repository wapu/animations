import numpy as np
import gizeh as gz
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from xr import *


name = 'xr_spinning_arcs'
width, height = 768, 768
duration = 6


xr = get_extinction_symbol_contours(radius=0.38*width, center=(width/2, height/2 + 20))
xr = geo.Polygon(xr[0], holes=xr[1:])


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    center = width/2, height/2 - 18

    circles = [geo.Point(center).buffer(r, resolution=32) for r in np.arange(5, 0.8 * width, 10)]
    p = [interval_progresses(progress + offset, 6, 'hermite') for offset in np.linspace(0, 1/3, len(circles))[::-1]]
    angles = [hermite(hermite(p[i][2] - p[i][5])) * 2*np.pi for i in range(len(p))]

    arcs = []
    for i, c in enumerate(circles):
        s = xr.intersection(c.exterior)
        if isinstance(s, geo.LineString):
            arcs.append((s, angles[i]))
        elif isinstance(s, geo.MultiLineString):
            arcs.extend([(arc, angles[i]) for arc in s])

    for arc, angle in arcs:
        coords = np.array(arc.coords)
        rotate_around(coords, angle, center)
        gz.polyline(points=coords, stroke=(1,1,1), stroke_width=5, line_cap='round').draw(surface)


    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
