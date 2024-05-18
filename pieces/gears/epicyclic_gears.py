import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'epicyclic_gears'
width, height = 768, 768
duration = 4


# Draw a single cog to the given surface
def draw_cog(surface, center, radius, n_teeth, l_teeth, fill=(0,0,0), stroke=(1,1,1), rotation=0, circle_offset=None):
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
    center = (width/2, height/2)

    progress = t / duration
    progress /= 7

    l_teeth = 15

    outer_radius = 333 - l_teeth
    intermediate_radius = 96 - l_teeth - 1
    inner_radius = 138

    outer_teeth = 42
    intermediate_teeth = 14
    inner_teeth = 21

    # outer
    draw_cog(surface, center, outer_radius, outer_teeth, l_teeth, fill=(.2,.2,.2), rotation=0, circle_offset=21)

    # intermediate
    n_intermediate_cogs = 7
    C = get_circle_coordinates(n_intermediate_cogs, outer_radius - intermediate_radius - 2, center)
    rotate_around(C, -2*np.pi*progress, center)
    for i in range(n_intermediate_cogs):
        draw_cog(surface, C[i,:], intermediate_radius, intermediate_teeth, l_teeth, fill=(.3,.3,.3),
                 rotation=2*np.pi*progress * (float(outer_teeth)/intermediate_teeth - 1), circle_offset=-15)

    # inner
    rotation_inner = 2*np.pi*progress * (-float(outer_teeth)/inner_teeth - 1) + 2*np.pi*(0.008)
    draw_cog(surface, center, inner_radius, inner_teeth, l_teeth, fill=(.2,.2,.2), rotation=rotation_inner, circle_offset=-15)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
