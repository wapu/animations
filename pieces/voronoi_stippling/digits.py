import numpy as np

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from stippling import *


name = 'digits'
width, height = 768, 768
duration = 10


def prepare_data():
    for i in range(10):
        print('CREATING KEYFRAME', i)
        points = stipple_image_points(f'digits/{i}.png',
                                      n_points=300, scale_factor=1, max_iterations=100)
        np.save(f'digits/{i}', points)


# Render frame at time t
def make_frame(t):
    surface = gz.Surface(width, height)

    image_paths = [f'digits/{9-j}.npy' for j in range(10)]
    image_paths.append(image_paths[0])
    coords = [np.load(path) * (height/1500) for path in image_paths]

    progress = t / duration
    weights = equidistant_weight_functions(progress, len(coords), 'hermite')
    max_dist = 36

    points = np.zeros(coords[0].shape)
    for i in range(len(coords[0])):
        points[i,:] = sum([weights[j] * coords[j][i,:] for j in range(len(coords))])

    for i in range(len(points)):
        for j in range(i+1, len(points)):
            p1, p2 = points[i,:], points[j,:]
            dd = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
            if dd <= (max_dist*max_dist):
                d = np.sqrt(dd)
                gz.polyline(points=[p1, p2], stroke=(1,1,1,1-d/max_dist), stroke_width=1).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    # prepare_data()
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
