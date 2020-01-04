import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'spiral_tiles'
width, height = 768, 768
duration = 7


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration
    progress = interval_progresses(progress, 2, 'hermite')

    revolutions = 20
    max_theta = revolutions * 2*np.pi
    raster_distance = 0.03 * np.pi
    tile_width = 2*np.pi / (19 + 2*(progress[0] - progress[1]))

    # Spiral sections
    for start in np.arange((5 - 2*progress[1]) * 2*np.pi, max_theta - tile_width, 2*tile_width):
        p = []
        for theta in np.arange(start, start + tile_width, raster_distance):
            r = 348 * hermite(ease_in(hermite(theta/max_theta)))
            p.append((polar_to_cartesian(r, theta)))
        for theta in np.arange(start + tile_width, start, -raster_distance):
            r = 348 * hermite(ease_in(hermite((theta - 2*np.pi)/max_theta)))
            p.append((polar_to_cartesian(r, theta)))
        p = np.array(p)
        p = 0.95 * p + 0.05 * p.mean(axis=0)
        p = [de_boor(t, p, 3) for t in np.linspace(0, len(p), 10*len(p))]
        gz.polyline(points=p, stroke_width=0, fill=(1,1,1,1), close_path=True).translate([width/2, height/2]).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
