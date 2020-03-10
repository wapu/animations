import numpy as np
import gizeh as gz
from scipy.spatial import distance_matrix

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *
from xr import *


name = 'xr_dist_lines'
width, height = 768, 768
duration = 15
max_dist = 50
n_floaters = 300

webm_params = {
    '-speed': '0',
    '-b:v': '10000k',
    '-minrate': '500k',
    '-maxrate': '20000k',
    '-crf': '0',
}

mp4_params = {
    '-b:v': '10000k',
    '-minrate': '500k',
    '-maxrate': '20000k',
}


def prepare_data():
    surface = gz.Surface(2000,2000)
    offset = np.array((1000, 1000))
    gz.square(l=2000, xy=offset, fill=(0,0,0)).draw(surface)

    radius, corners, stroke_width = get_extinction_symbol_params(800)
    gz.circle(r=radius, xy=offset, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    gz.polyline(points=corners + offset, close_path=True, fill=None, stroke=(1,1,1), stroke_width=stroke_width).draw(surface)
    surface.write_to_png('extinction_symbol.png')

    print('STIPPLING EXTINCTION SYMBOL')
    points = stipple_image_points('extinction_symbol.png',
                                  n_points=500, scale_factor=1, max_iterations=100)
    np.save('extinction_symbol', points)


amplitudes = 5 + 10 * np.random.rand(n_floaters)
periods = 50 + 50 * np.random.rand(n_floaters)
x_shifts = 50 + (width - 100) * np.random.rand(n_floaters)
repetitions = np.random.choice([1,2,3], n_floaters)
progresses = np.random.rand(n_floaters)

symbol = np.load('extinction_symbol.npy') * (height/2000)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)
    progress = t / duration

    t_floaters = (progress*repetitions + progresses)%1.0
    floaters = np.stack([x_shifts + amplitudes * np.sin(2*np.pi * t_floaters * (height/periods)), 50 + (width - 100) * (1 - t_floaters)]).T
    d_center = np.sum(np.square(floaters - np.array([width/2, height/2])), axis=1) - (width/2)**2

    points = np.concatenate([symbol, floaters[d_center < 0,:]])

    d = distance_matrix(symbol, floaters)
    for i in range(len(symbol)):
        for j in range(len(floaters)):
            if d[i,j] <= max_dist:
                alpha = (1 - d[i,j]/max_dist)**2
                gz.polyline(points=[points[i,:], floaters[j,:]], stroke=(1,1,1,alpha), stroke_width=1).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame, type='png')
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
