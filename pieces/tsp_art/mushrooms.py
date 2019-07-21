import numpy as np
from shapely import geometry as geo

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from tsp import *


name = 'mushrooms_tsp'
width, height = 768, 768
duration = 3


def stipple_image():
    points = stipple_image_points('mushrooms_shape.png', n_points=3500, scale_factor=2, max_iterations=100)
    np.save('mushrooms_shape.npy', points)


def solve_tsp():
    points = np.load('mushrooms_shape.npy')
    write_tsp('mushrooms.tsp', points)
    run_linkern('mushrooms.tsp', 'mushrooms.cyc', '../../tools/linkern.exe')
    postprocess_cyc('mushrooms_shape.npy', 'mushrooms.cyc',
                    'mushrooms_processed.npy', (width, height), radius=110/128, segment_length=4)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    color = np.array([1,1,1])

    progress = t / duration
    p = interval_progresses(progress, 2, 'none')

    points = np.load('mushrooms_processed.npy')[:,:] + np.array([30, 0])

    n_waves = 30
    for i in range(len(points)):
        segment_color = color * (0.67 + 0.33 * np.sin(2*np.pi*(n_waves*i / len(points) + progress)))
        gz.polyline(points=(points[i,:], points[(i+1) % len(points),:]),
                    stroke=segment_color, stroke_width=3, line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # stipple_image()
    # solve_tsp()

    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
