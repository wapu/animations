import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'torus_of_circles'
width, height = 768, 768
duration = 4


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 2, interpolation='hermite')

    surface = gz.Surface(width, height)
    center = (width/2, height/2)

    r_torus = 0.17*width + 0.01*width*(p[0] - p[1])
    r_circles = 0.25*width - 0.01*width*(p[0] - p[1])

    c1 = get_circle_coordinates(30, r_torus, center)
    c2 = get_circle_coordinates(15, r_torus, center)
    c3 = get_circle_coordinates(15, r_torus, center)

    rotate_around(c1, 2*np.pi * (1/60 + (p[0] + p[1])/60), center)
    rotate_around(c2, 2*np.pi * (1/30 - (p[0] + p[1])/30), center)

    for c in c1:
        gz.circle(xy=c, r=r_circles, stroke=(1,1,1,.2), stroke_width=6).draw(surface)
    for c in c2:
        gz.circle(xy=c, r=r_circles, stroke=(1,1,1,.3), stroke_width=4).draw(surface)
    for c in c3:
        gz.circle(xy=c, r=r_circles, stroke=(1,1,1,1), stroke_width=2).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
