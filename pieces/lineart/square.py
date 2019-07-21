import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'lineart_square'
width, height = 768, 768
duration = 3


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t / duration
    p = interval_progresses(progress, 2, 'none')

    radius = (300 + 30 * (p[0] - p[1]))
    center = (width/2, height/2)

    n_sides = 4
    n_points = 100

    C = get_circle_coordinates(n_sides, radius, center)
    rotate_around(C, 2*np.pi * progress / n_sides, center)
    points = []
    for i in range(n_sides):
        points.append(divide_line(C[i,:], C[(i+1) % n_sides,:], n_points)[:-1,:])

    for i in range(n_points-1):
        opacity = 0.1 + 0.6 * ((i / n_points + progress) % 1.0)

        for j in range(n_sides):
            gz.polyline(points=[points[j][i], points[(j+2) % n_sides][i]],
                       stroke=(1,1,1,opacity), stroke_width=1).draw(surface)

    for j in range(n_sides):
        gz.polyline(points=[points[j][0], points[(j+1) % n_sides][0]],
                   stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
