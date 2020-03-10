import numpy as np
import gizeh as gz
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from xr import *


name = 'xr_offset_contours'
width, height = 768, 768
duration = 2


xr = get_extinction_symbol_contours(radius=0.3*width, center=(width/2, height/2))
xr = geo.Polygon(xr[0], holes=xr[1:])


def draw(b, color, surface):
    if isinstance(b, geo.Polygon):
        if b.exterior is not None:
            gz.polyline(points=b.exterior.coords, stroke=color, stroke_width=2.5).draw(surface)
        for it in b.interiors:
            gz.polyline(points=it.coords, stroke=color, stroke_width=2.5).draw(surface)
    elif isinstance(b, geo.MultiPolygon):
        for poly in b:
            draw(poly, color, surface)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    for i in range(1,20):
        b = xr.buffer(5*(i+progress) + 2, resolution=100).buffer(-2)
        color = [1-((i+progress)/20)]*3
        draw(b, color, surface)

    b = xr.buffer(5*(0.5 + 0.5*np.cos((progress)*2*np.pi)) + 2, resolution=100).buffer(-2)
    draw(b, (1,1,1), surface)


    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
