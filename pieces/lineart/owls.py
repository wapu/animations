import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'lineart_owls'
width, height = 768, 768
duration = 3


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    progress = t / duration
    p = interval_progresses(progress, 2, 'none')

    radius = 300
    center = (width/2, height/2)

    n_sides = 9
    n_points = 50

    C_outer = get_circle_coordinates(n_sides, radius, center)
    rotate_around(C_outer, -2*np.pi/n_sides + 2*np.pi * progress/n_sides, center)

    C_inner = get_circle_coordinates(n_sides // 3, radius * (1 - p[0] + p[1]), center)
    if progress <= 0.5:
        rotate_around(C_inner, 2*np.pi * progress/9, center)
    else:
        rotate_around(C_inner, 2*np.pi * (progress-1)/9, center)

    points_outer = []
    points_inner = []
    for i in range(n_sides):
        points_outer.append(divide_line(C_outer[i], C_outer[(i+1) % n_sides], n_points)[:-1,:])
        if progress <= 0.5:
            points_inner.append(divide_line(C_outer[i], C_inner[i//3], n_points))
        else:
            points_inner.append(divide_line(C_outer[i], C_inner[((i+1)//3) % (n_sides//3)], n_points))

    for i in range(n_points-1):
        opacity = 0.25 + 0.5 * (float(i)/n_points)

        for j in range(n_sides):
            gz.polyline(points=[points_outer[j][i], points_inner[j][n_points - i - 1]],
                       stroke=(1,1,1, 1 - opacity), stroke_width=1).draw(surface)
            gz.polyline(points=[points_outer[j][i], points_inner[(j+1) % n_sides][i]],
                       stroke=(1,1,1, opacity), stroke_width=1).draw(surface)

    for j in range(n_sides):
        gz.polyline(points=[points_outer[j][0], points_outer[(j+1) % n_sides][0]],
                   stroke=(1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
