import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from tsp import *


name = 'brain_tsp'
width, height = 768, 768
duration = 1


def stipple_image():
    points = stipple_image_points('brain_shape.png', n_points=1000, scale_factor=2, max_iterations=100)
    np.save('brain_shape.npy', points)


def solve_tsp():
    points = np.load('brain_shape.npy')
    write_tsp('brain.tsp', points)
    run_linkern('brain.tsp', 'brain.cyc', '../../tools/linkern.exe')
    postprocess_cyc('brain_shape.npy', 'brain.cyc',
                    'brain_processed.npy', (width, height), radius=110/128, segment_length=3)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    n_segments = 3
    radius = 3

    progress = t / duration
    weights = equidistant_weight_functions(progress, n_segments+1, 'none')

    points = np.load('brain_processed.npy')[::2,:] + np.array([0, 15])

    n_extra_segments = len(points) % n_segments
    if n_extra_segments > 0:
        points = points[:-n_extra_segments,:]

    for i in range(0, len(points), n_segments):
        point = sum([weights[j] * points[(i+j) % len(points), :] for j in range(len(weights))])
        gz.circle(r=radius, xy=point, fill=(.4,.4,.4), stroke=(1,1,1), stroke_width=1).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # stipple_image()
    # solve_tsp()

    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
