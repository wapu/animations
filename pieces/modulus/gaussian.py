import numpy as np
from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = 'modulus_gaussian'
width, height = 768, 768
duration = 7


# Render frame at time t
def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 2, 'hermite')

    center = (width, height)
    outer_radius = 300
    sigma = 255

    coords = np.mgrid[0:2*width, 0:2*height].transpose([1,2,0])
    I = np.exp(-np.sum(np.square(coords - center), axis=2) / (2*sigma*sigma))
    I *= (1.25 + 7*(p[0] - p[1]))
    I = np.mod(I, 1.0)

    I = resize(I, (width, height))
    clip_to_circle(I, r=outer_radius)

    I = np.tile(I[:,:,None], (1,1,3))

    return I * 255


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    # render_webm(name, make_frame, duration, webm_params)
    # convert_to_mp4(name, mp4_params)
