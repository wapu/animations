import numpy as np
import gizeh as gz
from scipy.spatial import distance_matrix

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from tsp import *
from xr import *


name = 'xr_tsp_snake'
width, height = 768, 768
duration = 20


def prepare_data():
    surface = gz.Surface(1000,1000)
    offset = np.array((500, 500))
    gz.square(l=1000, xy=offset, fill=(0,0,0)).draw(surface)

    radius, corners, stroke_width = get_extinction_symbol_params(400)
    gz.circle(r=radius, xy=offset, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    gz.polyline(points=corners + offset, close_path=True, fill=None, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    surface.write_to_png('extinction_symbol.png')

    print('STIPPLING EXTINCTION SYMBOL')
    points = stipple_image_points('extinction_symbol.png',
                                  n_points=2500, scale_factor=1, max_iterations=50)
    np.save('extinction_symbol', points)

    points = np.load('extinction_symbol.npy')
    write_tsp('extinction_symbol.tsp', points)
    run_linkern('extinction_symbol.tsp', 'extinction_symbol.cyc', '../../tools/linkern.exe')
    postprocess_cyc('extinction_symbol.npy', 'extinction_symbol.cyc',
                    'extinction_symbol_processed.npy', (width, height), radius=110/128, segment_length=5)


points = np.load('extinction_symbol_processed.npy')

# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    head = int(round(len(points) * progress))
    tail_length = len(points)

    for i in range(len(points)):
        i_ = i if (i < head) else (i - len(points))
        segment_color =  np.ones(3) * (1 - .75 * min(1, (head - i_) / tail_length)**.5)
        gz.polyline(points=(points[i,:], points[(i+1) % len(points),:]),
                    stroke=segment_color, stroke_width=4, line_cap='round').draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
