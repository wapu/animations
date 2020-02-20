import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from project_3d import *


name = 'lineart_3d_spiral_ring_1'
width, height = 768, 768
duration = 5

# circle
r_0 = .5
base = np.linspace(0, 2*pi, 2000)
x = r_0 * np.sin(base)
y = r_0 * np.cos(base)
z = np.ones(base.size) * 0.4
points_start = np.vstack([x, y, z, np.ones(base.size)])

r_weight = (np.concatenate([hermite(np.linspace(0,1,base.size/2)), hermite(np.linspace(1,0,base.size/2))]))


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 5, ['none']*4 + ['hermite',])
    p_grow = hermite(sum(p[:-1]) / (len(p)-1))

    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    # spiral
    loops = 30 * p_grow
    base_ = np.linspace(-loops*np.pi, loops*np.pi, base.size)
    r = 0.2 * (1 - p[-1])
    points = np.array(points_start)
    points[2,:] += r * np.sin(base_) * r_weight
    points[:2,:] += norm(-points_start[:2,:], axis=0) * r * np.cos(base_) * r_weight
    points[:2,:] += norm(-points_start[:2,:], axis=0) * 0.2 * p[-1] * r_weight # correct for radius problem when r = 0

    # project to screen
    C = get_camera_matrix(t_x=np.pi/4, z=1.2)
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
                    stroke_width=3 + 3 * z_ratios[i],
                    stroke=[0.3 + 0.7 * z_ratios[i]]*3,
                    line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame, t=2)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
