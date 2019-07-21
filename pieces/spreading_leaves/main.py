import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'spreading_leaves'
width, height = 768, 768
duration = 6


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    n_leaves = 4 * 8
    coord_radius = 165
    C_base = get_circle_coordinates(n_leaves, coord_radius)
    angles = [0, np.pi/8, 2*np.pi/8, 3*np.pi/8]

    progress = t / duration
    p_shrink = ease_in( interval_progress(progress, (0.0, 0.5)))
    p_grow   = ease_out(interval_progress(progress, (0.5, 1.0)))

    for j in range(4):
        R = get_rotation_matrix(angles[j])
        C = C_base.dot(R) + [width/2, height/2]

        if j%2 == 0: opacity = 0.1
        else: opacity = 0.3

        for i in range(0, n_leaves, n_leaves//4):
            p1, p2 = C[(i-1)%n_leaves], C[(i+1)%n_leaves]
            p11 = p1 + (p1 - p2) * (-0.5 + 6*(p_grow - p_shrink))
            p22 = p2 + (p2 - p1) * (-0.5 + 6*(p_grow - p_shrink))
            radius = np.sqrt(np.sum(np.square(p11 - [width/2, height/2])))

            c1 = geo.point.Point(p11[0], p11[1]).buffer(radius)
            c2 = geo.point.Point(p22[0], p22[1]).buffer(radius)
            leaf = c1.intersection(c2)
            gz.polyline(points=leaf.exterior.coords, stroke_width=0, fill=(1,1,1,opacity)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
