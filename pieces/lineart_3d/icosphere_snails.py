import numpy as np
from scipy.spatial import distance_matrix

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from tsp import *
from project_3d import *
from icosphere import *


name = 'icosphere_snails'
width, height = 1024, 1024
duration = 4 * 8



def genererate_points():
    points = icosphere(3)
    np.save(f'{name}.npy', points)


def solve_tsp():
    points = np.load(f'{name}.npy')
    write_tsp_dist(f'{name}.tsp', distance_matrix(points, points) * 10000)
    run_linkern(f'{name}.tsp', f'{name}.cyc', '../../tools/linkern.exe')
    order = read_cyc(f'{name}.cyc')
    points = points[np.array(order)]
    np.save(f'{name}.npy', points)



# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    # get points
    r = 0.5
    points = np.load(f'{name}.npy') * r

    # line progress
    segments = interval_progresses(progress, duration, ['ease_out', 'ease_in']*(duration//2))
    phase = np.floor(sum(segments)) % 4
    f_even = sum(segments[::4] + segments[1::4]) % 1
    f_odd = sum(segments[2::4] + segments[3::4]) % 1

    # project to screen with rotated camera
    points = np.concatenate([points, np.ones((len(points),1))], axis=1).T
    C = get_camera_matrix(t_z=np.pi/2 + 1, t_x=-2*np.pi * progress)
    points, z = project(C, points, (width, height))

    # switch from points to lines
    lines = np.array([(points[i], points[(i+1)%len(points)]) for i in range(len(points))])
    z_lines = np.array([ (z[i] + z[(i+1)%len(z)]) / 2 for i in range(len(z))])
    # split into even and odd lines
    l_even = lines[::2]; z_even = z_lines[::2]
    l_odd = lines[1::2]; z_odd = z_lines[1::2]
    # sort each by depth
    i_even = np.argsort(z_even)
    l_even = l_even[i_even]
    z_even = z_even[i_even]
    i_odd = np.argsort(z_odd)
    l_odd = l_odd[i_odd]
    z_odd = z_odd[i_odd]

    # relative depth for shading
    z_min, z_max = z_lines.min(), z_lines.max()
    z_middle = (z_min + z_max)/2
    e_ratios = (r + z_even - z_middle) / (2*r)
    o_ratios = (r + z_odd - z_middle) / (2*r)

    # draw lines
    for i in range(len(l_even)):
        # even
        p0, p1 = l_even[i]
        mid = p0 * (1 - f_even) + p1 * f_even
        end = p0 if (phase == 1) else p1
        gz.polyline(points=[mid, end],
                    stroke_width=(3 + 3 * e_ratios[i]),
                    stroke=[0.2 + 0.8 * e_ratios[i]]*3,
                    line_cap='round').draw(surface)
        # odd
        p0, p1 = l_odd[i]
        mid = p0 * (1 - f_odd) + p1 * f_odd
        end = p0 if (phase == 3) else p1
        gz.polyline(points=[mid, end],
                    stroke_width=(3 + 3 * o_ratios[i]),
                    stroke=[0.2 + 0.8 * o_ratios[i]]*3,
                    line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # genererate_points()
    # solve_tsp()

    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
