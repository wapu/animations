import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *
from project_3d import *


name = 'lineart_3d_spiral_ring_double'
width, height = 768, 768
duration = 4

# circle
r_0 = 0.5
base_0 = np.linspace(0, 2*np.pi, 7000)
x = r_0 * np.sin(base_0)
y = r_0 * np.cos(base_0)
z = np.ones(base_0.size) * 0.2
spiral_0 = np.vstack([x, y, z, np.ones(base_0.size)])

loops_1 = 10
base_1 = np.linspace(-loops_1*np.pi, loops_1*np.pi, base_0.size)
loops_2 = 300
base_2 = np.linspace(-loops_2*np.pi, loops_2*np.pi, base_0.size)


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 4, 'hermite')

    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    # first level spiral
    r_1 = 0.2 * (p[0] - p[2])
    spiral_1 = np.array(spiral_0)
    spiral_1[2] += r_1 * np.sin(base_1)
    spiral_1[:2] += norm(-spiral_0[:2], axis=0) * r_1 * np.cos(base_1)

    # second level spiral
    r_2 = 0.03 * (p[1] + p[2] - 2*p[3])
    points = np.array(spiral_1)
    if r_1 > 0:
        to_center = norm(spiral_1[:3] - spiral_0[:3], axis=0)
    else:
        to_center = norm(spiral_0[:3], axis=0)
    to_next = norm(np.roll(spiral_1[:3], 1) - spiral_1[:3], axis=0)
    points[:3] += np.cross(to_next, to_center, axis=0) * r_2 * np.sin(base_2)
    points[:3] += to_center * r_2 * np.cos(base_2)

    # project to screen
    C = get_camera_matrix(t_x=np.pi/4, t_z=2*np.pi * progress * 2 / loops_1, z=1.2)
    points, z = project(C, points, (width, height))

    # switch from points to lines and sort by depth
    lines = np.array([(points[i], points[(i+1)%len(points)]) for i in range(len(points))])
    z_lines = np.array([ (z[i] + z[(i+1)%len(z)]) / 2 for i in range(len(z))])
    sort_indices = np.argsort(z_lines)
    lines = lines[sort_indices]
    z_lines = z_lines[sort_indices]

    # relative depth for shading
    z_min, z_max = z_lines.min(), z_lines.max()
    z_ratios = (z_lines - z_min) / (z_max - z_min)

    # draw lines
    for i in range(len(lines)):
        gz.polyline(points=lines[i],
                    stroke_width=(3 + 3 * z_ratios[i]) / (1 + 1.5 * (p[1] + p[2] - 2*p[-1])),
                    stroke=[0.3 + 0.7 * z_ratios[i]]*3,
                    line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, t=1.5)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
