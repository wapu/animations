import numpy as np
from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'modulus_gaussian_mix'
width, height = 768, 768
duration = 7


coords = np.mgrid[:2*width,:2*height].transpose([1,2,0])
centers = get_circle_coordinates(6, 315, (width, height))
squared_dists = [np.sum(np.square(coords - center), axis=2) for center in centers]
mask = get_circle_mask(width, height, 360)


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 3, 'hermite')

    sigma = (120 - 60 * (p[1] - p[2]))

    I = np.sum([np.exp(-squared_dist / (2 * sigma**2)) for squared_dist in squared_dists], axis=0)
    I *= (1.25 + (1 + p[0] - p[1])*(p[0] - p[2]))
    I = np.mod(I, 1.0)

    I = resize(I, (width, height))
    I *= mask

    I = np.tile(I[:,:,None], (1,1,3))

    return I * 255


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
