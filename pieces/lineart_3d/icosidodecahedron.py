import numpy as np
from scipy.spatial import distance_matrix

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from project_3d import *
from icosphere import *


name = 'icosidodecahedron'
width, height = 1024, 1024
duration = 3



verts_, faces = icosphere(0, return_faces=True)
A = adjacency_from_faces(len(verts_), faces)
index_edges = index_edges_from_A(A)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    points = np.array(verts_) * 0.5

    # project to screen with rotated camera
    points = np.concatenate([points, np.ones((len(points),1))], axis=1).T
    C = get_camera_matrix(t_z=np.pi/2 + 1, t_x=-2*np.pi * progress)
    points, z = project(C, points, (width, height))

    # switch from points to lines
    lines = np.array([(points[i], points[j]) for (i,j) in index_edges])
    z_lines = np.array([(z[i] + z[j])/2 for (i,j) in index_edges])

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
    # genererate_points()
    # solve_tsp()

    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
