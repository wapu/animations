import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from tsp import *


name = 'celtic_knot_tsp'
width, height = 768, 768
duration = 60


def stipple_image():
    points = stipple_image_points('celtic_knot_shape.png', n_points=6000, scale_factor=2, max_iterations=100)
    np.save('celtic_knot_shape.npy', points)


def solve_tsp():
    points = np.load('celtic_knot_shape.npy')
    write_tsp('celtic_knot.tsp', points)
    run_linkern('celtic_knot.tsp', 'celtic_knot.cyc', '../../tools/linkern.exe')
    postprocess_cyc('celtic_knot_shape.npy', 'celtic_knot.cyc',
                    'celtic_knot_processed.npy', (width, height), radius=100/128, segment_length=5)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    color = np.array([1,1,1])

    progress = t / duration
    p = interval_progresses(progress, 2, 'none')

    points = np.load('celtic_knot_processed.npy')

    head = int(round(len(points) * progress))
    tail_length = len(points)/6

    for i in range(len(points)):
        i_ = i if (i < head) else (i - len(points))
        segment_color =  color * (1 - .5 * min(1, (head - i_) / tail_length))
        gz.polyline(points=(points[i,:], points[(i+1) % len(points),:]),
                    stroke=segment_color, stroke_width=3, line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # stipple_image()
    solve_tsp()

    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
