import numpy as np
import gizeh as gz

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from project_3d import *


name = 'lineart_3d_twisting_ring'
width, height = 768, 768
duration = 12

r = .5
base = np.linspace(-r, r, 1000)
amplitudes = np.sqrt(r*r - np.square(base))


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 4, ['ease_out', 'ease_in', 'ease_out', 'ease_in'])

    surface = gz.Surface(width, height)
    center = np.array((width/2, height/2))

    # calculate 3D point coordinates
    angles = base * 2*np.pi * (p[0] - p[1] - p[2] + p[3]) * 5
    x = base
    y = np.cos(angles) * amplitudes
    z = np.sin(angles) * amplitudes

    # zip up points
    points_1 = np.vstack([x, y, z, np.ones(base.size)])
    points_2 = np.vstack([-x, -y, z, np.ones(base.size)])
    points = np.concatenate([points_1[:,:-1], points_2[:,:-1]], axis=1)

    # project to screen
    C = get_camera_matrix(t_z=np.pi/4, t_x=2*np.pi * progress)
    points, z = project(C, points, (width, height))

    # switch from points to lines and sort by depth
    lines = np.array([(points[i], points[(i+1)%len(points)]) for i in range(len(points))])
    z_lines = np.array([ (z[i] + z[(i+1)%len(z)]) / 2 for i in range(len(z))])
    sort_indices = np.argsort(z_lines)
    lines = lines[sort_indices]
    z_lines = z_lines[sort_indices]

    # relative depth for shading
    z_min, z_max = z_lines.min(), z_lines.max()
    z_middle = (z_min + z_max)/2
    z_ratios = (r + z_lines - z_middle) / (2*r)

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
