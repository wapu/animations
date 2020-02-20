import numpy as np
import gizeh as gz

from skimage.transform import resize

import sys
sys.path.insert(0, '../../tools')
from rendering import *
from geometry import *


name = '2d_fft_rotating_star'
width, height = 768, 768
duration = 6


def make_frame(t):
    progress = t / duration
    p = interval_progresses(progress, 2, 'hermite')
    center = (width/2, height/2)

    # star
    surface = gz.Surface(2*width, 2*height)
    n_lines = 24

    length = 30 + 5*(p[0] - p[1])
    C = get_circle_coordinates(n_lines, length, center)
    rotate_around(C, -2*np.pi * progress/n_lines, center)

    for i in range(n_lines):
        gz.polyline(points=[center, C[i,:]], stroke=(1,1,1), stroke_width=2).draw(surface)

    # FFT
    I = np.fft.fft2(surface.get_npimage()[:,:,0]/255)
    I = np.abs(I).astype(np.float32)
    I -= 1
    I = 1 - np.minimum(1, np.maximum(0, I))
    I = resize(I, (width, height))

    # border
    radius = 300
    I *= get_circle_mask(width, height, radius)
    I = np.tile(I[:,:,np.newaxis], (1,1,4)) * 255
    surface = gz.Surface.from_image(I.astype(np.uint8))
    gz.circle(xy=(width/2, height/2), r=radius, stroke=(1,1,1), stroke_width=3).draw(surface)

    return surface.get_npimage()


# Render animation
if __name__ == '__main__':
    save_poster(name, make_frame)
    render_webm(name, make_frame, duration, webm_params)
    convert_to_mp4(name, mp4_params)
