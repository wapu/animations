import numpy as np
from scipy.spatial import distance_matrix

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from tsp import *
from project_3d import *
from icosphere import *


name = 'globe_tsp'
width, height = 768, 768
duration = 300



def genererate_points():
    # points = np.random.randn(2000, 3)
    # points /= np.sqrt(np.sum(np.square(points), axis=1, keepdims=True))
    points = icosphere(4)
    np.save('globe.npy', points)


def solve_tsp():
    points = np.load('globe.npy')
    write_tsp_dist('globe.tsp', distance_matrix(points, points) * 10000)
    run_linkern('globe.tsp', 'globe.cyc', '../../tools/linkern.exe')
    postprocess_cyc('globe.npy', 'globe.cyc', 'globe_processed.npy',
                    None, segment_length=0.02, normalize_points=False)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    # get points
    r = 0.6
    points = np.load('globe_processed.npy')[::2] * r
    points = np.roll(points, shift=-int(progress * len(points)) - 8, axis=0)
    points = np.concatenate([points]*5, axis=0)
    points *= np.linspace(0, 1, len(points))[:,None]
    thickness = np.linspace(0, 1, len(points))
    points = np.concatenate([points, np.ones((len(points),1))], axis=1).T

    # project to screen with rotated camera
    x, y, z = points[:-1,-1]
    t_x = np.pi/12 + np.cos(2*np.pi*progress)*np.pi/24
    t_z = np.arctan2(y,x)
    t_y = np.arctan2(np.sqrt(x*x+y*y),z) + np.sin(2*np.pi*progress)*np.pi/16
    C = get_camera_matrix(t_x=t_x, t_y=t_y, t_z=t_z)
    points, z = project(C, points, (width, height))

    # switch from points to lines and sort by depth
    lines = np.array([(points[i], points[i+1]) for i in range(len(points) - 1)])
    z_lines = np.array([ (z[i] + z[i+1]) / 2 for i in range(len(z) - 1)])
    sort_indices = np.argsort(z_lines)
    lines = lines[sort_indices]
    z_lines = z_lines[sort_indices]
    thickness = thickness[sort_indices]

    # relative depth for shading
    z_min, z_max = z_lines.min(), z_lines.max()
    z_middle = (z_min + z_max)/2
    z_ratios = (r + z_lines - z_middle) / (2*r)

    # draw lines
    for i in range(len(lines)):
        gz.polyline(points=lines[i],
                    stroke_width=(3 + 3 * z_ratios[i]) * thickness[i],
                    stroke=[0.2 + 0.8 * z_ratios[i] * thickness[i]]*3,
                    line_cap='round').draw(surface)
    gz.circle(xy=points[-1], r=6, stroke=None, fill=(1,1,1)).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # genererate_points()
    # solve_tsp()

    # save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
