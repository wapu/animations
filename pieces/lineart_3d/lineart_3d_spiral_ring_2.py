import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from project_3d import *


name = 'lineart_3d_spiral_ring_2'
width, height = 768, 768
duration = 15

# underlying ring
n_points = 2000
r_0 = 0.5
ring_base = np.linspace(-(1/2) * 2*np.pi, (1+1/2) * 2*np.pi, 2*n_points)
ring_ = np.vstack([r_0 * np.sin(ring_base), r_0 * np.cos(ring_base), 0.2*np.ones(ring_base.size), np.ones(ring_base.size)])


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 15, ['none']*14 + ['hermite',])
    p_grow = hermite(sum(p[:-1]) / (len(p)-1))

    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    # parameters
    n_loops = 15 * p_grow
    r_1 = 0.2 * (1 - p[-1])

    # angles for trigonometric functions
    base_ = np.linspace(-2*n_loops * np.pi, 2*n_loops * np.pi, 2*n_points)

    # spiral offsets from ring
    z = r_1 * np.sin(base_)
    xy = norm(-ring_[:2,:], axis=0) * r_1 * np.cos(base_)
    xy += norm(-ring_[:2,:], axis=0) * 0.2 * p[-1] # correct for radius problem when r_1 = 0
    offset = np.vstack([xy, z, np.zeros(base_.size)])

    # smooth between non-matching spiral arms
    interp = hermite(np.linspace(.5,0,n_points//2))
    offset[:,n_points//2 : n_points] = \
        (1 - interp) * offset[:,n_points//2 : n_points] + interp * offset[:,-n_points//2 : ]
    offset[:,-n_points : -n_points//2] = \
        (1 - interp[::-1]) * offset[:,-n_points : -n_points//2] + interp[::-1] * offset[:, : n_points//2]
    offset = offset[:, n_points//2 : -n_points//2]
    ring = ring_[:, n_points//2 : -n_points//2]

    # final points
    points = ring + offset

    # project to screen
    C = get_camera_matrix(t_x=np.pi/4, t_z=2*np.pi * hermite(progress), z=1.15)
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
    save_poster(name, make_frame, t=8.9)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
