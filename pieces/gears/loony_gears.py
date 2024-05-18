import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'loony_gears'
width, height = 768, 768
duration = 12


# Draw a single cog to the given surface
def draw_cog(surface, center, radius, n_teeth, l_teeth, fill=(0,0,0), stroke=(1,1,1),
             rotation=0, circle_offset=None):
    inner = get_circle_coordinates(3 * n_teeth, radius, center)
    rotate_around(inner, rotation, center)
    outer = get_circle_coordinates(3 * n_teeth, radius + l_teeth, center)
    rotate_around(outer, 2*np.pi / (6*n_teeth) + rotation, center)

    points = []
    for i in range(n_teeth):
        points.extend([inner[3*i, :],
                       inner[(3*i+1) % (3*n_teeth), :],
                       outer[(3*i+1) % (3*n_teeth), :],
                       outer[(3*i+2) % (3*n_teeth), :],
                       inner[(3*i+3) % (3*n_teeth), :]
                      ])

    if circle_offset > 0:
        circle = get_circle_coordinates(int(radius), radius + circle_offset + l_teeth, center)
        gz.polyline(points=circle, close_path=True,
                    fill=fill, stroke=stroke, stroke_width=1).draw(surface)
        gz.polyline(points=points, fill=(0,0,0), stroke=stroke, stroke_width=1).draw(surface)
    else:
        circle = get_circle_coordinates(int(radius), radius + circle_offset, center)
        gz.polyline(points=points, fill=fill, stroke=stroke, stroke_width=1).draw(surface)
        gz.polyline(points=circle, close_path=True,
                    fill=(0,0,0), stroke=stroke, stroke_width=1).draw(surface)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    color = (1,1,1)

    progress = t / duration

    l_teeth = 15

    radius   = np.array([18, 9.1, 6, 5, 3]) * 13.5
    n_teeth  = np.array([37, 19, 13, 11, 7])
    offsets  = np.array([5, -5, -5, -5, -5]) * 3

    rotation = [0.0] * 5
    center   = [(0,0)] * 5
    center[0] = np.array((width/2, height/2))
    rotation[0] = 0.0

    center[1] = np.array((width/2 + radius[0] - radius[1], height/2))
    rotate_around(center[1], np.pi * (-5./35) + 2*np.pi*progress, center[0])
    rotation[1] = 2*np.pi * 1./(3*n_teeth[1]) + 2*np.pi*progress * (1 - float(n_teeth[0])/n_teeth[1])

    center[2] = np.array((width/2 + radius[0] - radius[2], height/2))
    rotate_around(center[2], np.pi * 37./36 + 2*np.pi*progress, center[0])
    rotation[2] = 2*np.pi * -1./(3*n_teeth[2]) + 2*np.pi*progress * (1 - float(n_teeth[0])/n_teeth[2])

    center[3] = np.array((width/2 + radius[0] - 2*radius[1] - radius[3] - 2*l_teeth, height/2))
    rotate_around(center[3], np.pi * 58.5/36 + 2*np.pi*progress, center[0])
    rotation[3] = 2*np.pi * -1./(3*n_teeth[3]) + 2*np.pi*progress * (1 + float(n_teeth[0])/n_teeth[3])

    center[4] = np.array((width/2 + radius[0] - radius[4], height/2))
    rotate_around(center[4], 2*np.pi * (1./4 - 0.003) + 2*np.pi*progress, center[0])
    rotation[4] = 2*np.pi * (1./(2*n_teeth[4]) + 0.01) + 2*np.pi*progress * (1 - float(n_teeth[0])/n_teeth[4])

    radius[1] -= 3
    radius[2] -= 3
    radius[4] -= 3

    shift = (center[3][0] - center[0][0], center[3][1] - center[0][1])
    fills = [(.2,.2,.2), (.3,.3,.3), (.3,.3,.3), (.2,.2,.2), (.3,.3,.3)]
    for i in range(5):
        shifted_center = (center[i][0] - shift[0], center[i][1] - shift[1])
        draw_cog(surface, shifted_center, radius[i], n_teeth[i], l_teeth,
                 fill=fills[i], rotation=rotation[i], circle_offset=offsets[i])

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
